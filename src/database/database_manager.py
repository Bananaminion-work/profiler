from dataclasses import asdict
import uuid

from pandas import DataFrame
from src.database.measurement_repository import MeasurementRepository, MeasurementRepoCsv, MeasurementRepoDatabricks
from src.database.metadata_repository import MetadataRepository, MetadataRepoCsv, MetadataRepoDatabricks
from src.database.vvt_repositorys import VvtRepoCsv, VvtRepoDatabricks, VvtRepository
from src.shared.data_composition import DataComposition
from nicegui import ui

from src.shared.data_models import Data, GoldData
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
        
        # create unique id
        measurement_id = str(uuid.uuid4())
        
        # get metadata
        metadata = measurement.get_metadata()
        
        # get medalliondata
        medallionData = measurement.get_medallion_data()
        bronze = medallionData["bronze"]
        silver = medallionData["silver"]
        gold = medallionData["gold"]
        
        # check if data objects are valid
        if not(isinstance(bronze, Data) and isinstance(silver, Data) and isinstance(gold, Data)):
            raise WrongInputError(f"Medallion data should be of type Data, got Bronze: {type(bronze)}, Silver: {type(silver)}, Gold: {type(gold)} instead.")
        
        # check if metadata is valid
        if not isinstance(asdict(metadata), dict):
            raise WrongInputError(f"Metadata should be a dictionary, got {type(metadata)} instead.")
        
        # save data to the database
        self._measurementRepository.add_measurement(measurement_id,medallionData)
        self._metadataRepository.save_measurement_metadata(metadata, measurement_id)
        
    
    
    def load_vvt(self)-> DataFrame:
        """loads the vvt from the database"""
        
        # returns the whole vvt table
        return self._vvtRepository.load_vvt()
    
    def list_saved_measurements(self):
        """lists all saved measurements in the database"""
        return self._metadataRepository.get_saved_measurements()
    
    def get_gold_data_by_id(self, measurement_ids: set):
        """retrieves gold data for a given measurement id"""
        
        #load all gold data for given ids
        goldDfLong = self._measurementRepository.get_gold_data_by_id(measurement_ids)
        
        # change format to wide for easier use in the plots
        goldDfWide = goldDfLong.pivot_table(
            index=['measurement_id','ReadTime'],
            columns='channel',
            values='value'
            ).reset_index()
        
        # split the df according to the measurement_id
        measurementsDict = {}
        
        # create dict with measurement_id as key and corresponding gold data as value
        for id, groupDf in goldDfWide.groupby('measurement_id'):
            
            # remove m_id as column and set ReadTime as index for easier use in plots
            cleanDf = groupDf.drop(columns=['measurement_id']).set_index('ReadTime')
            # fill the dict
            measurementsDict[id] = cleanDf
            
        return measurementsDict