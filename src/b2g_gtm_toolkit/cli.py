from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

import os

from b2g_gtm_toolkit.models.business import BusinessProfile
from b2g_gtm_toolkit.models.gtm import TargetAccountList
from b2g_gtm_toolkit.models.secop import SecopNormalizedRecord, SecopResearchInput
from b2g_gtm_toolkit.secop.research import default_offline_fixtures, run_research
from b2g_gtm_toolkit.notion.schema import DEFAULT_MANIFEST, manifest_for
from b2g_gtm_toolkit.notion.verify import plan_setup, verify_workspace
from b2g_gtm_toolkit.notion.write import dedupe_filter_for_secop, secop_record_properties

app = typer.Typer(help="B2G GTM Toolkit CLI")

notion_app = typer.Typer(help="Comandos de Notion")
secop_app = typer.Typer(help="Comandos de investigacion SECOP")
output_app = typer.Typer(help="Comandos de generacion de salidas")
validate_app = typer.Typer(help="Comandos de validacion de artefactos GTM")

app.add_typer(notion_app, name="notion")
app.add_typer(secop_app, name="secop")
app.add_typer(output_app, name="output")
app.add_typer(validate_app, name="validate")


@app.command()
def init() -> None:
    typer.echo("TODO: init")
    raise typer.Exit(code=0)


class _StubNotionClient:
    """Cliente stub usado cuando no hay NOTION_TOKEN."""

    def search_databases(self, query: str):
        return []

    def retrieve_database(self, database_id: str):
        return None

    def query_database(self, database_id: str, filter):
        return []

    def create_page(self, database_id: str, properties):
        return {"id": None}

    def update_page(self, page_id: str, properties):
        return {"id": page_id}


def _build_notion_client():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        return _StubNotionClient(), False
    try:
        from notion_client import Client  # type: ignore

        real = Client(auth=token)

        class _RealAdapter:
            def __init__(self, c):
                self._c = c

            def search_databases(self, query: str):
                res = self._c.search(query=query, filter={"value": "database", "property": "object"})
                return res.get("results", [])

            def retrieve_database(self, database_id: str):
                return self._c.databases.retrieve(database_id=database_id)

            def query_database(self, database_id: str, filter):
                return self._c.databases.query(database_id=database_id, filter=filter).get("results", [])

            def create_page(self, database_id: str, properties):
                return self._c.pages.create(parent={"database_id": database_id}, properties=properties)

            def update_page(self, page_id: str, properties):
                return self._c.pages.update(page_id=page_id, properties=properties)

        return _RealAdapter(real), True
    except Exception as exc:
        typer.echo(f"Aviso: no se pudo inicializar notion-client ({exc}); usando stub.", err=True)
        return _StubNotionClient(), False


def _known_database_ids() -> dict:
    out = {}
    for db in DEFAULT_MANIFEST.databases:
        env_key = "NOTION_DB_" + db.name.upper().replace(" ", "_")
        val = os.environ.get(env_key)
        if val:
            out[db.name] = val
    return out


@notion_app.command("verify")
def notion_verify() -> None:
    """Verifica que el workspace de Notion contenga las bases requeridas."""
    client, real = _build_notion_client()
    if not real:
        typer.echo("NOTION_TOKEN no definido: verificando contra cliente stub (workspace vacio).")
    manifest = manifest_for(None)
    report = verify_workspace(manifest, client, _known_database_ids())
    typer.echo("Reporte de verificacion de Notion:")
    typer.echo(report.summary())
    if report.ok:
        typer.echo("Estado: OK")
        raise typer.Exit(code=0)
    typer.echo("Estado: faltan elementos. Ejecuta 'b2g-gtm notion setup --dry-run' para ver el plan.")
    raise typer.Exit(code=1)


@notion_app.command("setup")
def notion_setup(
    dry_run: bool = typer.Option(False, "--dry-run", help="Mostrar el plan sin aplicar cambios."),
    apply: bool = typer.Option(False, "--apply", help="(no implementado en V1)"),
) -> None:
    """Planifica la creacion/actualizacion del workspace de Notion."""
    if apply:
        typer.echo("--apply no implementado en V1; ejecutá --dry-run", err=True)
        raise typer.Exit(code=2)
    if not dry_run:
        typer.echo("Indica --dry-run para previsualizar el plan.", err=True)
        raise typer.Exit(code=2)
    client, _real = _build_notion_client()
    manifest = manifest_for(None)
    report = verify_workspace(manifest, client, _known_database_ids())
    plan = plan_setup(manifest, report)
    typer.echo("Plan de setup (dry-run):")
    typer.echo(plan.summary())
    if plan.is_empty():
        typer.echo("Workspace ya cumple el manifiesto.")
    raise typer.Exit(code=0)


