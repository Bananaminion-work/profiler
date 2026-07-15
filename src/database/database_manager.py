from dataclasses import asdict
import uuid

from pandas import DataFrame
from src.database.databricks_client import DatabricksClient
from src.database.measurement_repository import MeasurementRepository, MeasurementRepoCsv, MeasurementRepoDatabricks
from src.database.metadata_repository import MetadataRepository, MetadataRepoCsv, MetadataRepoDatabricks
from src.database.vvt_repositorys import VvtRepoCsv, VvtRepoDatabricks, VvtRepository
from src.shared.data_composition import DataComposition
from nicegui import ui
import pandas as pd

from src.shared.data_models import Data
from src.shared.exceptions import WrongInputError
from src.shared.meta_names import MetaNames

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
            self.databricksClient = DatabricksClient()
            self._vvtRepository = VvtRepoDatabricks(self.databricksClient)
            self._measurementRepository = MeasurementRepoDatabricks(self.databricksClient)
            self._metadataRepository = MetadataRepoDatabricks(self.databricksClient)
        else:
            raise ValueError(f"Invalid source '{source}' for VVT repository.")
        
        

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
        try:
            self._measurementRepository.add_measurement(measurement_id,medallionData)
            self._metadataRepository.save_measurement_metadata(metadata, measurement_id)
            
        except Exception as e:
            self._measurementRepository.delete_measurement(measurement_id)
            self._metadataRepository.delete_measurement_metadata(measurement_id)
            print(f"Error while saving measurement to database: {e}")
        
    
    
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
    
    
    
    def is_duplicate(self,metadata: dict )-> bool:
        """checks if a measurement with the "same" metadata already exists in the database
        
        to change the range where a measurement is a duplicate change the timeRange variable of the method."""
        
        timeRange = 3600
        
        # get all saved measurements
        try:
            metaDf = self.list_saved_measurements()
        except FileNotFoundError as e:
            ui.notify(f"Error while fetching saved measurements: {e}", color="red")
            return False
        
        # if metadata is empty return false
        if metaDf.empty:
            return False
        
        # check if date an ovennumber are the same (convert to strings befor combining)
        maskDate = (metaDf[MetaNames.DATE].astype(str).str.strip() == str(metadata[MetaNames.DATE]).strip())
        maskOven = (metaDf[MetaNames.OVEN_NR].astype(str).str.strip() == str(metadata[MetaNames.OVEN_NR]).strip())
        
        # save duplicates
        potential_duplicates = metaDf[maskDate & maskOven]
        
        # if none were found
        if potential_duplicates.empty:
            return False
        
        # convert new meta-time to datetime for easier comparison
        new_meta_time = f"{metadata[MetaNames.DATE]} {metadata[MetaNames.START_TIME]}"
        new_meta_time = pd.to_datetime(new_meta_time)
        
        # convert old times to datetime and compare with new meta time
        existing_times = pd.to_datetime(potential_duplicates[MetaNames.DATE].astype(str) + " " + potential_duplicates[MetaNames.START_TIME].astype(str))
        
        # calculate time difference        
        diff = abs(new_meta_time - existing_times).dt.total_seconds().abs()
        
        # if time is less than (set seconds), consider it a duplicate
        if (diff < timeRange).any():
            return True
        
        return False
    
    
    def get_measurement_metadata(self, measurement_id)-> DataFrame:
        """Returns the metadata for a given id as a DataFrame"""
        return self._metadataRepository.get_measurement_metadata(measurement_id)