from fastapi import APIRouter

router = APIRouter()

# Temporary placeholder — will be replaced in step 6
@router.get("/ping")
async def ping():
    return {"route": "mood", "status": "ok"}