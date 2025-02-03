import ui
import aiohttp

async def OllamaOnline(session: aiohttp.ClientSession, origin: str) -> bool:
    ollama_online = False
    async with ui.loading.LoadingCircle("Testing Origin") as status:
        try:
            response = await session.get(origin)
            ollama_online = await response.text() == "Ollama is running"
        except Exception as e:
            pass
        if not ollama_online: await status.fail()
        else: await status.success()
    return ollama_online
