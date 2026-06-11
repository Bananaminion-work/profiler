from pathlib import Path
import pandas as pd
from pandas import DataFrame
import os

from src.shared.meta_names import MetaNames
from src.shared.metadata import Metadata

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class MetadataRepository:
    def __init__(self) -> None:
        pass
        
    def save_measurement_metadata(self, metadata, measurement_id: str) -> str:
        # Code to save measurement metadata to the database
        return""

    def get_measurement_metadata(self, measurement_id):
        # Code to retrieve measurement metadata from the database
        pass

    def delete_measurement_metadata(self, measurement_id):
        # Code to delete measurement metadata from the database
        pass
    
    def get_saved_measurements(self) -> DataFrame:
        # Code to retrieve all saved measurements from the database
        return DataFrame()
      
    
    
class MetadataRepoCsv(MetadataRepository):
    def __init__(self):
        super().__init__()
        self._pathToCsv = PROJECT_ROOT / "tests" / "fixtures" / "vps_metadata.csv"
    
    def save_measurement_metadata(self, metadata:Metadata, measurement_id: str) -> str:
        
        # get metadata as dict
        metaDict = metadata.get_metadata_dict()
        
        # add measurement_id to dict
        metaDict[MetaNames.MEASUREMENT_ID] = measurement_id
        
        # convert dict to df
        metaDf = DataFrame([metaDict])
        
        # convert datatypes from string to int, float or bool
        type_conversions = {
            MetaNames.OVEN_NR   : int,
            MetaNames.LOAD_PROFILE  : float,
            MetaNames.TEST_COOLER_FLAG  : bool,
            MetaNames.COOLER_COUNT_ON_TRAY  : int
        }
        metaDf = metaDf.astype(type_conversions,errors='ignore')
        
        # move Values in the right order
        columnOrder = [
            MetaNames.MEASUREMENT_ID,
            MetaNames.DATE,
            MetaNames.START_TIME,
            MetaNames.DATA_SOURCE,
            MetaNames.OVEN_RECIPE,
            MetaNames.OVEN_NR,
            MetaNames.PRODUCT,
            MetaNames.LOAD_PROFILE,
            MetaNames.POSITION_MEASUREMENT_COOLER,
            MetaNames.TEST_COOLER_FLAG,
            MetaNames.COOLER_COUNT_ON_TRAY,
            MetaNames.NOZZLEFIELD,
            MetaNames.PROFILE_NAME,
            MetaNames.COMMENT,
            MetaNames.INJECTION_1,
            MetaNames.INJECTION_2,
            MetaNames.INJECTION_3,
            MetaNames.INJECTION_4,
            MetaNames.WAITING_1,
            MetaNames.WAITING_2,
            MetaNames.WAITING_3,
            MetaNames.WAITING_4,
            MetaNames.COOLING_FREQ_1,
            MetaNames.COOLING_FREQ_2,
            MetaNames.COOLING_FREQ_3,
            MetaNames.COOLING_FREQ_4,
            MetaNames.COOLING_TIME_1,
            MetaNames.COOLING_TIME_2,
            MetaNames.COOLING_TIME_3,
            MetaNames.COOLING_TIME_4
        ]
        metaDf = metaDf[columnOrder]
        
        needsHeader = not self._pathToCsv.exists() or os.path.getsize(self._pathToCsv) == 0
        
        # save df to csv
        metaDf.to_csv(self._pathToCsv, mode='a', header=needsHeader, index=False)
        return measurement_id
    
    
    
    def get_measurement_metadata(self, measurement_id):
        pass
    
    
    
    def delete_measurement_metadata(self, measurement_id):
        pass
    
    
    
    def get_saved_measurements(self) -> DataFrame:
        
        # read in the content of the csv as a dataframe and return it
        if self._pathToCsv.exists():
            metaDf = pd.read_csv(self._pathToCsv)
            
            # ceonvert the time columns
            if MetaNames.DATE in metaDf.columns and MetaNames.START_TIME in metaDf.columns:
                
                #convert date
                metaDf[MetaNames.DATE] = pd.to_datetime(
                    metaDf[MetaNames.DATE],
                    format = "%Y-%m-%d",
                    errors='coerce'
                    ).dt.date #type:ignore
                
                #convert time without date
                metaDf[MetaNames.START_TIME] = pd.to_datetime(
                    metaDf[MetaNames.START_TIME],
                    format = "%H:%M:%S",
                    errors='coerce'
                    ).dt.time #type:ignore
                        
            
            # convert the datatypes from string in the csv as needed
            type_conversions = {
                MetaNames.OVEN_NR: int,
                MetaNames.LOAD_PROFILE: float,
                MetaNames.TEST_COOLER_FLAG: bool,
                MetaNames.COOLER_COUNT_ON_TRAY: int,
                MetaNames.INJECTION_1: float,
                MetaNames.INJECTION_2: float,
                MetaNames.INJECTION_3: float,
                MetaNames.INJECTION_4: float,
                MetaNames.WAITING_1: float,
                MetaNames.WAITING_2: float,
                MetaNames.WAITING_3: float,
                MetaNames.WAITING_4: float,
                MetaNames.COOLING_FREQ_1: float,
                MetaNames.COOLING_FREQ_2: float,
                MetaNames.COOLING_FREQ_3: float,
                MetaNames.COOLING_FREQ_4: float,
                MetaNames.COOLING_TIME_1: float,
                MetaNames.COOLING_TIME_2: float,
                MetaNames.COOLING_TIME_3: float,
                MetaNames.COOLING_TIME_4: float
            }
            metaDf = metaDf.astype(type_conversions)
            
            return metaDf
        else:
            return DataFrame()
    
    
    
class MetadataRepoDatabricks(MetadataRepository):
    def __init__(self):
        super().__init__()
    
    def save_measurement_metadata(self, metadata, measurement_id: str) -> str:
        return ""
    
    def get_measurement_metadata(self, measurement_id):
        pass
    
    def delete_measurement_metadata(self, measurement_id):
        pass
    
    def get_saved_measurements(self) -> DataFrame:
            return DataFrame()