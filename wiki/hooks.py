"""MkDocs build hooks — inject a single build timestamp into every page."""
from datetime import datetime, timezone

_BUILD_DATE = None


def on_config(config, **kwargs):
    global _BUILD_DATE
    _BUILD_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    config["extra"]["last_built"] = _BUILD_DATE
    return config


def on_page_context(context, page, **kwargs):
    # Material theme renders this meta field as "Last update" in the page footer.
    if _BUILD_DATE:
        page.meta["git_revision_date_localized"] = _BUILD_DATE
    return context
