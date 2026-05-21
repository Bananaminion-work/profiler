from src.shared.data_models import Data, GoldData
from src.data.creator import Creator
from pandas import DataFrame
from src.shared.upload_container import UploadContainer


class DataManager():
    
    _creator: Creator
    _measurementObjects:dict[str, Data]
    
    def __init__(self):
        self._creator = Creator()
        
    def create_data_from_measurement(self,uploadContainer: UploadContainer, source:str):
        self._measurementObjects = self._creator.create_data_objects(uploadContainer, source)
        
    def create_final_data(self,chosenZeropoints: dict[str,DataFrame]):
        gold = self._measurementObjects.get("gold")
        if gold is not None:
            self._measurementObjects["gold"] = self._creator.get_final_gold_object(gold, chosenZeropoints)
        
    def get_measurement_objects(self)->dict[str,Data]:
        return self._measurementObjects