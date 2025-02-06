import re
import math
import asyncio
from .colors import tag_to_text, RESET

ansi_escape_8bit = re.compile(
    r'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
)

class Typewriter():
    def __init__(self):
        self.stages = "⣾⣽⣻⢿⡿⣟⣯⣷" # "●⬤"
        self.tick = 0

        self.add = ""
        self.previous = ""

    async def put(self, text, put_color=True):
        printfull = ""
        if '\n' in text:
            text += '\n'
            split = text.split("\n")
            printfull = "\n".join(split[:-1])
            text = split[-1]

        self.previous = self.add
        self.add = text
        
        print("\b\b\b   \b\b\b", end='')
        print("\b"*len(ansi_escape_8bit.sub('', self.previous)), end='')
        print(self.previous, end='')
        print(printfull, end='')
        if put_color:
            print(tag_to_text("bright_blue")+self.add+RESET, end='')
        else:
            print(self.add, end='')
        print(f" {self.stages[math.floor(self.tick)]} ", end='', flush=True)

    async def __aenter__(self):
        self.task = asyncio.create_task(self.__aiter__())
        print("   ", end='', flush=True)
        return self
    async def __aexit__(self, *args):
        self.task.cancel()
        await self.put("", False)
        print("\b\b\b   ")
    async def __aiter__(self):
        while True:
            print(f"\b\b\b {self.stages[math.floor(self.tick)]} ", end='', flush=True)
            self.tick += 0.1
            self.tick %= len(self.stages)
            await asyncio.sleep(0.05)