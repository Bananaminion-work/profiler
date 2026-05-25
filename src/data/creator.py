from src.data.bronze_creator import BronzeCreator
from src.data.silver_creator import SilverCreator
from src.data.gold_creator import GoldCreator
from src.shared.data_models import Data
from datetime import datetime


from src.shared.upload_container import UploadContainer


class Creator():
    
    _bronzeCreator: BronzeCreator
    _silverCreator: SilverCreator
    _goldCreator: GoldCreator
    _dateTime: datetime
    
    def __init__(self):
        self._bronzeCreator = BronzeCreator()
        self._silverCreator = SilverCreator()
        self._goldCreator = GoldCreator()
        self._dateTime = datetime.now()
    
    def create_data_objects(self,uploadContainer: UploadContainer, source:str)->tuple[dict[str,Data], datetime]:
        """takes in the zip content and source of measurement to process and create 
        all data obejcts (bronze, silver, gold) and returns them in a dict"""
        
        dataObjects = dict[str,Data]()
        
        dataObjects["bronze"] = self._bronzeCreator.create_bronze_object(uploadContainer, source)
        dataObjects["silver"],self._dateTime = self._silverCreator.create_silver_object(dataObjects["bronze"],source)
        dataObjects["gold"] = self._goldCreator.create_gold_object(dataObjects["silver"],source)
            
        return dataObjects, self._dateTime