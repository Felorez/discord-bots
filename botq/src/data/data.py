import os

import json

class Data:
    __slots__ = ("__file",)
    
    def __init__(self)  -> None:
        with open(f"{os.path.abspath('src/data/config.json')}", "r") as file:
            self.__file = json.load(file)
            
    @property
    def file(self):
        return self.__file      
    
    @property
    def staff(self):
        with open(f"{os.path.abspath('src/data/text/staff.json')}", "rb") as file:
            self.__file = json.load(file)
            
        return self.__file

    # def __new__(cls) -> any:
    #     return cls.file
    
config = Data().file