import asyncio
import json
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import async_session
from app.services.vm_service import get_user_vm, release_vm

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/status/{user_id}")
async def websocket_status(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time connection status updates.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for user {user_id}")

    try:
        try:
            UUID(user_id)
        except ValueError:
            await websocket.send_json(
                {"status": "error", "message": "Invalid user ID format"}
            )
            await websocket.close()
            return

        while True:
            async with async_session() as session:
                vm = await get_user_vm(session, user_id)

                if vm is not None:
                    status_data = {
                        "status": "connected",
                        "vm": {
                            "id": str(vm.id),
                            "name": vm.name,
                            "host": vm.host,
                            "port": vm.port,
                            "protocol": vm.protocol,
                        },
                    }
                else:
                    status_data = {
                        "status": "disconnected",
                        "vm": None,
                        "message": "Not connected to any proxy server",
                    }

            await websocket.send_json(status_data)

            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                try:
                    data = json.loads(message)
                    if data.get("action") == "disconnect":
                        async with async_session() as session:
                            await release_vm(session, user_id)
                            await session.commit()
                        await websocket.send_json(
                            {
                                "status": "disconnected",
                                "vm": None,
                                "message": "Disconnected from proxy server",
                            }
                        )
                except (json.JSONDecodeError, KeyError):
                    pass  # Ignore invalid messages

            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
        async with async_session() as session:
            await release_vm(session, user_id)
            await session.commit()
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        try:
            await websocket.send_json(
                {"status": "error", "message": "Internal server error"}
            )
        except Exception:
            pass
