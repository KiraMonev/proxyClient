import uuid

from pydantic import BaseModel


class VMInfo(BaseModel):
    """VM info returned after successful key activation."""

    id: uuid.UUID
    name: str
    host: str
    port: int
    protocol: str

    model_config = {"from_attributes": True}


class ActivateKeyRequest(BaseModel):
    activation_key: str


class ActivateKeyResponse(BaseModel):
    message: str
    user_id: uuid.UUID
    vm: VMInfo


class ConnectionStatus(BaseModel):
    """WebSocket message format."""

    status: str  # connected, disconnected, no_free_vms, error
    vm: VMInfo | None = None
    message: str | None = None
