from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from dotenv import load_dotenv
from pydantic import ValidationError

import os

from b2g_gtm_toolkit.models.business import BusinessProfile, ICP
from b2g_gtm_toolkit.models.gtm import GtmOutput, GtmOutputType, TargetAccountList
from b2g_gtm_toolkit.models.notion import (
    NotionDatabaseSpec,
    NotionPropertySpec,
    NotionWorkspaceManifest,
)
from b2g_gtm_toolkit.models.secop import SecopNormalizedRecord, SecopResearchInput
from b2g_gtm_toolkit.secop.research import default_offline_fixtures, run_research
from b2g_gtm_toolkit.notion.schema import DEFAULT_MANIFEST, manifest_for
from b2g_gtm_toolkit.notion.verify import plan_setup, verify_workspace
from b2g_gtm_toolkit.notion.read import resolve_opportunity_input, resolve_target_account_input
from b2g_gtm_toolkit.notion.write import (
    _looks_like_notion_page_id,
    dedupe_filter_for_secop,
    import_workflow_to_notion,
    secop_record_properties,
    sync_secop_research_to_notion,
    upsert_gtm_output,
    upsert_page,
)

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

    def retrieve_page(self, page_id: str):
        return {"id": page_id, "properties": {}}

    def create_page(self, database_id: str, properties, children=None):
        return {"id": None}

    def update_page(self, page_id: str, properties):
        return {"id": page_id}

    def append_page_children(self, page_id: str, children):
        return {"id": page_id, "children": children}


def _load_cli_env(dotenv_path: Optional[Path] = None) -> bool:
    """Load local CLI configuration without overwriting exported values."""
    return load_dotenv(dotenv_path=dotenv_path or (Path.cwd() / ".env"), override=False)


def _build_notion_client():
    _load_cli_env()
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        return _StubNotionClient(), False
    try:
        from notion_client import Client  # type: ignore

        real = Client(auth=token)

        class _RealAdapter:
            def __init__(self, c):
                self._c = c

            def _data_source_id(self, database_id: str) -> str:
                db = self._c.databases.retrieve(database_id=database_id)
                sources = db.get("data_sources") or []
                if sources:
                    return sources[0]["id"]
                return database_id

            def search_databases(self, query: str):
                res = self._c.search(query=query, filter={"value": "database", "property": "object"})
                return [self.retrieve_database(item["id"]) for item in res.get("results", [])]

            def retrieve_database(self, database_id: str):
                try:
                    return self._c.data_sources.retrieve(data_source_id=database_id)
                except Exception:
                    pass
                db = self._c.databases.retrieve(database_id=database_id)
                sources = db.get("data_sources") or []
                if not sources:
                    return db
                source = self._c.data_sources.retrieve(data_source_id=sources[0]["id"])
                source["database_id"] = db.get("id")
                return source

            def query_database(self, database_id: str, filter):
                return self._c.data_sources.query(data_source_id=database_id, filter=filter).get("results", [])

            def retrieve_page(self, page_id: str):
                return self._c.pages.retrieve(page_id=page_id)

            def create_page(self, database_id: str, properties, children=None):
                kwargs = {"parent": {"data_source_id": database_id}, "properties": properties}
                if children:
                    kwargs["children"] = children
                return self._c.pages.create(**kwargs)

            def update_page(self, page_id: str, properties):
                return self._c.pages.update(page_id=page_id, properties=properties)

            def append_page_children(self, page_id: str, children):
                return self._c.blocks.children.append(block_id=page_id, children=children)

            def create_database(self, parent_page_id: str, title: str, properties):
                db = self._c.databases.create(
                    parent={"type": "page_id", "page_id": parent_page_id},
                    title=[{"type": "text", "text": {"content": title}}],
                )
                data_source_id = db["data_sources"][0]["id"]
                if properties:
                    return self.update_database(data_source_id, properties)
                return self._c.data_sources.retrieve(data_source_id=data_source_id)

            def update_database(self, database_id: str, properties):
                return self._c.data_sources.update(data_source_id=database_id, properties=properties)

        return _RealAdapter(real), True
    except Exception as exc:
        typer.echo(f"Aviso: no se pudo inicializar notion-client ({exc}); usando stub.", err=True)
        return _StubNotionClient(), False


