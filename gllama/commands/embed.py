import traceback
import asyncio
import json

from gllama import ui

async def RunEmbeddingModel(session, config, _1, _2, args):
    origin = config.get_value("origin")
    model = args[0]
    try:
        print(ui.colors.colorize("origin: <fg_blue>ready"))
        print("Welcome to Embedding UI.")
        print("Run /help to show list of all commands")
        params = {}
        while True:
            inp = input("> ")
            if inp.startswith("/"):
                inp = inp.strip()
                if inp == "/help":
                    print("Help")
                    print(" /set <parameter> [value] - Set model parameter")
                    print("                            Run with no value to unset")
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
                if inp == "/quit" or inp == "/exit" or inp == "/end":
                    break

            response = await session.post(f"{origin}/api/embed", json={"model": model,
                                                                       "input": inp,
                                                                       "options": params})
            response = await response.json()
            
            if response.get("error"):
                print(ui.colors.colorize(f"origin: <fg_red>{response["error"]}"))
                break

            embeddings = response["embeddings"]
            if len(embeddings) < 1:
                print(ui.colors.colorize(f"origin: <fg_blue>\\<nothing\\>"))
                continue
            embedding = embeddings[0]
            print(ui.colors.colorize(f"origin: <fg_blue>\\<{len(embedding)}-dimensional embedding\\>"))
            for i,val in enumerate(embedding):
                if i % 30 == 0 and i != 0: print()
                val = (val + 1) / 2
                val = val * 256**3
                print(f"\x1b[38;2;{val // 256**2 % 256:0.0f};{val // 256 % 256:0.0f};{val % 256:0.0f}m██", end='')
            print(ui.colors.RESET)
    except BaseException as e:
        traceback.print_exc()

    print("Bye!")
