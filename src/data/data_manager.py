from src.shared.data_models import Data, GoldData
from src.data.creator import Creator
from pandas import DataFrame
from src.shared.exceptions import NoDataToWorkWithError
from src.shared.upload_container import UploadContainer


class DataManager():
    
    _creator: Creator
    _measurementObjects:dict[str, Data]
    
    def __init__(self):
        self._creator = Creator()
        
    def create_data_from_measurement(self,uploadContainer: UploadContainer, source:str):
        self._measurementObjects = self._creator.create_data_objects(uploadContainer, source)
        return self._measurementObjects
        
    def create_final_data(self,chosenZeropoints: dict[str,DataFrame]):
        gold = self._measurementObjects.get("gold")
        if gold is not None:
            self._measurementObjects["gold"] = self._creator.get_final_gold_object(gold, chosenZeropoints)
        else:
            raise NoDataToWorkWithError("Gold data object is missing, cannot create final gold data.")
        
        return self._measurementObjects["gold"]
        
    def get_measurement_objects(self)->dict[str,Data]:
        return self._measurementObjects