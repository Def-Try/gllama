ESC_START = "\033["
ESC_END =   "m"

RESET = ESC_START+"0"+ESC_END

# +10 for bg, +60 for bright variants
COLORS = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37
}

def tag_to_text(tag):
    if tag == "reset": return RESET
    offset = 0
    if tag.startswith("bg_"):
        offset = 10
        tag = tag[3:]
    if tag.startswith("fg_"):
        offset = 0
        tag = tag[3:]
    if tag.startswith("bright_"):
        offset += 60
        tag = tag[7:]
    return ESC_START+str(COLORS[tag]+offset)+ESC_END


def colorize(string):
    tag = ""
    tagging = False
    result = ""

    lastch = ""
    for ch in string:
        if not tagging and ch == "<" and lastch != "\\":
            tagging = True
            lastch = ch
            continue
        if tagging and ch == ">" and lastch != "\\":
            tagging = False
            result += tag_to_text(tag)
            tag = ""
            lastch = ch
            continue
        if (ch == "<" or ch == ">") and lastch == "\\":
            if tagging:
                tag = tag[:-1]
            else:
                result = result[:-1]
        lastch = ch
        if tagging:
            tag += ch
            continue
        result += ch
    return result + ("<" if tagging else "") + tag + RESET