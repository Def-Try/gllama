from gllama import ui

async def DeleteModel(session, config, _1, _2, args):
    origin = config.get_value("origin")
    name = args[0]
    async with ui.loading.LoadingCircle("Deleting model") as status:
        response = await session.delete(f"{origin}/api/delete", json={"model": name})
        if response.status != 200:
            await status.fail()
            print(ui.colors.colorize("origin: <fg_red>failed to delete model"))
            return
        await status.success()
        print(ui.colors.colorize("origin: <fg_blue>success"))
