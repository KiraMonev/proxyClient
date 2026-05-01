from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.virtual_machine import (
    ActivateKeyRequest,
    ActivateKeyResponse,
    VMInfo,
)
from app.schemas.user import MessageResponse
from app.services.key_service import consume_activation_key, validate_activation_key
from app.services.vm_service import allocate_vm, release_vm

router = APIRouter(prefix="/api/proxy", tags=["Proxy"])


@router.post("/activate", response_model=ActivateKeyResponse)
async def activate_key(
    data: ActivateKeyRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Activate a key and allocate a free VM to the user.
    """
    user = await validate_activation_key(session, data.activation_key)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired activation key",
        )

    await consume_activation_key(session, user)

    vm = await allocate_vm(session, str(user.id))
    if vm is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Все прокси-серверы заняты. Попробуйте позже.",
        )

    return ActivateKeyResponse(
        message="Подключение установлено",
        user_id=user.id,
        vm=VMInfo.model_validate(vm),
    )


@router.post("/disconnect", response_model=MessageResponse)
async def disconnect(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Disconnect the current user from their allocated VM."""
    released = await release_vm(session, str(current_user.id))
    if not released:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not connected to any proxy server",
        )

    return MessageResponse(message="Отключено от прокси-сервера")
