from pathlib import Path
from typing import Dict, Sequence, Any
import uuid
import pandas as pd
from pandas import DataFrame

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class MetadataRepository:
    def __init__(self) -> None:
        pass
        
    def save_measurement_metadata(self, metadata)-> str:
        # Code to save measurement metadata to the database
        return""
        pass

    def get_measurement_metadata(self, measurement_id):
        # Code to retrieve measurement metadata from the database
        pass

    def delete_measurement_metadata(self, measurement_id):
        # Code to delete measurement metadata from the database
        pass
    
    def get_saved_measurements(self):
        # Code to retrieve all saved measurements from the database
        pass
    
    
    
class MetadataRepoCsv(MetadataRepository):
    def __init__(self):
        super().__init__()
        self._pathToCsv = PROJECT_ROOT / "tests" / "fixtures" / "vps_metadata.csv"
    
    def save_measurement_metadata(self, metadata) -> str:
        
        #create unique id
        measurement_id = str(uuid.uuid4())
        
        # get metadata as dict
        metaDict = metadata.get_metadata_dict()
        
        # add measurement_id to dict
        metaDict["measurement_id"] = measurement_id
        
        # convert dict to df
        metaDf = DataFrame([metaDict])
        
        # convert datatypes from string to int, float or bool
        type_conversions = {
            "ovenNr": int,
            "loadProfile": float,
            "testCooler_flag": bool,
            "coolerCountOnTray": int
        }
        metaDf = metaDf.astype(type_conversions)
        
        # move Values in the right order
        columnOrder = [
            "measurement_id",
            "date",
            "startTime",
            "dataSource",
            "ovenNr",
            "product",
            "loadProfile",
            "positionMeasurementCooler",
            "testCooler_flag",
            "coolerCountOnTray",
            "nozzlefield",
            "injection_1",
            "injection_2",
            "injection_3",
            "injection_4",
            "waiting_1",
            "waiting_2",
            "waiting_3",
            "waiting_4",
            "cooling_freq_1",
            "cooling_freq_2",
            "cooling_freq_3",
            "cooling_freq_4",
            "cooling_time_1",
            "cooling_time_2",
            "cooling_time_3",
            "cooling_time_4",
            "profileName",
            "comment"
        ]
        metaDf = metaDf[columnOrder]
        
        # save df to csv
        if self._pathToCsv.exists():
            metaDf.to_csv(self._pathToCsv, mode='a', header=False, index=False)
            return measurement_id
        else:
            return ""
        
    
    def get_measurement_metadata(self, measurement_id):
        pass
    
    def delete_measurement_metadata(self, measurement_id):
        pass
    
    def get_saved_measurements(self):
        pass
        
    
    
    
class MetadataRepoDatabricks(MetadataRepository):
    def __init__(self):
        super().__init__()
    
    def save_measurement_metadata(self, metadata) -> str:
        return ""
    
    def get_measurement_metadata(self, measurement_id):
        pass
    
    def delete_measurement_metadata(self, measurement_id):
        pass