@notion_app.command("sync")
def notion_sync(
    run: str = typer.Option(..., "--run", help="ID de la corrida (carpeta dentro de data/runs)."),
    apply: bool = typer.Option(False, "--apply", help="Escribir realmente en Notion (requiere NOTION_TOKEN)."),
) -> None:
    """Mapea una corrida SECOP a payloads de Notion. Default: dry-run."""
    run_path = Path("data/runs") / run / "secop-research.jsonl"
    if not run_path.exists():
        typer.echo(f"Archivo no encontrado: {run_path}", err=True)
        raise typer.Exit(code=2)

    records = []
    for idx, line in enumerate(run_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            prov = data.get("provenance") or {}
            if data.get("source_dataset") and not prov.get("source_dataset"):
                prov["source_dataset"] = data["source_dataset"]
                data["provenance"] = prov
            records.append(SecopNormalizedRecord.model_validate(data))
        except (json.JSONDecodeError, ValidationError) as exc:
            typer.echo(f"Linea {idx} invalida: {exc}", err=True)
            raise typer.Exit(code=1)

    typer.echo(f"Registros cargados: {len(records)}")
    target_db = "B2G SECOP Research"
    payloads = []
    for rec in records:
        props = secop_record_properties(rec)
        dedupe = dedupe_filter_for_secop(rec)
        payloads.append((rec.source_record_id, props, dedupe))

    if not apply:
        typer.echo("Modo dry-run. Escrituras planeadas:")
        for src_id, _props, _dedupe in payloads:
            typer.echo(f"  upsert en '{target_db}' por Source Record ID={src_id}")
        typer.echo(f"Total: {len(payloads)} upserts. Usa --apply para escribir.")
        raise typer.Exit(code=0)

    if not os.environ.get("NOTION_TOKEN"):
        typer.echo("--apply requiere NOTION_TOKEN en el entorno.", err=True)
        raise typer.Exit(code=2)

    typer.echo("Escritura real no implementada en V1; usa el modo dry-run.", err=True)
    raise typer.Exit(code=2)


@secop_app.command("research")
def secop_research(
    input: str = typer.Option(..., "--input", help="Ruta al archivo JSON de entrada de investigacion SECOP."),
    offline: bool = typer.Option(False, "--offline", help="Usar fixtures locales en lugar de la API real."),
    output_root: Path = typer.Option(Path("data/runs"), "--output-root", help="Carpeta raiz para las ejecuciones."),
    fixtures_dir: Path = typer.Option(Path("tests/fixtures/secop"), "--fixtures-dir", help="Directorio de fixtures cuando se usa --offline."),
) -> None:
    """Ejecuta una investigacion SECOP con la entrada provista y escribe JSONL normalizado."""
    input_path = Path(input)
    if not input_path.exists():
        typer.echo(f"Archivo de entrada no encontrado: {input_path}", err=True)
        raise typer.Exit(code=2)

    try:
        raw = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        typer.echo(f"JSON invalido en {input_path}: {exc}", err=True)
        raise typer.Exit(code=2)

    try:
        input_data = SecopResearchInput.model_validate(raw)
    except ValidationError as exc:
        typer.echo("Entrada SECOP invalida:", err=True)
        for error in exc.errors():
            loc = ".".join(str(part) for part in error["loc"])
            typer.echo(f"  - {loc}: {error['msg']}", err=True)
        raise typer.Exit(code=1)

    offline_fixtures = default_offline_fixtures(fixtures_dir) if offline else None

    run = run_research(
        input_data,
        output_root=output_root,
        offline_fixtures=offline_fixtures,
    )

    typer.echo("OK: investigacion SECOP completada")
    typer.echo(f"  run_id: {run.run_id}")
    typer.echo(f"  datasets: {', '.join(run.datasets)}")
    typer.echo(f"  registros raw: {run.raw_count}")
    typer.echo(f"  registros deduplicados: {run.deduped_count}")
    typer.echo(f"  jsonl: {run.jsonl_path}")
    typer.echo(f"  manifest: {run.manifest_path}")
    raise typer.Exit(code=0)


_OUTPUT_TYPE_MAP = {
    "outreach": ("outreach.md", "build_outreach_context"),
    "meeting-prep": ("meeting-prep.md", "build_meeting_prep_context"),
    "proposal": ("proposal-brief.md", "build_proposal_context"),
}


@output_app.command("create")
def output_create(
    type: str = typer.Option(..., "--type", help="Tipo de salida: outreach | meeting-prep | proposal."),
    source: str = typer.Option(..., "--source", help="Ruta a JSON con {opportunity, account, research}."),
    out: Path = typer.Option(None, "--out", help="Ruta opcional para escribir el markdown; si se omite, imprime a stdout."),
) -> None:
    """Genera entregables AE (outreach, meeting-prep, proposal) a partir de una oportunidad investigada."""
    if type not in _OUTPUT_TYPE_MAP:
        typer.echo(
            f"Tipo invalido '{type}'. Opciones: {', '.join(_OUTPUT_TYPE_MAP.keys())}.", err=True
        )
        raise typer.Exit(code=2)

    source_path = Path(source)
    if not source_path.exists():
        typer.echo(f"Archivo de entrada no encontrado: {source_path}", err=True)
        raise typer.Exit(code=2)

    try:
        data = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        typer.echo(f"JSON invalido en {source_path}: {exc}", err=True)
        raise typer.Exit(code=2)

    opportunity = data.get("opportunity") or {}
    account = data.get("account") or {}
    research = data.get("research") or []

    from b2g_gtm_toolkit.outputs import (
        build_meeting_prep_context,
        build_outreach_context,
        build_proposal_context,
    )
    from b2g_gtm_toolkit.outputs.render import render

    builders = {
        "outreach": build_outreach_context,
        "meeting-prep": build_meeting_prep_context,
        "proposal": build_proposal_context,
    }

    template_name, _ = _OUTPUT_TYPE_MAP[type]
    context = builders[type](opportunity, account, research)
    markdown = render(template_name, context)

    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
        typer.echo(f"OK: salida escrita en {out}")
    else:
        typer.echo(markdown)
    raise typer.Exit(code=0)


@validate_app.command("business-profile")
def validate_business_profile(
    path: Path = typer.Argument(..., exists=False, help="Ruta al archivo JSON con el business profile."),
) -> None:
    """Valida un business profile JSON contra el modelo BusinessProfile."""
    if not path.exists():
        typer.echo(f"Archivo no encontrado: {path}", err=True)
        raise typer.Exit(code=2)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        typer.echo(f"JSON invalido en {path}: {exc}", err=True)
        raise typer.Exit(code=2)

    try:
        profile = BusinessProfile.model_validate(raw)
    except ValidationError as exc:
        typer.echo("Validacion fallida:", err=True)
        for error in exc.errors():
            loc = ".".join(str(part) for part in error["loc"])
            typer.echo(f"  - {loc}: {error['msg']}", err=True)
        raise typer.Exit(code=1)

    typer.echo("OK: business profile valido")
    typer.echo(f"  nombre: {profile.name}")
    typer.echo(f"  etapa: {profile.company_stage.value}")
    typer.echo(f"  productos/servicios: {len(profile.products_services)}")
    typer.echo(f"  clientes actuales: {len(profile.current_customers)}")
    typer.echo(f"  Tier A: {len(profile.best_customers)}")
    typer.echo(f"  Tier C: {len(profile.poor_fit_customers)}")
    typer.echo(f"  regiones: {', '.join(profile.regions_served) or '(ninguna)'}")
    raise typer.Exit(code=0)


@validate_app.command("target-accounts")
def validate_target_accounts(
    path: Path = typer.Argument(..., exists=False, help="Ruta al archivo JSON con la lista de target accounts."),
) -> None:
    """Valida una lista de target accounts JSON contra el modelo TargetAccountList."""
    if not path.exists():
        typer.echo(f"Archivo no encontrado: {path}", err=True)
        raise typer.Exit(code=2)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        typer.echo(f"JSON invalido en {path}: {exc}", err=True)
        raise typer.Exit(code=2)

    try:
        account_list = TargetAccountList.model_validate(raw)
    except ValidationError as exc:
        typer.echo("Validacion fallida:", err=True)
        for error in exc.errors():
            loc = ".".join(str(part) for part in error["loc"])
            typer.echo(f"  - {loc}: {error['msg']}", err=True)
        raise typer.Exit(code=1)

    typer.echo("OK: lista de target accounts valida")
    typer.echo(f"  ICP de referencia: {account_list.icp_id or '(no especificado)'}")
    typer.echo(f"  fuente: {account_list.source or '(no especificada)'}")
    typer.echo(f"  total de cuentas: {len(account_list.accounts)}")

    ranked = sorted(
        account_list.accounts,
        key=lambda a: (a.fit_score is not None, a.fit_score or 0.0),
        reverse=True,
    )
    top = ranked[:3]
    typer.echo("  top 3 por fit_score:")
    if not top:
        typer.echo("    (sin cuentas)")
    for idx, account in enumerate(top, start=1):
        score = f"{account.fit_score:.0f}" if account.fit_score is not None else "s/d"
        location = account.location or account.municipality or account.department or "s/d"
        typer.echo(f"    {idx}. {account.name} — {account.entity_type or 's/d'} ({location}) — fit {score}")
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
