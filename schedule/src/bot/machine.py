import os

import asyncio
import datetime

import hikari
import lightbulb
import miru

from ..data.data import config

class Bot(lightbulb.BotApp):
    def __init__(self):
        self.__config = {
            "token": os.environ.get("TOKEN"), 
            "default_enabled_guilds": config["guilds"]["main"],
            "intents": hikari.Intents.ALL
        }
        
        super().__init__(**self.__config)
        
        self.__banner= {
            "banner": "src",
            "allow_color": 0,
            "force_color": 0
        }
        
        super().print_banner(**self.__banner)
    
bot = Bot()

client = miru.Client(
    bot,
    ignore_unknown_interactions = True
)


