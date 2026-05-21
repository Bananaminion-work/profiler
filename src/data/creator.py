from src.data.bronze_creator import BronzeCreator
from src.data.silver_creator import SilverCreator
from src.data.gold_creator import GoldCreator
from src.shared.data_models import BronzeData, Data, SilverData 
from pandas import DataFrame

from src.shared.upload_container import UploadContainer


class Creator():
    
    _bronzeCreator: BronzeCreator
    _silverCreator: SilverCreator
    _goldCreator: GoldCreator
    
    def __init__(self):
        self._bronzeCreator = BronzeCreator()
        self._silverCreator = SilverCreator()
        self._goldCreator = GoldCreator()
    
    def create_data_objects(self,uploadContainer: UploadContainer, source:str)->dict[str,Data]:
        """takes in the zip content and source of measurement to process and create 
        all data obejcts (bronze, silver, gold) and returns them in a dict"""
        
        dataObjects = dict[str,Data]()
        
        dataObjects["bronze"] = self._bronzeCreator.create_bronze_object(uploadContainer, source)
        dataObjects["silver"] = self._silverCreator.create_silver_object(dataObjects["bronze"])
        dataObjects["gold"] = self._goldCreator.create_gold_object_multiple(dataObjects["silver"])
            
        return dataObjects
        
    def get_final_gold_object(self, gold: Data, chosenZeropoints: dict[str,DataFrame])->Data:
        return self._goldCreator.create_gold_data_final(gold, chosenZeropoints)