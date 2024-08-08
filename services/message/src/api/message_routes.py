from typing import Any
from fastapi import Body, APIRouter

from core.message import MessageHandler

router = APIRouter(prefix="/ws")

message_h = MessageHandler()

@router.post("/connect")
async def ws_connect(req: Any = Body(None)):
    print("New connection -> " + req["connectionId"])
    message_h.add_connection(req["connectionId"])
    return {"status": 200}


@router.post("/disconnect")
async def ws_disconnect(req: Any = Body(None)):
    message_h.remove_connection(req["connectionId"])
    return {"status": 200}


@router.post("/unknown")
async def ws_unknown(req: Any = Body(None)):
    print(req)
    return {"status": 404}


@router.post("/send")
async def ws_send(req: Any = Body(None)):
    print("\nAttempting message from " + req["connectionId"])
    message_h.send_to_channel(req["connectionId"], req["payload"]["message"])
    return {"status" : 200}


@router.post("/joinChannel")
async def ws_joinChan(req: Any = Body(None)):
    print(req)
    # join channel takes the unique channel id, the user's email, and the user's connection id
    status = message_h.join_channel(req["payload"]["channel_id"], req["payload"]["user_email"], req["connectionId"])
    return status
