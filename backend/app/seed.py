"""
Seed script
Run inside the backend container:
    python -m app.seed
"""

import asyncio

from sqlalchemy import select

from app.database import async_session
from app.models.virtual_machine import VirtualMachine

SEED_VMS = [
    {
        "name": "proxy-1",
        "host": "192.168.1.10",
        "port": 1080,
        "protocol": "socks5",
        "is_active": True,
    },
    {
        "name": "proxy-2",
        "host": "192.168.1.11",
        "port": 8080,
        "protocol": "http",
        "is_active": True,
    },
]


async def seed():
    async with async_session() as session:
        result = await session.execute(select(VirtualMachine))
        existing = result.scalars().all()

        if existing:
            print(f"Database already has {len(existing)} VMs. Skipping seed.")
            return

        for vm_data in SEED_VMS:
            vm = VirtualMachine(**vm_data)
            session.add(vm)

        await session.commit()
        print(f"Seeded {len(SEED_VMS)} virtual machines.")


if __name__ == "__main__":
    asyncio.run(seed())
