import asyncio
import traceback
import aiohttp
import ui

class CommandHandler:
    def __init__(self):
        self.commands = {}
        self.aliases = {}

    @staticmethod
    async def __unknown_handler(s, c, cmd, a, args):
        print(f"Unknown command: {cmd}")

    async def __help_handler(self, ss, cf, cm, ag, args):
        print("Help")
        maxstartlen = 0
        for cmd, data in self.commands.items():
            maxstartlen = max(len(f"{cmd}{' '+data[1] if data[1] != '' else ''}"), maxstartlen)
        for cmd, data in self.commands.items():
            start = f"{cmd}{' '+data[1] if data[1] != '' else ''}"
            print(f" {start}{' '*(maxstartlen-len(start))} - {data[0]}")

    def register(self, cmd, args, desc, handler):
        self.commands[cmd] = [desc, args, handler]

    def alias(self, alias, cmd):
        self.aliases[alias] = cmd

    @staticmethod
    def parse_args(arglst, argstr):
        args = []
        handling = [False, None]
        for ch in arglst.strip():
            if ch == "<" or ch == "[":
                if handling[0]:
                    raise Exception(f"Argument #{len(args)+1} was never closed")
                handling = [True, ""]
            if handling[0]:
                handling[1] = handling[1]+ch
            if ch == ">" or ch == "]":
                if not handling[0]:
                    raise Exception(f"Stray argument close after #{len(args)}")
                args.append(handling[1])
                handling = [False, None]
        if handling[0]:
            raise Exception(f"Argument #{len(args)+1} was never closed")
        
        required = 0

        req_done = False
        full_cap_found = False
        for arg in args:
            if full_cap_found:
                raise Exception(f"Another argument after full capture argument")
            if arg[0] == "[":
                req_done = True
            if arg[0] == "<" and req_done:
                raise Exception("Required argument came after optional argument")
            if arg[-4:-1] == "...":
                full_cap_found = True
            if not req_done:
                required += 1
            
        ptr = 0
        arglist = []
        curarg = ""
        inquote = False
        while ptr < len(argstr):
            ch = argstr[ptr]
            ptr += 1
            if len(arglist) > len(args)-1:
                raise ValueError("Too many arguments")
            if ch == " " and not inquote and args[len(arglist)][-4:-1] != "...":
                arglist.append(curarg)
                curarg = ""
                continue
            if (ch == "\"" or ch == "\'") and args[len(arglist)][-4:-1] != "...":
                inquote = not inquote
                continue
            curarg += ch
        if curarg != "": arglist.append(curarg)

        if len(arglist) < required:
            raise ValueError("Not enough arguments")
        if len(arglist) > len(args):
            raise ValueError("Too many arguments")
        return arglist
                

    async def start(self, session: aiohttp.ClientSession, config):
        self.register("help", "", "Show this message", self.__help_handler)
        while True:
            inp = input(">>> ")
            cmd = inp.split(" ")[0]
            data = self.commands.get(cmd, self.commands.get(self.aliases.get(cmd), ["", "", self.__unknown_handler]))
            argstr = " ".join(inp.split(" ")[1:])
            try:
                args = self.parse_args(data[1], argstr) if data[1] != "" else [argstr]
            except ValueError as e:
                print(ui.colors.colorize(f"{cmd}: <fg_red>{e}"))
                continue

            if cmd in ["quit", "q", "exit"]: return
            handler = data[2]
            try:
                await handler(session, config, cmd, argstr, args)
            except Exception as e:
                traceback.print_exc()
