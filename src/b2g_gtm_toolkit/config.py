from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("B2G_DATA_DIR", PROJECT_ROOT / "data"))
RUNS_DIR = DATA_DIR / "runs"

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")
NOTION_WORKSPACE_NAME = os.getenv("NOTION_WORKSPACE_NAME")

SECOP_BASE_URL = os.getenv("SECOP_BASE_URL", "https://www.datos.gov.co/resource")
SECOP_APP_TOKEN = os.getenv("SECOP_APP_TOKEN")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")
