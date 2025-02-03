import math
import asyncio
from .colors import tag_to_text, RESET

class LoadingCircle():
    def __init__(self, message):
        self.message = message
        self.stages = "⠇⠋⠙⠸⠴⠦"
        self.tick = 0
        self.status = None
        self.closed = False

    async def success(self):
        self.status = True
        await self.__aexit__()
    async def fail(self):
        self.status = False
        await self.__aexit__()
    async def neutral(self):
        self.status = None
        await self.__aexit__()

    async def __aenter__(self):
        self.task = asyncio.create_task(self.__aiter__())
        return self
    async def __aexit__(self, *args):
        if self.closed: return
        self.closed = True
        self.task.cancel()
        print(f"\r{self.message}"+(
               f" {tag_to_text('green')}✓{RESET}" if self.status == True else
               f" {tag_to_text('red')}✗{RESET}" if self.status == False else
               f" {tag_to_text('blue')}•{RESET}"))
    async def __aiter__(self):
        while True:
            print(f"\r{self.message} {self.stages[math.floor(self.tick)]}", end='', flush=True)
            self.tick += 0.1
            self.tick %= len(self.stages)
            await asyncio.sleep(0.05)

class LoadingBar():
    def __init__(self, message, length):
        self.message = message
        self.stages = "⠇⠋⠙⠸⠴⠦"
        self.tick = 0
        self.status = None
        self.closed = False
        self.length = length

        self.done = 0
        self.total = 1
        self.blocks = ["", "▏","▎","▍","▌","▋","▊","▉","█"]
        self.formatter = lambda done, total: f"{done}/{total}"

    async def success(self):
        self.status = True
        self.done = self.total
        await self.__aexit__()
    async def fail(self):
        self.status = False
        await self.__aexit__()
    async def neutral(self):
        self.status = None
        await self.__aexit__()
    def set_progress(self, done):
        self.done = done
    def set_total(self, total):
        self.total = total
    def __gen_bar(self):
        fmt = self.formatter(self.done, self.total)
        length = self.length - len(fmt) - 2
        value = self.done / self.total
        v = value*length
        x = math.floor(v) # integer part
        y = v - x         # fractional part
        base = 0.125      # 0.125 = 1/8
        prec = 3
        i = int(round(base*math.floor(float(y)/base),prec)/base)
        bar = "█"*x + self.blocks[i]
        n = length-len(bar)
        bar = "▕" + bar + " "*n + "▏"
        bar = bar + fmt
        return bar

    async def __aenter__(self):
        self.task = asyncio.create_task(self.__aiter__())
        return self
    async def __aexit__(self, *args):
        if self.closed: return
        self.closed = True
        self.task.cancel()
        print(f"\r{self.message} {self.__gen_bar()}"+(
               f" {tag_to_text('green')}✓{RESET}" if self.status == True else
               f" {tag_to_text('red')}✗{RESET}" if self.status == False else
               f" {tag_to_text('blue')}•{RESET}"), end='    \n')
    async def __aiter__(self):
        while True:
            print(f"\r{self.message} {self.__gen_bar()} {self.stages[math.floor(self.tick)]}", end='    ', flush=True)
            self.tick += 0.1
            self.tick %= len(self.stages)
            await asyncio.sleep(0.05)
