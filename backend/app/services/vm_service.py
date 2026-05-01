from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.virtual_machine import VirtualMachine


async def allocate_vm(session: AsyncSession, user_id: str) -> VirtualMachine | None:
    """
    Allocate a free VM to the user.
    Returns the VM if one is available, otherwise None.
    """
    result = await session.execute(
        select(VirtualMachine)
        .where(
            VirtualMachine.current_user_id.is_(None),
            VirtualMachine.is_active.is_(True),
        )
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    vm = result.scalar_one_or_none()

    if vm is None:
        return None

    vm.current_user_id = user_id
    vm.last_used_at = datetime.now(timezone.utc)
    session.add(vm)
    await session.flush()
    return vm


async def release_vm(session: AsyncSession, user_id: str) -> bool:
    """
    Release any VMs currently held by the user.
    Returns True if a VM was released, False otherwise.
    """
    result = await session.execute(
        select(VirtualMachine).where(VirtualMachine.current_user_id == user_id)
    )
    vm = result.scalar_one_or_none()

    if vm is None:
        return False

    vm.current_user_id = None
    session.add(vm)
    await session.flush()
    return True


async def get_user_vm(session: AsyncSession, user_id: str) -> VirtualMachine | None:
    """Get the VM currently allocated to the user, if any."""
    result = await session.execute(
        select(VirtualMachine).where(VirtualMachine.current_user_id == user_id)
    )
    return result.scalar_one_or_none()