def _known_database_ids() -> dict:
    _load_cli_env()
    out = {}
    for db in DEFAULT_MANIFEST.databases:
        env_key = "NOTION_DB_" + db.name.upper().replace(" ", "_")
        val = os.environ.get(env_key)
        if val:
            out[db.name] = val
    return out


def _all_database_ids_known(
    manifest: NotionWorkspaceManifest,
    known_database_ids: Dict[str, str],
) -> bool:
    return all(db.name in known_database_ids for db in manifest.databases)


def _manifest_with_database(
    manifest: NotionWorkspaceManifest,
    database_name: str,
) -> NotionWorkspaceManifest:
    return NotionWorkspaceManifest(
        version=manifest.version,
        databases=[db for db in manifest.databases if db.name == database_name],
    )


def _manifest_with_databases(
    manifest: NotionWorkspaceManifest,
    database_names: list[str],
) -> NotionWorkspaceManifest:
    wanted = set(database_names)
    return NotionWorkspaceManifest(
        version=manifest.version,
        databases=[db for db in manifest.databases if db.name in wanted],
    )


def _read_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        typer.echo(f"Archivo no encontrado: {path}", err=True)
        raise typer.Exit(code=2)
    except json.JSONDecodeError as exc:
        typer.echo(f"JSON invalido en {path}: {exc}", err=True)
        raise typer.Exit(code=2)


def _load_secop_records(path: Path) -> list[SecopNormalizedRecord]:
    records: list[SecopNormalizedRecord] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
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
            typer.echo(f"Linea {idx} invalida en {path}: {exc}", err=True)
            raise typer.Exit(code=1)
    return records


def _resolve_secop_run_path(run: Path) -> Path:
    if run.is_file():
        return run
    if run.is_dir():
        candidate = run / "secop-research.jsonl"
        if candidate.exists():
            return candidate
    candidate = Path("data/runs") / str(run) / "secop-research.jsonl"
    if candidate.exists():
        return candidate
    typer.echo(f"Archivo SECOP no encontrado para --run: {run}", err=True)
    raise typer.Exit(code=2)


def _database_ids_for_names(database_names: list[str], client) -> Dict[str, str]:
    manifest = manifest_for(None)
    target_manifest = _manifest_with_databases(manifest, database_names)
    known_ids = _known_database_ids()
    report = verify_workspace(
        target_manifest,
        client,
        known_ids,
        allow_search_fallback=any(name not in known_ids for name in database_names),
    )
    database_ids = {db.name: db.database_id for db in report.databases if db.found and db.database_id}
    missing = [name for name in database_names if name not in database_ids]
    if missing:
        typer.echo(
            "No encontre las bases requeridas: "
            + ", ".join(missing)
            + ". Ejecuta primero 'b2g-gtm notion setup --apply'.",
            err=True,
        )
        raise typer.Exit(code=2)
    return database_ids


def _notion_property_schema(prop: NotionPropertySpec, database_ids: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    if prop.type.value == "select":
        return {"select": {"options": [{"name": option} for option in prop.options]}}
    if prop.type.value == "multi_select":
        return {"multi_select": {"options": [{"name": option} for option in prop.options]}}
    if prop.type.value == "relation":
        target_id = (database_ids or {}).get(prop.relation_database or "")
        if not target_id:
            raise ValueError(f"relation target not available for {prop.name}: {prop.relation_database}")
        return {"relation": {"data_source_id": target_id, "type": "single_property", "single_property": {}}}
    return {prop.type.value: {}}


def _database_properties_for_create(db: NotionDatabaseSpec) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}
    for prop in db.properties:
        if prop.type.value == "relation":
            continue
        if prop.type.value == "title":
            properties["Name"] = {"name": prop.name, "title": {}}
            continue
        properties[prop.name] = _notion_property_schema(prop)
    return properties


def _missing_property_specs(db: NotionDatabaseSpec, missing_names: list[str]) -> list[NotionPropertySpec]:
    missing = set(missing_names)
    return [prop for prop in db.properties if prop.name in missing]


