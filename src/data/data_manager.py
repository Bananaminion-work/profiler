from src.data.data_store import DataStore
from src.shared.data_composition import DataComposition
from src.shared.data_models import Data
from src.data.creator import Creator
from pandas import DataFrame
from datetime import datetime
from src.shared.upload_container import UploadContainer

class DataManager():
    
    _creator: Creator
    _measurementObjects:dict[str, Data]
    _dateTime: datetime
    _description: str = ""
    
    def __init__(self):
        self._creator = Creator()
        self._store = DataStore()
        
    def create_data_from_measurement(self,uploadContainer: UploadContainer, source:str):
        self._measurementObjects,self._dateTime,self._description = self._creator.create_data_objects(uploadContainer, source)
        return self._measurementObjects,self._dateTime,self._description
        
    def get_measurement_objects(self)->dict[str,Data]:
        return self._measurementObjects
    
    def scope_data_single(self, preset:str):
        """Return a DataFrame with the data for the given preset, or an empty DataFrame if no measurement is loaded"""
        return self._store.get_scoped_data_single(preset)
    
    def scope_data_multiple(self, preset:str)->dict[str, DataFrame]:
        """Return a dict of DataFrames with the data for the given preset, or an empty DataFrame if no measurement is loaded"""
        return self._store.get_scoped_data_multiple(preset)
    
    
    
    @property
    def current_import_measurement(self) -> DataComposition:
        return self._store.current_import_measurement
    
    @property
    def current_gold_data_for_plot(self) -> dict[str, DataFrame]:
        return self._store.current_gold_data_for_plot
    
    @property
    def current_gold_zeropoints(self):
        return self._store.current_gold_zeropoints
    
    @property
    def measurement_ids(self) -> set:
        return self._store.measurement_ids
    
    @property
    def measurement_name_mapping(self) -> dict[str,str]:
        return self._store.measurement_name_mapping
    
    @property
    def fileName(self) -> str:
        return self._store.fileName
    
    
    @current_import_measurement.setter
    def current_import_measurement(self, composition: DataComposition):
        self._store.current_import_measurement = composition
        
    @current_gold_data_for_plot.setter
    def current_gold_data_for_plot(self, data: dict[str, DataFrame]):
        self._store.current_gold_data_for_plot = data
        
    @current_gold_zeropoints.setter
    def current_gold_zeropoints(self, zeropoints):
        self._store.current_gold_zeropoints = zeropoints
        
    @measurement_ids.setter
    def measurement_ids(self, ids: set):
        self._store.measurement_ids = ids
        
    @measurement_name_mapping.setter
    def measurement_name_mapping(self, mapping: dict[str,str]):
        self._store.measurement_name_mapping = mapping

    @fileName.setter
    def fileName(self, name: str):
        self._store.fileName = name
        
        
    def reset(self):
        """resets the current session data"""
        self._store.current_import_measurement = DataComposition()
        self._store.current_gold_data_for_plot = {}
        self._store.current_gold_zeropoints = {}
        self._store.measurement_ids = set()
        self._store.measurement_name_mapping = {}
        self._store.fileName = ""