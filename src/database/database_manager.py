from dataclasses import asdict

from pandas import DataFrame
from src.database.measurement_repository import MeasurementRepository, MeasurementRepoCsv, MeasurementRepoDatabricks
from src.database.metadata_repository import MetadataRepository, MetadataRepoCsv, MetadataRepoDatabricks
from src.database.vvt_repositorys import VvtRepoCsv, VvtRepoDatabricks, VvtRepository
from src.shared.data_composition import DataComposition
from nicegui import ui

from src.shared.data_models import BronzeData, Data
from src.shared.exceptions import DataError, WrongInputError

class DatabaseManager:
    
    _vvtRepository : VvtRepository
    _measurementRepository : MeasurementRepository
    _metadataRepository : MetadataRepository
    
    def __init__(self,source: str):
        
        # create repos object based on source parameter
        if source == "csv":
            self._vvtRepository = VvtRepoCsv()
            self._measurementRepository = MeasurementRepoCsv()
            self._metadataRepository = MetadataRepoCsv()
        elif source == "databricks":
            self._vvtRepository = VvtRepoDatabricks()
            self._measurementRepository = MeasurementRepoDatabricks()
            self._metadataRepository = MetadataRepoDatabricks()
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
        
        measurement_id :str = ""
        
        metadata = measurement.get_metadata()
        
        medallionData = measurement.get_medallion_data()
        bronze = medallionData["bronze"]
        silver = medallionData["silver"]
        gold = medallionData["gold"]
        
        if isinstance(asdict(metadata), dict):
            measurement_id = self._metadataRepository.save_measurement_metadata(metadata)
            
        else: 
            raise WrongInputError(f"Metadata should be a dictionary, got {type(metadata)} instead.")
        
        
        if measurement_id != "" and isinstance(bronze, Data) and isinstance(silver, Data) and isinstance(gold, Data):
            self._measurementRepository.add_measurement(measurement_id,medallionData)
            
        else:
            raise DataError(f"Measurement data is not as expected. Measurement ID: {measurement_id}, Bronze type: {type(bronze)}, Silver type: {type(silver)}, Gold type: {type(gold)}.")
        
    
    def load_vvt(self)-> DataFrame:
        """loads the vvt from the database"""
        
        # returns the whole vvt table
        return self._vvtRepository.load_vvt()