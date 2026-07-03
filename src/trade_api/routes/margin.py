from fastapi import APIRouter
from trade_api.models import MarginResponse, MarginSegment

router = APIRouter(prefix="/margin", tags=["Margin"])

@router.get(
    "/available", 
    response_model=MarginResponse,
    summary="Get Available Margin",
    description="Returns real-time margin utilization and available limits across all segments. Matches Groww SDK margin.get_margin() output."
)
async def get_margin():
    # Mock data exactly matching Groww's nested schema
    return MarginResponse(
        equity=MarginSegment(
            used=15000.50,
            available=85000.00,
            total=100000.50
        ),
        commodity=MarginSegment(
            used=0.0,
            available=50000.00,
            total=50000.00
        ),
        fno=MarginSegment(
            used=25000.00,
            available=125000.00,
            total=150000.00
        ),
        currency=MarginSegment(
            used=0.0,
            available=0.0,
            total=0.0
        )
    )