from src.shared.data_models import Data, GoldData
from src.data.creator import Creator
from pandas import DataFrame
from datetime import datetime
from src.shared.upload_container import UploadContainer


class DataManager():
    
    _creator: Creator
    _measurementObjects:dict[str, Data]
    _dateTime: datetime
    
    def __init__(self):
        self._creator = Creator()
        
    def create_data_from_measurement(self,uploadContainer: UploadContainer, source:str):
        self._measurementObjects,self._dateTime = self._creator.create_data_objects(uploadContainer, source)
        return self._measurementObjects,self._dateTime
        
    def create_final_data(self,chosenZeropoints: dict[str,DataFrame]):
        pass
        
    def get_measurement_objects(self)->dict[str,Data]:
        return self._measurementObjects