"""
Specifications API Router

Endpoints for viewing and managing generated specifications.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, PlainTextResponse

from config.settings import get_settings
from spec_ai_writer.core.phase_manager import PhaseManager
from spec_ai_writer.utils.validation import validate_project_id, validate_path_within_directory
from ..models import (
    SpecificationResponse,
    SpecificationListResponse,
    SpecificationGenerateRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()

settings = get_settings()
phase_manager = PhaseManager()


def _get_specs_dir(project_id: str) -> Path:
    """Get specs directory for project."""
    validate_project_id(project_id)
    specs_dir = Path(settings.data_dir) / project_id / "specs"
    validate_path_within_directory(specs_dir, Path(settings.data_dir))
    return specs_dir


def _get_spec_file(project_id: str, filename: str) -> Path:
    """Get specification file path."""
    return _get_specs_dir(project_id) / filename


@router.get("/{project_id}/download-all")
async def download_all_specifications(project_id: str):
    """
    Download all specifications as a ZIP file.

    Returns a ZIP archive containing all generated specification files.
    """
    import io
    import zipfile
    from fastapi.responses import StreamingResponse

    try:
        specs_dir = _get_specs_dir(project_id)

        if not specs_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No specifications found for project '{project_id}'"
            )

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            spec_count = 0

            for i in range(1, 8):
                phase_info = phase_manager.get_phase_info(i)
                spec_file = specs_dir / phase_info.filename

                if spec_file.exists():
                    zip_file.write(spec_file, arcname=phase_info.filename)
                    spec_count += 1

            if spec_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No specifications found for project '{project_id}'"
                )

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={project_id}_specifications.zip"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download all specifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download all specifications: {str(e)}"
        )


@router.get("/{project_id}", response_model=SpecificationListResponse)
async def list_specifications(project_id: str):
    """
    List all generated specifications for a project.

    Returns a list of all specification files with their metadata.
    """
    try:
        specs_dir = _get_specs_dir(project_id)

        if not specs_dir.exists():
            return SpecificationListResponse(
                project_id=project_id,
                specifications=[]
            )

        specifications = []

        for i in range(1, 8):
            phase_info = phase_manager.get_phase_info(i)
            spec_file = specs_dir / phase_info.filename

            if spec_file.exists():
                specifications.append({
                    "phase_num": i,
                    "phase_name": phase_info.name,
                    "filename": phase_info.filename,
                    "file_size": spec_file.stat().st_size,
                    "generated_at": datetime.fromtimestamp(spec_file.stat().st_mtime).isoformat(),
                    "exists": True
                })
            else:
                specifications.append({
                    "phase_num": i,
                    "phase_name": phase_info.name,
                    "filename": phase_info.filename,
                    "exists": False
                })

        return SpecificationListResponse(
            project_id=project_id,
            specifications=specifications
        )

    except Exception as e:
        logger.error(f"Failed to list specifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list specifications: {str(e)}"
        )


@router.get("/{project_id}/{phase_num}", response_model=SpecificationResponse)
async def get_specification(project_id: str, phase_num: int):
    """
    Get a specific specification by phase number.

    Returns the content of the specification file.
    """
    try:
        if phase_num < 1 or phase_num > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid phase number: {phase_num}. Must be between 1 and 7."
            )

        phase_info = phase_manager.get_phase_info(phase_num)
        spec_file = _get_spec_file(project_id, phase_info.filename)

        if not spec_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Specification for phase {phase_num} not found"
            )

        # Read file content
        content = spec_file.read_text(encoding="utf-8")

        return SpecificationResponse(
            project_id=project_id,
            phase_num=phase_num,
            phase_name=phase_info.name,
            filename=phase_info.filename,
            content=content,
            generated_at=datetime.fromtimestamp(spec_file.stat().st_mtime)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get specification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get specification: {str(e)}"
        )


@router.get("/{project_id}/{phase_num}/download")
async def download_specification(project_id: str, phase_num: int):
    """
    Download a specification file.

    Returns the specification as a downloadable Markdown file.
    """
    try:
        if phase_num < 1 or phase_num > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid phase number: {phase_num}. Must be between 1 and 7."
            )

        phase_info = phase_manager.get_phase_info(phase_num)
        spec_file = _get_spec_file(project_id, phase_info.filename)

        if not spec_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Specification for phase {phase_num} not found"
            )

        return FileResponse(
            path=str(spec_file),
            media_type="text/markdown",
            filename=phase_info.filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download specification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download specification: {str(e)}"
        )