def _apply_database_setup(manifest, report, client, parent_page_id: str) -> Dict[str, str]:
    database_ids = {status.name: status.database_id for status in report.databases if status.found and status.database_id}
    state_by_name = {status.name: status for status in report.databases}
    spec_by_name = {db.name: db for db in manifest.databases}

    for db in manifest.databases:
        if db.name in database_ids:
            continue
        created = client.create_database(parent_page_id, db.name, _database_properties_for_create(db))
        database_ids[db.name] = created["id"]
        typer.echo(f"Creada: {db.name} ({created['id']})")

    for db in manifest.databases:
        status = state_by_name.get(db.name)
        missing_names = list(status.missing_properties) if status and status.found else [
            prop.name for prop in db.properties if prop.type.value == "relation"
        ]
        relation_issues = [issue.property for issue in (status.missing_relations if status else [])]
        missing_names.extend(name for name in relation_issues if name not in missing_names)
        props_to_add = _missing_property_specs(db, missing_names)
        if not props_to_add:
            continue
        properties = {}
        for prop in props_to_add:
            if prop.type.value == "title":
                properties["Name"] = {"name": prop.name, "title": {}}
            else:
                properties[prop.name] = _notion_property_schema(prop, database_ids)
        client.update_database(database_ids[db.name], properties)
        typer.echo(f"Actualizada: {db.name} (+{len(properties)} propiedades)")

    return database_ids


@notion_app.command("verify")
def notion_verify() -> None:
    """Verifica que el workspace de Notion contenga las bases requeridas."""
    client, real = _build_notion_client()
    if not real:
        typer.echo("NOTION_TOKEN no definido: verificando contra cliente stub (workspace vacio).")
    manifest = manifest_for(None)
    known_ids = _known_database_ids()
    allow_search_fallback = not (real and _all_database_ids_known(manifest, known_ids))
    if real and not allow_search_fallback:
        typer.echo("Usando IDs configurados de Notion; no se hara busqueda amplia.")
    report = verify_workspace(
        manifest,
        client,
        known_ids,
        allow_search_fallback=allow_search_fallback,
    )
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
    apply: bool = typer.Option(False, "--apply", help="Crear/actualizar bases de datos en Notion."),
) -> None:
    """Planifica la creacion/actualizacion del workspace de Notion."""
    if not dry_run and not apply:
        typer.echo("Indica --dry-run para previsualizar o --apply para aplicar.", err=True)
        raise typer.Exit(code=2)
    client, _real = _build_notion_client()
    manifest = manifest_for(None)
    known_ids = _known_database_ids()
    report = verify_workspace(
        manifest,
        client,
        known_ids,
        allow_search_fallback=not _all_database_ids_known(manifest, known_ids),
    )
    plan = plan_setup(manifest, report)
    typer.echo("Plan de setup (dry-run):")
    typer.echo(plan.summary())
    if plan.is_empty():
        typer.echo("Workspace ya cumple el manifiesto.")
        raise typer.Exit(code=0)
    if not apply:
        raise typer.Exit(code=0)

    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not os.environ.get("NOTION_TOKEN") or not parent_page_id:
        typer.echo("--apply requiere NOTION_TOKEN y NOTION_PARENT_PAGE_ID en el entorno.", err=True)
        raise typer.Exit(code=2)
    if dry_run:
        typer.echo("Aplicando despues de mostrar el plan porque tambien se indico --apply.")
    database_ids = _apply_database_setup(manifest, report, client, parent_page_id)
    typer.echo("Setup aplicado. IDs de bases creadas/encontradas:")
    for name, database_id in database_ids.items():
        env_key = "NOTION_DB_" + name.upper().replace(" ", "_")
        typer.echo(f"  {env_key}={database_id}")
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

    _load_cli_env()
    if not os.environ.get("NOTION_TOKEN"):
        typer.echo("--apply requiere NOTION_TOKEN en el entorno.", err=True)
        raise typer.Exit(code=2)

    client, real = _build_notion_client()
    if not real:
        typer.echo("No se pudo inicializar el cliente real de Notion.", err=True)
        raise typer.Exit(code=2)
    manifest = manifest_for(None)
    target_manifest = _manifest_with_database(manifest, target_db)
    known_ids = _known_database_ids()
    report = verify_workspace(
        target_manifest,
        client,
        known_ids,
        allow_search_fallback=target_db not in known_ids,
    )
    target_status = next((db for db in report.databases if db.name == target_db and db.found), None)
    if not target_status or not target_status.database_id:
        typer.echo(f"No encontre la base '{target_db}'. Ejecuta primero 'b2g-gtm notion setup --apply'.", err=True)
        raise typer.Exit(code=2)

    results = []
    for _src_id, props, dedupe in payloads:
        results.append(upsert_page(target_status.database_id, props, dedupe, client))
    created = sum(1 for result in results if result.action == "create")
    updated = sum(1 for result in results if result.action == "update")
    typer.echo(f"Sync aplicado: {created} creados, {updated} actualizados.")
    raise typer.Exit(code=0)


