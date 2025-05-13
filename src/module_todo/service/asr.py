import json
import aiofiles
from fastapi import Query, WebSocket, APIRouter
from fastapi.responses import HTMLResponse

# self
from config.server import app
from config.log import logger

router = APIRouter()

async def ASRService(
    websocket: WebSocket,
    samplerate: int = 16000,
):
    pass

    
