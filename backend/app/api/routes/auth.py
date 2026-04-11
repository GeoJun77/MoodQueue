from fastapi import APIRouter

# APIRouter is a "mini FastAPI app". We group related routes
# here, then plug them into main.py with include_router().
# This keeps the code modular and easy to navigate.
router = APIRouter()

# Temporary placeholder — will be replaced in step 4
@router.get("/ping")
async def ping():
    return {"route": "auth", "status": "ok"}