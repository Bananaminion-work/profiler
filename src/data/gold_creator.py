# MUSS NOCH GELÖSCHT WERDEN; IST NUR FÜR TESTING DABEI !!!!!
from nicegui import ui

from pandas import DataFrame
from src.shared.data_models import GoldData, SilverData, Data
from src.shared.exceptions import WrongInputError

class GoldCreator():
    def __init__(self):
        pass    
    
    def create_gold_object_multiple(self, silver: SilverData)->GoldData:
        if isinstance(silver, SilverData): 
            ui.notify("call of function create_gold_object_multiple successful")
            return GoldData(DataFrame())
        else:
            raise WrongInputError("Expected SilverData as input for silver parameter")
    
    def create_gold_data_final(self, gold: Data, chosenZeropoints: dict[str,DataFrame])->GoldData:
        if isinstance(gold, GoldData):
            ui.notify("call of function create_gold_data_final successful")
            return GoldData(DataFrame())
        
        else:
            raise WrongInputError("Expected GoldData as input for gold parameter")