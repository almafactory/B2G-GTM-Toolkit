from __future__ import annotations

from typing import Dict, Optional

from b2g_gtm_toolkit.models.notion import (
    NotionDatabaseSpec,
    NotionWorkspaceManifest,
    default_workspace_manifest,
)

DEFAULT_MANIFEST: NotionWorkspaceManifest = default_workspace_manifest()


REQUIRED_DATABASE_NAMES = [db.name for db in DEFAULT_MANIFEST.databases]


def manifest_for(env_overrides: Optional[Dict[str, str]] = None) -> NotionWorkspaceManifest:
    """Return the default workspace manifest, optionally overriding database names.

    `env_overrides` keys are the canonical database names (e.g. "B2G ICPs"); values
    replace the resulting `name` for that database. Useful for workspaces that already
    contain renamed databases."""
    manifest = default_workspace_manifest()
    if not env_overrides:
        return manifest

    new_dbs = []
    for db in manifest.databases:
        new_name = env_overrides.get(db.name, db.name)
        if new_name == db.name:
            new_dbs.append(db)
        else:
            new_dbs.append(
                NotionDatabaseSpec(
                    name=new_name,
                    description=db.description,
                    properties=list(db.properties),
                )
            )
    return NotionWorkspaceManifest(version=manifest.version, databases=new_dbs)


def find_database(manifest: NotionWorkspaceManifest, name: str) -> Optional[NotionDatabaseSpec]:
    for db in manifest.databases:
        if db.name == name:
            return db
    return None
