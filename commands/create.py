import aiohttp
import json
import ui

from util import digest

async def QuantizeModel(session, config, _1, _2, args):
    origin = config.get_value("origin")
    from_model, name, level = args[0], args[1], args[2]
    async with ui.loading.LoadingCircle("Quantizing model") as status:
        response = await session.post(f"{origin}/api/create", json={"model": name,
                                                                    "from": from_model,
                                                                    "quantize": level})
        if response.status != 200:
            await status.fail()
            print(ui.colors.colorize(f"origin: <fg_red>{(await response.json())['error']}"))
            return

        was = ""
        while True:
            msg = json.loads((await response.content.readline()).decode()[:-1])
            if msg.get("error"):
                await status.fail()
                print(ui.colors.colorize(f"origin: <fg_red>{msg.get('error')}"))
                break
            if was == msg["status"]: continue
            was = msg["status"]
            if msg["status"] == "success":
                await status.success()
                break
            print(ui.colors.colorize(f"\rorigin: <fg_blue>{msg['status']}"))

def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"
    return "".join(safe_char(c) for c in s).rstrip("_")

async def put_blob(session, config, blob_path):
    origin = config.get_value("origin")
    file = open(blob_path, 'rb')
    async with ui.loading.LoadingCircle(f"Pushing blob") as status:
        file_digest = await digest.sha256(file)
        print(f"\rblob digest is {file_digest}")
        response = await session.head(f"{origin}/api/blobs/sha256:{file_digest}")
        if response.status == 200:
            await status.success()
            print(ui.colors.colorize(f"origin: <fg_blue>blob {file_digest} already exists"))
            return True, file_digest
        file.seek(0)
        response = await session.post(f"{origin}/api/blobs/sha256:{file_digest}", data=file)
        if response.status != 201:
            await status.fail()
            print(ui.colors.colorize(f"origin: <fg_red>{(await response.json())['error']}"))
            return False, None
        await status.success()
        print(ui.colors.colorize(f"origin: <fg_blue>blob {file_digest} created"))
    return True, file_digest

async def CreateGGUF(session, config, _1, _2, args):
    origin = config.get_value("origin")
    name, path = args[0], args[1]
    success, file_digest = await put_blob(session, config, path)
    if not success: return
    async with ui.loading.LoadingCircle("Creating model") as status:
        response = await session.post(f"{origin}/api/create", json={"model": name,
                                                                    "files": {
                                                                        make_safe_filename(f"model_{name}.gguf"): "sha256:"+file_digest
                                                                    }})
        if response.status != 200:
            await status.fail()
            print(ui.colors.colorize(f"origin: <fg_red>{(await response.json())['error']}"))
            return
        
        was = ""
        while True:
            msg = json.loads((await response.content.readline()).decode()[:-1])
            if msg.get("error"):
                await status.fail()
                print(ui.colors.colorize(f"origin: <fg_red>{msg.get('error')}"))
                break
            if was == msg["status"]: continue
            was = msg["status"]
            if msg["status"] == "success":
                await status.success()
                break
            print(ui.colors.colorize(f"\rorigin: <fg_blue>{msg['status']}"))
