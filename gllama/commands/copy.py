from gllama import ui

async def CopyModel(session, config, _1, _2, args):
    origin = config.get_value("origin")
    src, dst = args[0], args[1]
    async with ui.loading.LoadingCircle("Copying model") as status:
        response = await session.post(f"{origin}/api/copy", json={"source": src, "destination": dst})
        if response.status != 200:
            await status.fail()
            print(ui.colors.colorize("origin: <fg_red>failed to copy model"))
            return
        await status.success()
        print(ui.colors.colorize("origin: <fg_blue>success"))
