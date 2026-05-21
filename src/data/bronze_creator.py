# MUSS NOCH GELÖSCHT WERDEN; IST NUR FÜR TESTING DABEI !!!!!
from nicegui import ui

from src.shared.data_models import BronzeData, Data
from pandas import DataFrame


class BronzeCreator():
    def __init__(self):
        pass
    
    def create_bronze_object(self,uploadContainer, source:str)->Data:
        ui.notify("call of function create_bronze_object successful")
        return BronzeData(DataFrame())