import aiohttp
import asyncio
import humanize
import json

from gllama import ui

async def PullModel(session, config, _1, _2, args):
    origin = config.get_value("origin")
    name = args[0]
    async with ui.loading.LoadingCircle("Preparing") as status:
        response = await session.post(f"{origin}/api/pull", json={"model": name})
        if response.status != 200:
            await status.fail()
            print(ui.colors.colorize("origin: <fg_red>failed to initialize pull"))
            return
        msg = json.loads((await response.content.readline()).decode()[:-1])
        print(ui.colors.colorize(f"\rorigin: <fg_blue>{msg['status']}"))
        msg = json.loads((await response.content.readline()).decode()[:-1])
        if msg.get("error"):
            await status.fail()
            print(ui.colors.colorize(f"origin: <fg_red>{msg.get('error')}"))
            return
        await status.success()

    async with ui.loading.LoadingBar("Pulling model", 50) as status:
        status.formatter = lambda done, total: humanize.naturalsize(done)+"/"+humanize.naturalsize(total)
        while True:
            try:
                msg = json.loads((await response.content.readline()).decode()[:-1])
            except aiohttp.client_exceptions.ClientPayloadError:
                status.fail()
                print(ui.colors.colorize("origin: <fg_red>pipe broken"))
                return
            except asyncio.TimeoutError:
                print(ui.colors.colorize(f"\rorigin: <fg_blue>read timeout"))
                continue

            if msg.get("error"):
                await status.fail()
                print(ui.colors.colorize(f"origin: <fg_red>{msg.get('error')}"))
                return

            if not msg.get("total"):
                await status.success()
                break
            status.set_progress(msg.get('completed', 0))
            status.set_total(msg['total'])
    
    async with ui.loading.LoadingCircle("Finishing") as status:
        was = ""
        cnt = b""
        while True:
            cnt = cnt + await response.content.readline()
            try:
                msg = json.loads(cnt.decode()[:-1])
            except json.JSONDecodeError:
                if cnt != b'': continue
                await status.fail()
                print(ui.colors.colorize("origin: <fg_red>unknown error"))
                break
            cnt = b""
            if was == msg["status"]: continue
            was = msg["status"]
            if msg["status"] == "success":
                await status.success()
                break
            print(ui.colors.colorize(f"\rorigin: <fg_blue>{msg['status']}"))
