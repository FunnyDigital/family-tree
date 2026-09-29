import io
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps

from app.config import ALLOWED_IMAGE_TYPES, MAX_UPLOAD_BYTES, THUMB_SIZE, UPLOAD_DIR

EXT_BY_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def ensure_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def person_dir(person_id: int) -> Path:
    directory = UPLOAD_DIR / str(person_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_photo(person_id: int, upload: UploadFile) -> dict:
    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    data = upload.file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Empty upload")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit",
        )

    ext = EXT_BY_TYPE.get(upload.content_type) or Path(upload.filename or "").suffix or ".jpg"
    stem = uuid.uuid4().hex
    filename = f"{stem}{ext}"
    thumb_filename = f"{stem}_thumb.jpg"

    directory = person_dir(person_id)
    (directory / filename).write_bytes(data)

    try:
        image = Image.open(io.BytesIO(data))
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        image.thumbnail((THUMB_SIZE, THUMB_SIZE))
        image.save(directory / thumb_filename, "JPEG", quality=85, optimize=True)
    except Exception:
        thumb_filename = filename

    return {
        "filename": f"{person_id}/{filename}",
        "thumb_filename": f"{person_id}/{thumb_filename}",
        "original_name": upload.filename,
    }


def delete_photo_files(filename: str, thumb_filename: str | None) -> None:
    for rel in {filename, thumb_filename}:
        if not rel:
            continue
        target = (UPLOAD_DIR / rel).resolve()
        try:
            target.relative_to(UPLOAD_DIR.resolve())
        except ValueError:
            continue
        if target.is_file():
            target.unlink(missing_ok=True)


def delete_person_files(person_id: int) -> None:
    directory = (UPLOAD_DIR / str(person_id)).resolve()
    try:
        directory.relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        return
    if directory.is_dir():
        for child in directory.iterdir():
            if child.is_file():
                child.unlink(missing_ok=True)
        directory.rmdir()
