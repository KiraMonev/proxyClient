from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    ChangePasswordRequest,
    MessageResponse,
    UserProfile,
)
from app.services.auth_service import hash_password, verify_password
from app.services.key_service import set_user_activation_key
from app.tasks.email_tasks import send_activation_email

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile information."""
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Change the current user's password."""
    if data.new_password != data.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match",
        )

    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    current_user.password_hash = hash_password(data.new_password)
    session.add(current_user)
    await session.flush()

    return MessageResponse(message="Пароль успешно изменён")


@router.post("/refresh-key", response_model=MessageResponse)
async def refresh_key(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Generate a new activation key and send it via email."""
    key = await set_user_activation_key(session, current_user)

    send_activation_email.delay(current_user.email, key)

    return MessageResponse(message="Новый ключ активации отправлен на вашу почту")
