import json
import logging
import typing

logger = logging.getLogger()

def read_config() -> typing.Dict:
    with open("data/config.json", 'r', encoding="utf-8") as configfile:
        return json.load(configfile)
    
def write_config(config: typing.Dict):
    with open("data/config.json", 'w', encoding="utf-8") as configfile:
        json.dump(config, configfile)

config = {}

defaults = {
    "origin": "http://127.0.0.1:11434"
}

try:
    config = read_config()
except json.JSONDecodeError as e:
    logger.error(f"JSON decoding error: {e.msg} at L{e.lineno}C{e.colno}")
except FileNotFoundError:
    logger.warning(f"Config file not found")
    write_config({})

def get_value(key: typing.AnyStr) -> typing.Any:
    return config.get(key, defaults.get(key, None))

def set_value(key: typing.AnyStr, value: typing.Any):
    if value == defaults.get(key, None):
        del config[key]
    else:
        config[key] = value
    write_config(config)
