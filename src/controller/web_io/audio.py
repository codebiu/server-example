import json
import aiofiles
from fastapi import WebSocket, APIRouter
from fastapi.responses import HTMLResponse

# self
from config.server import app
from config.log import logger

router = APIRouter()


# ########################### htttp


# ########################### ws
