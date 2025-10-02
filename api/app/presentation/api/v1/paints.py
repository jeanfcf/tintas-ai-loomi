"""Paint management routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.infrastructure.database import get_db
from app.domain.entities import (
    Paint, PaintCreate, PaintUpdate, PaintResponse, PaintFilters, 
    PaginationParams, PaginatedPaintResponse, SurfaceType, Environment, 
    FinishType, PaintLine, CSVImportRequest, CSVImportResponse
)
from app.services.embedding_service import EmbeddingService
from app.infrastructure.middleware import get_current_admin_user
from app.core.logging import get_logger
from app.core.container import container

logger = get_logger(__name__)

router = APIRouter(prefix="/paints", tags=["paints"])


def _parse_and_validate_filters(
    search: str,
    color: str,
    surface_types: Optional[str],
    environment: Optional[Environment],
    finish_type: Optional[FinishType],
    line: Optional[PaintLine],
    features: Optional[str]
) -> PaintFilters:
    """Parse and validate paint filters."""
    from app.domain.validators import FilterValidator
    
    # Sanitize string parameters
    search_clean = search.strip() if search and search.strip() else None
    color_clean = color.strip() if color and color.strip() else None
    
    # Parse and validate features
    features_list = []
    if features and features.strip():
        try:
            features_list = [f.strip() for f in features.split(",") if f.strip()]
            for feature in features_list:
                if len(feature) > 50:
                    raise ValueError(f"Feature '{feature}' is too long (max 50 characters)")
                if not feature.replace(' ', '').replace('-', '').replace('_', '').isalnum():
                    raise ValueError(f"Feature '{feature}' contains invalid characters")
        except Exception as e:
            raise ValueError(f"Invalid features format: {str(e)}")
    
    # Parse and validate surface types
    surface_types_list = []
    if surface_types and surface_types.strip():
        try:
            surface_types_list = [SurfaceType(s.strip().lower()) for s in surface_types.split(",") if s.strip()]
        except Exception as e:
            raise ValueError(f"Invalid surface types format: {str(e)}")
    
    # Create filters with validated data
    filters = PaintFilters(
        search=search_clean,
        color=color_clean,
        surface_types=surface_types_list if surface_types_list else None,
        environment=environment,
        finish_type=finish_type,
        line=line,
        features=features_list if features_list else None
    )
    
    # Validate filters
    FilterValidator.validate_filters(filters)
    return filters


@router.post("/", response_model=PaintResponse, status_code=status.HTTP_201_CREATED, summary="Create Paint")
async def create_paint(
    paint_data: PaintCreate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new paint with automatic embedding generation."""
    try:
        paint_service = container.get_paint_service()
        paint = paint_service.create_paint(db, paint_data)
        
        # Generate and store embedding
        embedding_service = container.get_embedding_service()
        await embedding_service.generate_and_store_embedding(db, paint.id)
        
        logger.info(f"Paint created: {paint.name}")
        return paint
        
    except ValueError as e:
        logger.warning(f"Validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating paint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/public", response_model=PaginatedPaintResponse, summary="Get All Paints (Public)")
