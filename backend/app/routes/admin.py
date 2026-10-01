"""Backup and restore.

Restore imports people, marriages, photos and stories from an uploaded backup. It deliberately
leaves the *users* table alone, so restoring a database from another machine does not replace
your login with the one from that machine.
"""

import sqlite3
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import text

from app.config import DB_FILE
from app.database import engine
from app.deps import get_current_active_user
from app.models import User as UserModel

router = APIRouter(prefix="/api/admin", tags=["admin"])

SQLITE_MAGIC = b"SQLite format 3\x00"
REQUIRED_TABLES = {"persons", "unions", "photos", "stories"}

TABLES = [
    (
        "persons",
        [
            "id", "first_name", "last_name", "maiden_name", "gender", "birth_date",
            "death_date", "birth_place", "death_place", "occupation", "bio", "is_living",
            "father_id", "mother_id", "created_at", "updated_at",
        ],
    ),
    ("unions", ["id", "partner_a_id", "partner_b_id", "status", "start_date", "end_date", "notes", "created_at", "updated_at"]),
    ("photos", ["id", "person_id", "filename", "thumb_filename", "original_name", "caption", "is_primary", "sort_order", "uploaded_at"]),
    ("stories", ["id", "person_id", "title", "body", "created_at", "updated_at"]),
]


@router.get("/backup")
def download_backup(_: UserModel = Depends(get_current_active_user)):
    """A consistent snapshot of the database, safe to take while the app is running."""
    handle = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    handle.close()
    source = sqlite3.connect(DB_FILE)
    try:
        destination = sqlite3.connect(handle.name)
        with destination:
            source.backup(destination)
        destination.close()
        payload = Path(handle.name).read_bytes()
    finally:
        source.close()
        Path(handle.name).unlink(missing_ok=True)

    return Response(
        content=payload,
        media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="family-tree-backup.db"'},
    )


def _read_table(connection: sqlite3.Connection, table: str, wanted: list[str]):
    present = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    columns = [name for name in wanted if name in present]
    if not columns:
        return [], []
    rows = connection.execute(f"SELECT {', '.join(columns)} FROM {table}").fetchall()
    return columns, [dict(zip(columns, row)) for row in rows]


@router.post("/restore")
async def restore_backup(
    file: UploadFile = File(...),
    _: UserModel = Depends(get_current_active_user),
):
    payload = await file.read()
    if not payload.startswith(SQLITE_MAGIC):
        raise HTTPException(status_code=400, detail="That file is not a SQLite database.")
    if len(payload) > 200 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Backup file is too large.")

    handle = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    handle.write(payload)
    handle.close()

    try:
        connection = sqlite3.connect(handle.name)
        try:
            tables = {
                row[0]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            missing = REQUIRED_TABLES - tables
            if missing:
                raise HTTPException(
                    status_code=400,
                    detail="That is not a family tree backup (missing: "
                    + ", ".join(sorted(missing))
                    + ").",
                )
            loaded = [(table, *_read_table(connection, table, columns)) for table, columns in TABLES]
        finally:
            connection.close()
    finally:
        Path(handle.name).unlink(missing_ok=True)

    counts = {}
    with engine.begin() as conn:
        # Children are inserted with their parents, so checks are deferred to the commit.
        conn.exec_driver_sql("PRAGMA defer_foreign_keys = ON")
        for table, _columns in reversed(TABLES):
            conn.execute(text(f"DELETE FROM {table}"))
        for table, columns, rows in loaded:
            counts[table] = len(rows)
            if rows:
                placeholders = ", ".join(f":{name}" for name in columns)
                conn.execute(
                    text(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"),
                    rows,
                )

    return {
        "people": counts.get("persons", 0),
        "unions": counts.get("unions", 0),
        "photos": counts.get("photos", 0),
        "stories": counts.get("stories", 0),
    }
