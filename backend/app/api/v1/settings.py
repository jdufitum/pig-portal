from fastapi import APIRouter, Depends

from ...config import settings
from ...deps import get_current_user
from ...schemas.settings import OwnerSettingsOut


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=OwnerSettingsOut)
def get_owner_settings(_=Depends(get_current_user)):
    return OwnerSettingsOut(app_name=settings.app_name, cors_origins=settings.cors_origins)