async def get_paints_public(
    skip: int = Query(0, ge=0, description="Number of paints to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of paints to return"),
    search: str = Query("", max_length=100, description="Search term for name, color, or description"),
    color: str = Query("", max_length=50, description="Filter by color"),
    surface_types: Optional[str] = Query("", max_length=200, description="Filter by surface types (comma-separated)"),
    environment: Optional[Environment] = Query(None, description="Filter by environment"),
    finish_type: Optional[FinishType] = Query(None, description="Filter by finish type"),
    line: Optional[PaintLine] = Query(None, description="Filter by paint line"),
    features: Optional[str] = Query("", max_length=500, description="Filter by features (comma-separated)"),
    db: Session = Depends(get_db)
):
    """Get all paints with pagination and filters (public access)."""
    try:
        filters = _parse_and_validate_filters(search, color, surface_types, environment, finish_type, line, features)
        
        from app.domain.validators import PaginationValidator
        PaginationValidator.validate(skip, limit)
        
        pagination = PaginationParams(skip=skip, limit=limit)
        paint_service = container.get_paint_service()
        result = paint_service.get_paints(db, pagination, filters)
        
        logger.info(f"Retrieved {len(result.items)} paints")
        return result
        
    except ValueError as e:
        logger.warning(f"Validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving paints: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=PaginatedPaintResponse, summary="Get All Paints")
async def get_paints(
    skip: int = Query(0, ge=0, description="Number of paints to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of paints to return"),
    search: str = Query("", max_length=100, description="Search term for name, color, or description"),
    color: str = Query("", max_length=50, description="Filter by color"),
    surface_types: Optional[str] = Query("", max_length=200, description="Filter by surface types (comma-separated)"),
    environment: Optional[Environment] = Query(None, description="Filter by environment"),
    finish_type: Optional[FinishType] = Query(None, description="Filter by finish type"),
    line: Optional[PaintLine] = Query(None, description="Filter by paint line"),
    features: Optional[str] = Query("", max_length=500, description="Filter by features (comma-separated)"),
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all paints with pagination and filters."""
    try:
        filters = _parse_and_validate_filters(search, color, surface_types, environment, finish_type, line, features)
        
        from app.domain.validators import PaginationValidator
        PaginationValidator.validate(skip, limit)
        
        pagination = PaginationParams(skip=skip, limit=limit)
        paint_service = container.get_paint_service()
        result = paint_service.get_paints(db, pagination, filters)
        
        logger.info(f"Retrieved {len(result.items)} paints")
        return result
        
    except ValueError as e:
        logger.warning(f"Validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving paints: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{paint_id}", response_model=PaintResponse, summary="Get Paint by ID")
async def get_paint(
    paint_id: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get paint by ID."""
    try:
        paint_service = container.get_paint_service()
        paint = paint_service.get_paint(db, paint_id)
        
        if not paint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paint not found"
            )
        
        logger.info(f"Paint retrieved - id: {paint_id}, name: {paint.name}")
        return paint
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving paint: {e} - paint_id: {paint_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{paint_id}", response_model=PaintResponse, summary="Update Paint")
async def update_paint(
    paint_id: int,
    paint_data: PaintUpdate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update paint with automatic embedding regeneration."""
    try:
        paint_service = container.get_paint_service()
        paint = paint_service.update_paint(db, paint_id, paint_data)
        
        if not paint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paint not found"
            )
        
        # Regenerate and store embedding
        embedding_service = container.get_embedding_service()
        await embedding_service.generate_and_store_embedding(db, paint.id)
        
        logger.info(f"Paint updated - id: {paint_id}, name: {paint.name}")
        return paint
        
    except ValueError as e:
        logger.warning(f"Paint update validation failed: {e} - paint_id: {paint_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating paint: {e} - paint_id: {paint_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{paint_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Paint")
async def delete_paint(
    paint_id: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Soft delete paint."""
    try:
        paint_service = container.get_paint_service()
        success = paint_service.delete_paint(db, paint_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paint not found"
            )
        
        logger.info(f"Paint deleted - id: {paint_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting paint: {e} - paint_id: {paint_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/search/filters", response_model=List[PaintResponse], summary="Search Paints by Filters")
async def search_paints_by_filters(
    search: str = Query("", description="Search term for name, color, or description"),
    color: str = Query("", description="Filter by color"),
    surface_types: Optional[str] = Query("", max_length=200, description="Filter by surface types (comma-separated)"),
    environment: Optional[Environment] = Query(None, description="Filter by environment"),
    finish_type: Optional[FinishType] = Query(None, description="Filter by finish type"),
    line: Optional[PaintLine] = Query(None, description="Filter by paint line"),
    features: Optional[str] = Query("", max_length=500, description="Filter by features (comma-separated)"),
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Search paints by specific filters without pagination."""
    try:
        filters = _parse_and_validate_filters(search, color, surface_types, environment, finish_type, line, features)
        
        paint_service = container.get_paint_service()
        paints = paint_service.get_paints_by_filters(db, filters)
        
        logger.info(f"Found {len(paints)} paints")
        return paints
        
    except ValueError as e:
        logger.warning(f"Validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/by-name/{name}", response_model=PaintResponse, summary="Get Paint by Name")
async def get_paint_by_name(
    name: str,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get paint by name."""
    try:
        paint_service = container.get_paint_service()
        paint = paint_service.get_paint_by_name(db, name)
        
        if not paint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paint not found"
            )
        
        logger.info(f"Paint retrieved by name - name: {name}")
        return paint
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving paint by name: {e} - name: {name}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/import-csv", response_model=CSVImportResponse, status_code=status.HTTP_200_OK, summary="Import Paints from CSV")
async def import_paints_from_csv(
    import_request: CSVImportRequest,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Import paints from CSV file.
    
    CSV format must include the following columns:
    - nome: Paint name
    - cor: Color
    - tipo_parede: Surface types (comma-separated: alvenaria, madeira, ferro, concrete, metal, plastic)
    - ambiente: Environment (interno, externo, interno/externo)
    - acabamento: Finish type (fosco, acetinado, brilhante, semi-brilhante)
    - features: Features (comma-separated list)
    - linha: Paint line (premium, standard, economic)
    """
    try:
        csv_import_service = container.get_csv_import_service()
        result = await csv_import_service.import_paints_from_csv(db, import_request)
        
        logger.info(f"CSV import completed - file: {import_request.file_name}, success: {result.success}")
        return result
        
    except ValueError as e:
        logger.warning(f"CSV import validation failed: {e} - file: {import_request.file_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during CSV import: {e} - file: {import_request.file_name}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/search/similar", response_model=List[Dict[str, Any]], summary="Search Similar Paints")
async def search_similar_paints(
    query: str = Query(..., description="Search query for similar paints"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Similarity threshold"),
    db: Session = Depends(get_db)
):
    """Search for paints similar to the given query using embeddings."""
    try:
        embedding_service = EmbeddingService()
        results = await embedding_service.search_similar_paints(
            query=query,
            db=db,
            limit=limit,
            threshold=threshold
        )
        
        logger.info(f"Similar paint search completed - query: {query}, results: {len(results)}")
        return results
        
    except Exception as e:
        logger.error(f"Error in similar paint search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for similar paints"
        )
