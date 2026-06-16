from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.dependencies import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def live():
    try:
        return {"status": "alive"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get('/db')
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text('SELECT DATABASE()'))
        return {"db": "connected", "result": result.scalar()}
    except Exception as e:
        return {"db": "disconnected", "error": str(e)}
    