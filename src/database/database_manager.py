from pandas import DataFrame

import src
from src.database.vvt_repositorys import CsvRepository, DatabricksRepository, VvtRepository
from src.shared.data_composition import DataComposition
from nicegui import ui

class DatabaseManager:
    
    _vvtRepository : VvtRepository
    
    def __init__(self,source: str):
        
        # create repos object based on source parameter
        if source == "csv":
            self._vvtRepository = CsvRepository()
        elif source == "databricks":
            self._vvtRepository = DatabricksRepository()
        else:
            raise ValueError(f"Invalid source '{source}' for VVT repository.")
    
    def connect_to_database(self):
        """connects to the database"""
        ui.notify("function to connect to database was called... wait to be implemented", color="orange")
        
    def disconnect_from_database(self):
        """disconnects from the database"""
        ui.notify("function to disconnect from database was called... wait to be implemented", color="orange")

    def save_measurement(self, measurement: DataComposition):
        """saves the measurement to the database"""
        ui.notify("function to save measurement was called... wait to be implemented", color="orange")
    
    def load_vvt(self)-> DataFrame:
        """loads the vvt from the database"""
        
        # returns the whole vvt table
        return self._vvtRepository.load_vvt()