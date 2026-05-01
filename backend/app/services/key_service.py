import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


def generate_activation_key() -> str:
    """Generate a 32-character hex activation key."""
    return secrets.token_hex(16)


async def set_user_activation_key(session: AsyncSession, user: User) -> str:
    """Generate a new activation key for the user, replacing any existing one."""
    key = generate_activation_key()
    user.activation_key = key
    user.activation_key_expires = None
    session.add(user)
    await session.flush()
    return key


async def validate_activation_key(session: AsyncSession, key: str) -> User | None:
    """
    Validate an activation key.
    Returns the User if key is valid, otherwise None.
    """
    result = await session.execute(
        select(User).where(
            User.activation_key == key,
            User.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def consume_activation_key(session: AsyncSession, user: User) -> None:
    """Mark the activation key as used (set to None)."""
    user.activation_key = None
    user.activation_key_expires = None
    session.add(user)
    await session.flush()
