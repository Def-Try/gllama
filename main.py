import readline
import logging
import aiohttp
import asyncio
import sys
import os

if os.path.exists("data/log.log"):
    os.remove("data/log.log")
logger = logging.getLogger("gllama")
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)7s] %(message)s",
    handlers=[
        logging.FileHandler("data/log.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

import config
origin = config.get_value("origin")
logging.info(f"Origin is {origin}")

import ui
import util
import commands

async def main(session: aiohttp.ClientSession):


    ollama_online = await util.checks.OllamaOnline(session, origin)
    if not ollama_online:
        print("Ollama is offline on the origin server!")

    handler = ui.CommandHandler()

    handler.register("list",    "",
                     "List available models",       commands.ListModels)
    handler.register("running", "",
                     "List running models",         commands.ListRunningModels)
    handler.register("show",    "<model>",
                     "Show model data",             commands.ShowModel)
    
    handler.register("pull",   "<model>",
                     "Download model from library", commands.PullModel)
    handler.register("delete", "<model>",
                     "Delete model",                commands.DeleteModel)
    handler.register("copy",   "<source> <destination>",
                     "Copy model",                  commands.CopyModel)
    
    handler.register("create_gguf", "<name> <path>",
                     "Create model from GGUF",      commands.CreateGGUF)
    handler.register("quantize",    "<from> <name> <level>",
                     "Quantize a model",            commands.QuantizeModel)

    handler.register("run",  "<model>",
                     "Run model",                   commands.RunModel)
    handler.register("embed", "<model>",
                     "Run embedding model",         commands.RunEmbeddingModel)
    handler.register("chat", "<model>",
                     "Run chat model",              commands.RunChatModel)

    handler.alias("ls", "list")
    handler.alias("ps", "running")
    handler.alias("rm", "delete")
    handler.alias("cp", "copy")

    await handler.start(session, config)

    print("Bye!")
    logger.info("User exit")

async def __entry():
    async with aiohttp.ClientSession() as session:
        await main(session)

asyncio.run(__entry())
