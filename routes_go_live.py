"""
Go-Live Import Pipeline API Endpoints
Enhanced CSV upload with validation, idempotency, and error handling
"""

import io
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from auth.dependencies import get_optional_current_user
from csv_mapper import ImportPipeline
from db import get_session as get_db
from models import Booking, ImportLog, User

router = APIRouter(prefix="/api/go-live", tags=["Go-Live Import Pipeline"])


@router.post("/upload")
async def go_live_upload(
    files: List[UploadFile] = File(...),
    source: str = Form("airbnb"),  # "airbnb" or "offline"
    channel: str = Form("official_csv"),  # "official_csv", "facebook", "zalo", etc.
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Enhanced CSV upload endpoint for Go-Live pipeline

    Args:
        files: List of CSV files to upload
        source: Data source type ("airbnb" or "offline")
        channel: Specific channel ("official_csv", "facebook", "zalo", etc.)

    Returns:
        Detailed processing results with validation summary
    """

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    pipeline = ImportPipeline()
    total_results = []
    total_stats = {
        "files_processed": 0,
        "total_rows": 0,
        "valid_rows": 0,
        "invalid_rows": 0,
        "duplicate_rows": 0,
        "rows_inserted": 0,
        "rows_skipped": 0,
        "processing_time": 0,
    }

    processing_start = datetime.utcnow()

    for upload_file in files:
        file_start = datetime.utcnow()
        filename = upload_file.filename or "unknown.csv"

        try:
            # Read and validate CSV
            content = await upload_file.read()
            df = pd.read_csv(io.BytesIO(content))

            if df.empty:
                total_results.append(
                    {
                        "filename": filename,
                        "success": False,
                        "error": "Empty CSV file",
                        "stats": {},
                    }
                )
                continue

            # Process CSV through pipeline
            valid_rows, ingestion_id = pipeline.process_csv(df, source, channel)

            # Save to database
            rows_inserted = 0
            rows_skipped = 0

            for row_data in valid_rows:
                # Check for existing row hash (idempotency)
                existing = db.exec(
                    select(Booking).where(Booking.row_hash == row_data["row_hash"])
                ).first()

                if existing:
                    rows_skipped += 1
                    continue

                # Create new booking
                booking = Booking(
                    **{k: v for k, v in row_data.items() if k != "row_hash"}
                )
                booking.row_hash = row_data["row_hash"]

                db.add(booking)
                rows_inserted += 1

            db.commit()

            # Save error log if there are errors
            error_file = None
            if pipeline.errors:
                error_file = pipeline.save_error_log(f"{ingestion_id}_{filename}")

            # Create import log entry
            file_processing_time = (datetime.utcnow() - file_start).total_seconds()

            import_log = ImportLog(
                filename=filename,
                source=source,
                channel=channel,
                ingestion_id=ingestion_id,
                rows_total=len(df),
                rows_inserted=rows_inserted,
                rows_updated=0,  # We don't update existing rows in this version
                rows_skipped=rows_skipped,
                rows_errors=len(pipeline.errors),
                file_size_bytes=len(content),
                processing_time_seconds=file_processing_time,
                error_log_file=error_file,
                completed_at=datetime.utcnow(),
            )

            db.add(import_log)
            db.commit()

            # Get processing summary
            file_summary = pipeline.get_processing_summary()
            file_summary.update(
                {
                    "rows_inserted": rows_inserted,
                    "rows_skipped": rows_skipped,
                    "processing_time": file_processing_time,
                    "ingestion_id": ingestion_id,
                    "error_log_file": error_file,
                }
            )

            total_results.append(
                {"filename": filename, "success": True, "stats": file_summary}
            )

            # Update totals
            total_stats["files_processed"] += 1
            total_stats["total_rows"] += file_summary["total_rows"]
            total_stats["valid_rows"] += file_summary["valid_rows"]
            total_stats["invalid_rows"] += file_summary["invalid_rows"]
            total_stats["duplicate_rows"] += file_summary["duplicate_rows"]
            total_stats["rows_inserted"] += rows_inserted
            total_stats["rows_skipped"] += rows_skipped

            # Reset pipeline for next file
            pipeline = ImportPipeline()

        except Exception as e:
            total_results.append(
                {"filename": filename, "success": False, "error": str(e), "stats": {}}
            )

    total_stats["processing_time"] = (
        datetime.utcnow() - processing_start
    ).total_seconds()

    return {
        "success": True,
        "message": f"Processed {total_stats['files_processed']} files",
        "summary": total_stats,
        "files": total_results,
    }


@router.post("/validate")
async def validate_csv(
    files: List[UploadFile] = File(...),
    source: str = Form("airbnb"),
    channel: str = Form("official_csv"),
):
    """
    Validate CSV files without importing to database
    Useful for pre-upload validation
    """

    pipeline = ImportPipeline()
    validation_results = []

    for upload_file in files:
        filename = upload_file.filename or "unknown.csv"

        try:
            content = await upload_file.read()
            df = pd.read_csv(io.BytesIO(content))

            if df.empty:
                validation_results.append(
                    {
                        "filename": filename,
                        "valid": False,
                        "error": "Empty CSV file",
                        "stats": {},
                    }
                )
                continue

            # Process through validation pipeline
            valid_rows, ingestion_id = pipeline.process_csv(df, source, channel)

            # Get validation summary
            summary = pipeline.get_processing_summary()
            summary["sample_valid_rows"] = valid_rows[
                :3
            ]  # First 3 valid rows as example
            summary["sample_errors"] = pipeline.errors[:5]  # First 5 errors as example

            validation_results.append(
                {"filename": filename, "valid": len(valid_rows) > 0, "stats": summary}
            )

        except Exception as e:
            validation_results.append(
                {"filename": filename, "valid": False, "error": str(e), "stats": {}}
            )

    return {
        "success": True,
        "message": f"Validated {len(files)} files",
        "results": validation_results,
    }


@router.get("/import-history")
async def get_import_history(
    limit: int = 50,
    source: Optional[str] = None,
    channel: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get import history with filtering options"""

    query = select(ImportLog).order_by(ImportLog.created_at.desc())

    if source:
        query = query.where(ImportLog.source == source)

    if channel:
        query = query.where(ImportLog.channel == channel)

    query = query.limit(limit)

    import_logs = db.exec(query).all()

    return {
        "success": True,
        "count": len(import_logs),
        "imports": [
            {
                "id": log.id,
                "filename": log.filename,
                "source": log.source,
                "channel": log.channel,
                "ingestion_id": log.ingestion_id,
                "rows_total": log.rows_total,
                "rows_inserted": log.rows_inserted,
                "rows_skipped": log.rows_skipped,
                "rows_errors": log.rows_errors,
                "success_rate": round(
                    (log.rows_inserted / max(log.rows_total, 1)) * 100, 2
                ),
                "processing_time": log.processing_time_seconds,
                "created_at": log.created_at,
                "completed_at": log.completed_at,
                "error_log_file": log.error_log_file,
            }
            for log in import_logs
        ],
    }


@router.get("/stats")
async def get_import_stats(db: Session = Depends(get_db)):
    """Get overall import statistics"""

    # Basic stats
    total_imports = db.exec(select(ImportLog)).all()

    if not total_imports:
        return {
            "success": True,
            "stats": {
                "total_imports": 0,
                "total_rows_processed": 0,
                "total_rows_inserted": 0,
                "total_errors": 0,
                "success_rate": 0,
                "sources": {},
                "channels": {},
            },
        }

    # Calculate aggregated stats
    total_rows_processed = sum(log.rows_total for log in total_imports)
    total_rows_inserted = sum(log.rows_inserted for log in total_imports)
    total_errors = sum(log.rows_errors for log in total_imports)

    # Group by source and channel
    sources = {}
    channels = {}

    for log in total_imports:
        # Source stats
        if log.source not in sources:
            sources[log.source] = {"imports": 0, "rows": 0, "inserted": 0}
        sources[log.source]["imports"] += 1
        sources[log.source]["rows"] += log.rows_total
        sources[log.source]["inserted"] += log.rows_inserted

        # Channel stats
        if log.channel not in channels:
            channels[log.channel] = {"imports": 0, "rows": 0, "inserted": 0}
        channels[log.channel]["imports"] += 1
        channels[log.channel]["rows"] += log.rows_total
        channels[log.channel]["inserted"] += log.rows_inserted

    return {
        "success": True,
        "stats": {
            "total_imports": len(total_imports),
            "total_rows_processed": total_rows_processed,
            "total_rows_inserted": total_rows_inserted,
            "total_errors": total_errors,
            "success_rate": round(
                (total_rows_inserted / max(total_rows_processed, 1)) * 100, 2
            ),
            "sources": sources,
            "channels": channels,
        },
    }
