from fastapi import APIRouter

router = APIRouter()

# Temporary placeholder — will be replaced in step 5
@router.get("/ping")
async def ping():
    return {"route": "playlist", "status": "ok"}