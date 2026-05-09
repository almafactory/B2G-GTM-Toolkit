from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from b2g_gtm_toolkit.models.notion import (
    NotionDatabaseSpec,
    NotionPropertySpec,
    NotionWorkspaceManifest,
)


class NotionClientLike(Protocol):
    def search_databases(self, query: str) -> List[Dict[str, Any]]: ...
    def retrieve_database(self, database_id: str) -> Optional[Dict[str, Any]]: ...


@dataclass
class PropertyIssue:
    database: str
    property: str
    kind: str
    detail: str


@dataclass
class DatabaseStatus:
    name: str
    found: bool
    database_id: Optional[str] = None
    missing_properties: List[str] = field(default_factory=list)
    mistyped_properties: List[PropertyIssue] = field(default_factory=list)
    missing_relations: List[PropertyIssue] = field(default_factory=list)


@dataclass
class VerifyReport:
    ok: bool
    databases: List[DatabaseStatus]
    errors: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        for db in self.databases:
            if not db.found:
                lines.append(f"- {db.name}: NO encontrada")
                continue
            problems = []
            if db.missing_properties:
                problems.append(f"propiedades faltantes: {', '.join(db.missing_properties)}")
            if db.mistyped_properties:
                items = ", ".join(f"{p.property} ({p.detail})" for p in db.mistyped_properties)
                problems.append(f"tipos incorrectos: {items}")
            if db.missing_relations:
                items = ", ".join(f"{p.property} -> {p.detail}" for p in db.missing_relations)
                problems.append(f"relaciones faltantes: {items}")
            if problems:
                lines.append(f"- {db.name}: " + "; ".join(problems))
            else:
                lines.append(f"- {db.name}: OK")
        return "\n".join(lines)


@dataclass
class SetupAction:
    kind: str
    database: str
    detail: str


@dataclass
class SetupPlan:
    creates: List[SetupAction] = field(default_factory=list)
    updates: List[SetupAction] = field(default_factory=list)
    noops: List[SetupAction] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.creates or self.updates)

    def summary(self) -> str:
        lines = []
        if self.creates:
            lines.append("Bases de datos a crear:")
            for a in self.creates:
                lines.append(f"  + {a.database}: {a.detail}")
        if self.updates:
            lines.append("Cambios en bases existentes:")
            for a in self.updates:
                lines.append(f"  ~ {a.database}: {a.detail}")
        if self.noops:
            lines.append("Sin cambios:")
            for a in self.noops:
                lines.append(f"  = {a.database}: {a.detail}")
        if not lines:
            lines.append("(plan vacio)")
        return "\n".join(lines)


def _property_type(prop_payload: Dict[str, Any]) -> Optional[str]:
    return prop_payload.get("type") if isinstance(prop_payload, dict) else None


def _check_database(spec: NotionDatabaseSpec, db_payload: Dict[str, Any]) -> DatabaseStatus:
    status = DatabaseStatus(
        name=spec.name,
        found=True,
        database_id=db_payload.get("id"),
    )
    properties: Dict[str, Any] = db_payload.get("properties", {}) or {}
    for prop in spec.properties:
        actual = properties.get(prop.name)
        if actual is None:
            status.missing_properties.append(prop.name)
            continue
        actual_type = _property_type(actual)
        if actual_type != prop.type.value:
            status.mistyped_properties.append(
                PropertyIssue(
                    database=spec.name,
                    property=prop.name,
                    kind="type_mismatch",
                    detail=f"esperado {prop.type.value}, encontrado {actual_type}",
                )
            )
            continue
        if prop.type.value == "relation":
            relation_block = actual.get("relation") if isinstance(actual, dict) else None
            target = None
            if isinstance(relation_block, dict):
                target = relation_block.get("database_id") or relation_block.get("database_name")
            if prop.relation_database and not target:
                status.missing_relations.append(
                    PropertyIssue(
                        database=spec.name,
                        property=prop.name,
                        kind="relation_missing_target",
                        detail=prop.relation_database,
                    )
                )
    return status


def _resolve_database_payload(
    spec: NotionDatabaseSpec,
    client: NotionClientLike,
    known_ids: Dict[str, str],
) -> Optional[Dict[str, Any]]:
    db_id = known_ids.get(spec.name)
    if db_id:
        try:
            payload = client.retrieve_database(db_id)
        except Exception:
            payload = None
        if payload:
            return payload
    try:
        candidates = client.search_databases(spec.name)
    except Exception:
        return None
    for candidate in candidates or []:
        title = _extract_title(candidate)
        if title == spec.name:
            return candidate
    return None


def _extract_title(payload: Dict[str, Any]) -> Optional[str]:
    title = payload.get("title")
    if isinstance(title, str):
        return title
    if isinstance(title, list):
        parts = []
        for piece in title:
            if isinstance(piece, dict):
                text = piece.get("plain_text") or piece.get("text", {}).get("content")
                if text:
                    parts.append(text)
        if parts:
            return "".join(parts)
    return payload.get("name")


def verify_workspace(
    manifest: NotionWorkspaceManifest,
    client: NotionClientLike,
    known_database_ids: Optional[Dict[str, str]] = None,
) -> VerifyReport:
    known = known_database_ids or {}
    statuses: List[DatabaseStatus] = []
    for spec in manifest.databases:
        payload = _resolve_database_payload(spec, client, known)
        if not payload:
            statuses.append(DatabaseStatus(name=spec.name, found=False))
            continue
        statuses.append(_check_database(spec, payload))

    ok = all(
        s.found
        and not s.missing_properties
        and not s.mistyped_properties
        and not s.missing_relations
        for s in statuses
    )
    return VerifyReport(ok=ok, databases=statuses)


def plan_setup(
    manifest: NotionWorkspaceManifest,
    current_state: VerifyReport,
) -> SetupPlan:
    plan = SetupPlan()
    state_by_name = {s.name: s for s in current_state.databases}
    for spec in manifest.databases:
        state = state_by_name.get(spec.name)
        if state is None or not state.found:
            plan.creates.append(
                SetupAction(
                    kind="create_database",
                    database=spec.name,
                    detail=f"crear base con {len(spec.properties)} propiedades",
                )
            )
            continue
        details = []
        if state.missing_properties:
            details.append(
                "agregar propiedades: " + ", ".join(state.missing_properties)
            )
        if state.mistyped_properties:
            details.append(
                "corregir tipos: "
                + ", ".join(p.property for p in state.mistyped_properties)
            )
        if state.missing_relations:
            details.append(
                "configurar relaciones: "
                + ", ".join(p.property for p in state.missing_relations)
            )
        if details:
            plan.updates.append(
                SetupAction(
                    kind="update_database",
                    database=spec.name,
                    detail="; ".join(details),
                )
            )
        else:
            plan.noops.append(
                SetupAction(
                    kind="noop",
                    database=spec.name,
                    detail="schema OK",
                )
            )
    return plan
