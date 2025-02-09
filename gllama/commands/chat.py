import traceback
import asyncio
import json

from gllama import ui

async def RunChatModel(session, config, _1, _2, args):
    origin = config.get_value("origin")
    model = args[0]
    async with ui.loading.LoadingCircle("Loading model") as status:
        response = await session.post(f"{origin}/api/chat", json={"model": model})
        if response.status != 200:
            await status.fail()
            print(ui.colors.colorize("origin: <fg_red>failed to load model"))
            return
        await status.success()
        print(ui.colors.colorize("origin: <fg_blue>success"))
    try:
        print(ui.colors.colorize("origin: <fg_blue>ready"))
        print("Welcome to Chat UI.")
        print("Start with \"[clear]\" to clear context before message")
        print("Run /help to show list of all commands")
        messages = []
        params = {}
        while True:
            inp = input("> ")
            if inp.startswith("/"):
                inp = inp.strip()
                if inp == "/help":
                    print("Help")
                    print(" /set <parameter> [value] - Set model parameter")
                    print("                            Run with no value to unset")
                    print(" /clear                   - Clear prompt")
                    print(" /show                    - Show messages")
                    print(" /quit                    - Quit this UI")
                    print(" /exit                    - ^")
                    print(" /end                     - ^")
                    continue
                if inp == "/set":
                    print("Parameter expected, got nothing")
                if inp[:5] == "/set ":
                    namevalue = inp[5:].split(" ")
                    if len(namevalue) == 1:
                        del params[namevalue[0]]
                        print(f"\"{namevalue[0]}\" unset")
                        continue
                    try:
                        params[namevalue[0]] = float(namevalue[1])
                    except ValueError:
                        print("value should be a number")
                        continue
                    print(f"\"{namevalue[0]}\" set to {namevalue[1]}")
                    continue
                if inp == "/clear":
                    print("Context cleared")
                    messages = []
                    continue
                if inp == "/show":
                    print("Context:")
                    print(f"  Total {len(messages)} messages")
                    for message in messages[-5:]:
                        print(ui.colors.colorize(f"<fg_blue>{message['role'].title()}\n")+
                                                 message['content'])
                    continue
                if inp == "/quit" or inp == "/exit" or inp == "/end":
                    break
            if inp.startswith("[clear]"):
                messages = []
                inp = inp[7:]
            messages += [{"role": "user", "content": inp}]

            response = await session.post(f"{origin}/api/chat", json={"model": model,
                                                                      "messages": messages,
                                                                      "options": params})
            messages += [{"role": "assistant", "content": ""}]
            tokens, length = 0, 0
            print(ui.colors.colorize(f"<fg_blue>User<reset>\n{messages[-2]['content'].replace('<', '\\<').replace('>', '\\>')}\n"+
                                     f"<fg_blue>Assistant"))
            async with ui.typewriter.Typewriter() as writer:
                while True:
                    try:
                        msg = json.loads((await response.content.readline()).decode()[:-1])
                    except asyncio.exceptions.CancelledError:
                        print("\b\b", end='') # "^C" here!
                        await writer.put(ui.colors.colorize(f" [<fg_red>INTERRUPTED<reset>]"), False)
                        break
                    except asyncio.TimeoutError:
                        await writer.put(ui.colors.colorize(f" [<fg_red>TIMEOUT<reset>]"), False)
                        break
                    if msg.get("error"):
                        break
                    messages[-1]["content"] += msg["message"]["content"]
                    await writer.put(msg["message"]["content"])
                    if msg.get("done"):
                        break
                    tokens += 1
                    length += len(msg["message"]["content"])
            if msg.get("error"):
                print(ui.colors.colorize(f"origin: <fg_red>{msg["error"]}"))
            else:
                print("="*80)
                print(f"{length} chars\t{tokens} tokens\t{round(msg.get('eval_count', 1) / msg.get('eval_duration', 1) * 10**9, 2)} token/sec")     
    except BaseException as e:
        traceback.print_exc()

    print("Bye!")

    async with ui.loading.LoadingCircle("Unloading model") as status:
        response = await session.post(f"{origin}/api/chat", json={"model": model, "keep_alive": 0})
        if response.status != 200:
            await status.fail()
            print(ui.colors.colorize("origin: <fg_red>failed to unload model"))
            return
        await status.success()
        print(ui.colors.colorize("origin: <fg_blue>success"))