@notion_app.command("import-workflow")
def notion_import_workflow(
    business_profile: Path = typer.Option(..., "--business-profile", help="Ruta al business-profile.json."),
    icp: Path = typer.Option(..., "--icp", help="Ruta al icp.json."),
    target_accounts: Path = typer.Option(..., "--target-accounts", help="Ruta al target-accounts.json."),
    run: Path = typer.Option(..., "--run", help="Ruta a secop-research.jsonl, carpeta de corrida, o ID de corrida."),
    apply: bool = typer.Option(False, "--apply", help="Escribir realmente en Notion (por defecto solo previsualiza)."),
) -> None:
    """Importa un workflow local completo a Notion. Default: preview sin escrituras."""
    try:
        profile = BusinessProfile.model_validate(_read_json_file(business_profile))
        icp_model = ICP.model_validate(_read_json_file(icp))
        account_list = TargetAccountList.model_validate(_read_json_file(target_accounts))
    except ValidationError as exc:
        typer.echo("Validacion fallida:", err=True)
        for error in exc.errors():
            loc = ".".join(str(part) for part in error["loc"])
            typer.echo(f"  - {loc}: {error['msg']}", err=True)
        raise typer.Exit(code=1)

    run_path = _resolve_secop_run_path(run)
    records = _load_secop_records(run_path)

    required_dbs = [
        "B2G Business Profiles",
        "B2G ICPs",
        "B2G Target Accounts",
        "B2G SECOP Research",
    ]
    database_ids = {name: name for name in required_dbs}
    client = None

    if apply:
        _load_cli_env()
        if not os.environ.get("NOTION_TOKEN"):
            typer.echo("--apply requiere NOTION_TOKEN en el entorno.", err=True)
            raise typer.Exit(code=2)
        client, real = _build_notion_client()
        if not real:
            typer.echo("No se pudo inicializar el cliente real de Notion.", err=True)
            raise typer.Exit(code=2)
        database_ids = _database_ids_for_names(required_dbs, client)

    result = import_workflow_to_notion(
        business_profile=profile,
        icp=icp_model,
        target_accounts=account_list.accounts,
        secop_records=records,
        database_ids=database_ids,
        client=client,
    )

    all_results = [result.business_profile, result.icp, *result.target_accounts, *result.secop_records]
    created = sum(1 for item in all_results if item.action in {"create", "dry_run_create"})
    updated = sum(1 for item in all_results if item.action in {"update", "dry_run_update"})

    if not apply:
        typer.echo("Modo preview. Nada fue escrito en Notion.")
    typer.echo(
        f"Workflow procesado: 1 business profile, 1 ICP, {len(result.target_accounts)} target accounts, "
        f"{len(result.secop_records)} registros SECOP."
    )
    typer.echo(f"Acciones: {created} creaciones planeadas/aplicadas, {updated} actualizaciones.")
    typer.echo(f"Relaciones SECOP -> Target Account: {result.matched_secop_records}.")
    if result.augmented_target_account_nits:
        typer.echo(f"NIT inferidos para target accounts durante el import: {result.augmented_target_account_nits}.")
    if not apply:
        typer.echo("Usa --apply para escribir estos cambios en Notion.")
    raise typer.Exit(code=0)


