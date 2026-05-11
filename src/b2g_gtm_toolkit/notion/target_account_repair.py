"""Find and merge duplicate B2G Target Account pages that share NIT or name+municipality."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Sequence

from b2g_gtm_toolkit.models.gtm import TargetAccount
from b2g_gtm_toolkit.notion.dedupe_norm import (
    entity_name_normalized,
    municipality_normalized,
    nit_digits_normalized,
)
from b2g_gtm_toolkit.notion.read import relation_contains_filter, target_account_from_page
from b2g_gtm_toolkit.notion.write import pick_canonical_target_account_page

FILTER_FETCHER = Callable[[str, Dict[str, Any]], List[Dict[str, Any]]]


def snapshot_from_target_page(page: Dict[str, Any]) -> tuple[tuple[str, str], Dict[str, Any]]:
    blob = target_account_from_page(page)
    nit_k = nit_digits_normalized(blob.get("nit"))
    name_norm = entity_name_normalized(
        normalized_name=blob.get("normalized_name"),
        display_name=blob.get("name") or "",
    )
    mun_norm = municipality_normalized(blob.get("municipality") or "")
    pid = page.get("id") or ""
    summary = {
        "page_id": pid,
        "nit_key": nit_k,
        "title": blob.get("name"),
        "municipality": blob.get("municipality"),
    }
    if nit_k:
        return ("nit", nit_k), summary
    geo_key = f"{name_norm}|{mun_norm}"
    return ("geo", geo_key), summary


def grouping_label(group_type: str, key_part: str) -> str:
    return f"{group_type}:{key_part}"


def find_duplicate_groups(pages: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: MutableMapping[str, List[Dict[str, Any]]] = {}
    metas: Dict[str, tuple[str, str]] = {}
    for page in pages:
        (kind, raw_key), _summary = snapshot_from_target_page(page)
        if kind == "geo" and (not raw_key or raw_key == "|"):
            continue
        gk = grouping_label(kind, raw_key)
        buckets.setdefault(gk, []).append(page)
        metas[gk] = (kind, raw_key)

    duplicates: List[Dict[str, Any]] = []
    for gk, group_pages in buckets.items():
        if len(group_pages) < 2:
            continue
        kind, raw_key = metas[gk]
        summaries: List[Dict[str, Any]] = []
        for p in group_pages:
            _, s = snapshot_from_target_page(p)
            summaries.append(s)
        s0 = summaries[0]
        synthetic = TargetAccount(
            name=(s0.get("title") or "Unknown"),
            nit=(s0.get("nit_key") or None),
            municipality=s0.get("municipality"),
        )
        canonical_id = pick_canonical_target_account_page(group_pages, synthetic)
        dup_ids = [p["id"] for p in group_pages if p.get("id") != canonical_id]
        duplicates.append(
            {
                "group_key": gk,
                "match_kind": kind,
                "match_value": raw_key,
                "canonical_page_id": canonical_id,
                "duplicate_page_ids": dup_ids,
                "pages": summaries,
            }
        )
    duplicates.sort(key=lambda item: item["group_key"])
    return duplicates


@dataclass
class RepairApplyResult:
    relinked_secop: int
    relinked_outputs: int
    archived_pages: int


def _single_target_relation(canonical_id: str) -> Dict[str, Any]:
    return {"Target Account": {"relation": [{"id": canonical_id}]}}


def apply_duplicate_merge(
    *,
    duplicate_groups: Sequence[Mapping[str, Any]],
    client: Any,
    secop_database_id: str,
    gtm_outputs_database_id: str,
    fetch_with_filter: FILTER_FETCHER,
    archive_duplicates: bool = True,
) -> RepairApplyResult:
    relinked_secop = 0
    relinked_outputs = 0
    canonical_by_dup: Dict[str, str] = {}
    for group in duplicate_groups:
        canonical_id = group.get("canonical_page_id") or ""
        for dup_id in group.get("duplicate_page_ids") or []:
            if dup_id != canonical_id:
                canonical_by_dup[dup_id] = canonical_id

    for dup_id, canonical_id in canonical_by_dup.items():
        for sp in fetch_with_filter(secop_database_id, relation_contains_filter("Target Account", dup_id)):
            pid = sp.get("id")
            if pid:
                client.update_page(pid, _single_target_relation(canonical_id))
                relinked_secop += 1
        for op in fetch_with_filter(gtm_outputs_database_id, relation_contains_filter("Target Account", dup_id)):
            pid = op.get("id")
            if pid:
                client.update_page(pid, _single_target_relation(canonical_id))
                relinked_outputs += 1

    archived_pages = 0
    archive = getattr(client, "archive_page", None)
    if archive_duplicates and callable(archive):
        for dup_id in canonical_by_dup:
            archive(dup_id)
            archived_pages += 1

    return RepairApplyResult(
        relinked_secop=relinked_secop,
        relinked_outputs=relinked_outputs,
        archived_pages=archived_pages,
    )
