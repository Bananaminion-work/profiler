# MUSS NOCH GELÖSCHT WERDEN; IST NUR FÜR TESTING DABEI !!!!!
from nicegui import ui

from pandas import DataFrame
from src.shared.data_models import Data, BronzeData,  SilverData
from src.shared.exceptions import WrongInputError


class SilverCreator():
    def __init__(self):
        pass
    
    def create_silver_object(self, bronze: Data)->SilverData:
            if isinstance(bronze, BronzeData):
                ui.notify("call of function create_silver_object successful")
                return SilverData(DataFrame())
            else:
                raise WrongInputError("Expected BronzeData as input for bronze parameter")