@secop_app.command("research")
def secop_research(
    input: str = typer.Option(..., "--input", help="Ruta al archivo JSON de entrada de investigacion SECOP."),
    offline: bool = typer.Option(False, "--offline", help="Usar fixtures locales en lugar de la API real."),
    output_root: Path = typer.Option(Path("data/runs"), "--output-root", help="Carpeta raiz para las ejecuciones."),
    fixtures_dir: Path = typer.Option(Path("tests/fixtures/secop"), "--fixtures-dir", help="Directorio de fixtures cuando se usa --offline."),
    to_notion: bool = typer.Option(False, "--to-notion", help="Preparar sync de resultados a Notion."),
    apply: bool = typer.Option(False, "--apply", help="Escribir en Notion. Requiere --to-notion."),
) -> None:
    """Ejecuta una investigacion SECOP con la entrada provista y escribe JSONL normalizado."""
    if apply and not to_notion:
        typer.echo("Para escribir en Notion usa --to-notion --apply.", err=True)
        raise typer.Exit(code=2)

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
    if not to_notion:
        typer.echo("Notion: no solicitado; nada fue escrito.")
        raise typer.Exit(code=0)

    records = _load_secop_records(run.jsonl_path)
    required_dbs = ["B2G SECOP Research"]
    if input_data.target_account_ref and not _looks_like_notion_page_id(input_data.target_account_ref):
        required_dbs.append("B2G Target Accounts")

    database_ids = {name: name for name in required_dbs}
    client = None
    if apply:
        _load_cli_env()
        if not os.environ.get("NOTION_TOKEN"):
            typer.echo("--apply requiere NOTION_TOKEN en el entorno.", err=True)
            raise typer.Exit(code=2)
        client, real = _build_notion_client()
        if not real:
            typer.echo("No se pudo inicializar el cliente real de Notion.", err=True)
            raise typer.Exit(code=2)
        database_ids = _database_ids_for_names(required_dbs, client)

    sync_result = sync_secop_research_to_notion(
        records=records,
        database_ids=database_ids,
        client=client,
        target_account_ref=input_data.target_account_ref,
    )
    created = sum(1 for item in sync_result.secop_records if item.action in {"create", "dry_run_create"})
    updated = sum(1 for item in sync_result.secop_records if item.action in {"update", "dry_run_update"})
    if apply:
        typer.echo(f"Notion escrito: {created} registros creados, {updated} actualizados en B2G SECOP Research.")
    else:
        typer.echo("Notion preview: nada fue escrito.")
        typer.echo(f"  upserts planeados en B2G SECOP Research: {len(sync_result.secop_records)}")
        typer.echo("  usa --apply para escribir estos resultados.")

    if sync_result.target_account_status == "direct_page_id":
        typer.echo("Target Account: relacionado usando el page id provisto.")
    elif sync_result.target_account_status == "resolved":
        typer.echo("Target Account: referencia resuelta y relacionada en Notion.")
    elif sync_result.target_account_status == "ambiguous":
        typer.echo("Target Account: referencia ambigua; los registros SECOP quedaron sin relacion.")
    elif sync_result.target_account_status == "not_resolved":
        typer.echo("Target Account: referencia no resuelta; los registros SECOP quedaron sin relacion.")
    else:
        typer.echo("Target Account: no provisto.")
    raise typer.Exit(code=0)


_OUTPUT_TYPE_MAP = {
    "outreach": ("outreach.md", "build_outreach_context", GtmOutputType.outreach),
    "meeting-prep": ("meeting-prep.md", "build_meeting_prep_context", GtmOutputType.meeting_prep),
    "proposal": ("proposal-brief.md", "build_proposal_context", GtmOutputType.proposal_brief),
}


def _build_gtm_output_for_write(
    *,
    output_type: GtmOutputType,
    type_label: str,
    opportunity: Dict[str, Any],
    account: Dict[str, Any],
    research: list[Dict[str, Any]],
    content: str,
    opportunity_page: Optional[str],
    target_account_page: Optional[str],
) -> GtmOutput:
    account_name = account.get("name") or account.get("normalized_name") or "Cuenta sin nombre"
    opportunity_title = opportunity.get("title") or account_name
    title = f"{type_label}: {opportunity_title}"
    research_page_ids = [item.get("id") for item in research if item.get("id")]
    evidence_keys = [
        item.get("source_record_id") or item.get("process_id") or item.get("contract_id") or item.get("id")
        for item in research
    ]
    evidence_payload = "|".join(sorted(str(key) for key in evidence_keys if key))
    source_summary = f"{len(research)} registros SECOP usados para {account_name}"
    return GtmOutput(
        type=output_type,
        title=title,
        content=content,
        source_summary=source_summary,
        source_evidence_hash=hashlib.sha256(evidence_payload.encode("utf-8")).hexdigest()[:16]
        if evidence_payload
        else None,
        target_account_ref=target_account_page or account.get("id"),
        opportunity_ref=opportunity_page or opportunity.get("id"),
        research_record_refs=[str(page_id) for page_id in research_page_ids],
    )


