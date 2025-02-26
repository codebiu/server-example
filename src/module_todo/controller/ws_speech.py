from fastapi import Query, WebSocket, APIRouter
from fastapi.responses import HTMLResponse

# self
from config.server import app
from config.log import logger
from module_todo.service.asr import ASRService

router = APIRouter()


@router.websocket("/sherpa")
async def asr_sherpa(
    websocket: WebSocket,
    samplerate: int = 16000,
):
    await websocket.accept()
    asr_service = ASRService()
    message = await websocket.receive()  # 获取原始消息
    # async def task_recv_pcm():
    #     while True:
    #         pcm_bytes = await websocket.receive_bytes()
    #         if not pcm_bytes:
    #             return
    #         await asr_stream.write(pcm_bytes)

    # async def task_send_result():
    #     while True:
    #         result: ASRResult = await asr_stream.read()
    #         if not result:
    #             return
    #         await websocket.send_json(result.to_dict())

    # try:
    #     await asyncio.gather(task_recv_pcm(), task_send_result())
    # except WebSocketDisconnect:
    #     logger.info("asr: disconnected")
    # finally:
    #     await asr_stream.close()
    
@router.websocket("/tts_sherpa")
async def tts_sherpa(websocket: WebSocket,
                        samplerate: int = Query(16000,
                                                title="Sample Rate",
                                                description="The sample rate of the generated audio."),
                        interrupt: bool = Query(True,
                                                title="Interrupt",
                                                description="是否中断当前语音"),
                        sid: int = Query(0,
                                         title="Speaker ID",
                                         description="The ID of the speaker to use for TTS."),
                        chunk_size: int = Query(1024,
                                                title="Chunk Size",
                                                description="The size of the chunk to send to the client."),
                        speed: float = Query(1.0,
                                             title="Speed",
                                             description="The speed of the generated audio."),
                        split: bool = Query(True,
                                            title="Split",
                                            description="Split the text into sentences.")):
    await websocket.accept()
    asr_service = ASRService()
    
app.include_router(router, prefix="/ws_speech", tags=["实时音频处理"])
    

