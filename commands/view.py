import humanize
import ui

async def ListModels(session, config, _1, _2, _3):
    origin = config.get_value("origin")
    async with ui.loading.LoadingCircle("Fetching models list") as status:
        response = await session.get(f"{origin}/api/tags")
        if response.status != 200: await status.fail()
        else: await status.success()
    if response.status != 200:
        print(ui.colors.colorize(f"\rorigin: <fg_red>{response.status}"))
        return
    print(ui.colors.colorize(f"\rorigin: <fg_blue>\\<json object\\>"))
    models = (await response.json())['models']
    maxnamelen, maxverlen = 0, 0
    for model in models:
        name, version = model["model"].split(":")
        maxnamelen, maxverlen = max(len(name), maxnamelen), max(len(version), maxverlen)
    print(f"{' '*(maxnamelen-4)}NAME\t{' '*(maxverlen-3)}TAG\t  SIZE\t  DIGEST")
    models = sorted(models, key=lambda mdl: mdl["model"])
    for model in models:
        name, version = model["model"].split(":")
        print(f"{' '*(maxnamelen-len(name))}{name}\t", end='')
        print(f"{' '*(maxverlen-len(version))}{version}\t", end='')
        print(f"{humanize.naturalsize(model['size'])}\t", end='')
        print(f"{model['digest'][0:8]}")

async def ListRunningModels(session, config, _1, _2, _3):
    origin = config.get_value("origin")
    async with ui.loading.LoadingCircle("Fetching running models list") as status:
        response = await session.get(f"{origin}/api/ps")
        if response.status != 200: await status.fail()
        else: await status.success()
    if response.status != 200:
        print(ui.colors.colorize(f"\rorigin: <fg_red>{response.status}"))
        return
    print(ui.colors.colorize(f"\rorigin: <fg_blue>\\<json object\\>"))
    models = (await response.json())['models']
    maxnamelen, maxverlen = 0, 0
    for model in models:
        name, version = model["model"].split(":")
        maxnamelen, maxverlen = max(len(name), maxnamelen), max(len(version), maxverlen)
    print(f"{' '*(maxnamelen-4)}NAME\t{' '*(maxverlen-3)}TAG\t  SIZE\t  VRAM\t  DIGEST")
    models = sorted(models, key=lambda mdl: mdl["model"])
    for model in models:
        name, version = model["model"].split(":")
        print(f"{' '*(maxnamelen-len(name))}{name}\t", end='')
        print(f"{' '*(maxverlen-len(version))}{version}\t", end='')
        print(f"{humanize.naturalsize(model['size'])}\t", end='')
        print(f"{humanize.naturalsize(model['size_vram'])}\t", end='')
        print(f"{model['digest'][0:8]}")

async def ShowModel(session, config, _1, _2, args):
    origin = config.get_value("origin")
    name = args[0]
    async with ui.loading.LoadingCircle("Fetching model data") as status:
        response = await session.post(f"{origin}/api/show", json={"model": name})
        if response.status != 200: await status.fail()
        else: await status.success()
    if response.status != 200:
        print(f"Failed to get model data")
        print(f"origin: {(await response.json())['error']}")
        # print(f"origin: {await response.text()}")
        return
    print("origin: <json object>")
    data = (await response.json())
    details = data['details']
    print(f"-- {name} --")
    print(f"  Family: {details['family']}")
    print(f"  Format: {details['format']}")
    print(f"  Parameter size: {details['parameter_size']}")
    print(f"  Quantization level: {details['quantization_level']}")
    print(f"  Modified at: {data['modified_at']}")