def _first_markdown_h1(content: str) -> Optional[str]:
    for line in content.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def _generated_import_title(type_label: str, file: Path) -> str:
    stem = file.stem.replace("-", " ").replace("_", " ").strip()
    return f"Imported {type_label}: {stem or 'markdown output'}"


def _build_imported_gtm_output(
    *,
    output_type: GtmOutputType,
    type_label: str,
    file: Path,
    content: str,
    target_account_page: Optional[str],
    opportunity_page: Optional[str],
    research_pages: list[str],
) -> GtmOutput:
    title = _first_markdown_h1(content) or _generated_import_title(type_label, file)
    relation_bits = []
    if target_account_page:
        relation_bits.append(f"Target Account {target_account_page}")
    if opportunity_page:
        relation_bits.append(f"Opportunity {opportunity_page}")
    if research_pages:
        relation_bits.append(f"{len(research_pages)} research records")
    relation_summary = "; ".join(relation_bits) if relation_bits else "no Notion relations provided"
    return GtmOutput(
        type=output_type,
        title=title,
        content=content,
        source_summary=f"Imported local markdown file '{file.name}'; {relation_summary}.",
        target_account_ref=target_account_page,
        opportunity_ref=opportunity_page,
        research_record_refs=research_pages,
    )


@output_app.command("create")
def output_create(
    type: str = typer.Option(..., "--type", help="Tipo de salida: outreach | meeting-prep | proposal."),
    source: Optional[str] = typer.Option(None, "--source", help="Ruta a JSON con {opportunity, account, research}."),
    opportunity_page: Optional[str] = typer.Option(None, "--opportunity-page", help="ID de pagina Notion de B2G Opportunities."),
    target_account_page: Optional[str] = typer.Option(None, "--target-account-page", help="ID de pagina Notion de B2G Target Accounts."),
    to_notion: bool = typer.Option(False, "--to-notion", help="Preparar escritura del output en Notion."),
    apply: bool = typer.Option(False, "--apply", help="Aplicar la escritura en Notion. Requiere --to-notion."),
    out: Path = typer.Option(None, "--out", help="Ruta opcional para escribir el markdown; si se omite, imprime a stdout."),
) -> None:
    """Genera entregables AE (outreach, meeting-prep, proposal) a partir de una oportunidad investigada."""
    if type not in _OUTPUT_TYPE_MAP:
        typer.echo(
            f"Tipo invalido '{type}'. Opciones: {', '.join(_OUTPUT_TYPE_MAP.keys())}.", err=True
        )
        raise typer.Exit(code=2)

    if opportunity_page and target_account_page:
        typer.echo("Usa solo --opportunity-page o --target-account-page, no ambos.", err=True)
        raise typer.Exit(code=2)

    if apply and not to_notion:
        typer.echo("Para escribir en Notion usa --to-notion --apply.", err=True)
        raise typer.Exit(code=2)

    client = None
    real = False
    database_ids: Dict[str, str] = {}
    if opportunity_page or target_account_page:
        client, real = _build_notion_client()
        if not real:
            typer.echo("Para leer inputs canonicos se requiere Notion configurado.", err=True)
            raise typer.Exit(code=2)
        database_ids = _database_ids_for_names(["B2G SECOP Research", "B2G GTM Outputs"], client)
        notion_input = (
            resolve_opportunity_input(
                opportunity_page_id=opportunity_page,
                database_ids=database_ids,
                client=client,
            )
            if opportunity_page
            else resolve_target_account_input(
                target_account_page_id=target_account_page,
                database_ids=database_ids,
                client=client,
            )
        )
        opportunity, account, research = notion_input.builder_args()
    else:
        if to_notion:
            typer.echo(
                "La escritura real en Notion requiere --opportunity-page o --target-account-page. "
                "Usa --source solo para preview local o importaciones explicitas.",
                err=True,
            )
            raise typer.Exit(code=2)
        if not source:
            typer.echo("Indica --source para preview local o --opportunity-page/--target-account-page para leer desde Notion.", err=True)
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

    template_name, _, output_type = _OUTPUT_TYPE_MAP[type]
    context = builders[type](opportunity, account, research)
    markdown = render(template_name, context)
    output = _build_gtm_output_for_write(
        output_type=output_type,
        type_label=type,
        opportunity=opportunity,
        account=account,
        research=research,
        content=markdown,
        opportunity_page=opportunity_page,
        target_account_page=target_account_page,
    )

    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
        typer.echo(f"OK: salida escrita en {out}")

    if to_notion:
        if not apply:
            typer.echo("Preview generado: no se escribio en Notion porque falta --apply.")
            if not out:
                typer.echo(markdown)
            raise typer.Exit(code=0)
        if client is None or not real:
            client, real = _build_notion_client()
        if not real:
            typer.echo("Para escribir en Notion se requiere Notion configurado.", err=True)
            raise typer.Exit(code=2)
        if not database_ids:
            database_ids = _database_ids_for_names(["B2G GTM Outputs"], client)
        result = upsert_gtm_output(database_ids["B2G GTM Outputs"], output, client)
        typer.echo(f"OK: output {'actualizado' if result.action == 'update' else 'creado'} en Notion")
        typer.echo(f"  pagina: {result.page_id}")
        raise typer.Exit(code=0)

    if not out:
        typer.echo(markdown)
    raise typer.Exit(code=0)


@output_app.command("import")
def output_import(
    type: str = typer.Option(..., "--type", help="Tipo de salida: outreach | meeting-prep | proposal."),
    file: Path = typer.Option(..., "--file", help="Ruta al markdown local existente."),
    target_account_page: Optional[str] = typer.Option(None, "--target-account-page", help="ID de pagina Notion de B2G Target Accounts."),
    opportunity_page: Optional[str] = typer.Option(None, "--opportunity-page", help="ID de pagina Notion de B2G Opportunities."),
    research_pages: Optional[list[str]] = typer.Option(None, "--research-page", help="ID de pagina Notion de B2G SECOP Research. Repetible."),
    to_notion: bool = typer.Option(False, "--to-notion", help="Preparar importacion del output en Notion."),
    apply: bool = typer.Option(False, "--apply", help="Aplicar la escritura en Notion. Requiere --to-notion."),
) -> None:
    """Importa un markdown local existente a B2G GTM Outputs. Default: preview sin escrituras."""
    if type not in _OUTPUT_TYPE_MAP:
        typer.echo(
            f"Tipo invalido '{type}'. Opciones: {', '.join(_OUTPUT_TYPE_MAP.keys())}.", err=True
        )
        raise typer.Exit(code=2)

    if apply and not to_notion:
        typer.echo("Para escribir en Notion usa --to-notion --apply.", err=True)
        raise typer.Exit(code=2)

    if apply and not (target_account_page or opportunity_page):
        typer.echo(
            "--apply requiere --target-account-page o --opportunity-page para evitar outputs sin relacion en Notion.",
            err=True,
        )
        raise typer.Exit(code=2)

    if not file.exists():
        typer.echo(f"Archivo markdown no encontrado: {file}", err=True)
        raise typer.Exit(code=2)

    content = file.read_text(encoding="utf-8")
    if not content.strip():
        typer.echo(f"Archivo markdown vacio: {file}", err=True)
        raise typer.Exit(code=2)

    _template_name, _builder_name, output_type = _OUTPUT_TYPE_MAP[type]
    output = _build_imported_gtm_output(
        output_type=output_type,
        type_label=type,
        file=file,
        content=content,
        target_account_page=target_account_page,
        opportunity_page=opportunity_page,
        research_pages=research_pages or [],
    )

    if not apply:
        preview = upsert_gtm_output("B2G GTM Outputs", output)
        typer.echo("Preview de importacion: nada fue escrito en Notion.")
        typer.echo(f"  output: {output.title}")
        typer.echo(f"  accion planeada: {preview.action}")
        typer.echo("  usa --to-notion --apply para escribir este output.")
        raise typer.Exit(code=0)

    client, real = _build_notion_client()
    if not real:
        typer.echo("Para escribir en Notion se requiere Notion configurado.", err=True)
        raise typer.Exit(code=2)
    database_ids = _database_ids_for_names(["B2G GTM Outputs"], client)
    result = upsert_gtm_output(database_ids["B2G GTM Outputs"], output, client)
    typer.echo(f"OK: output importado y {'actualizado' if result.action == 'update' else 'creado'} en Notion")
    typer.echo(f"  pagina: {result.page_id}")
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
