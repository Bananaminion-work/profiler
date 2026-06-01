from pathlib import Path
import uuid
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
        
        # save df to csv
        if self._pathToCsv.exists():
            metaDf.to_csv(self._pathToCsv, mode='a', header=False, index=True)
            return measurement_id
        else:
            return ""
        
    
    def get_measurement_metadata(self, measurement_id):
        pass
    
    def delete_measurement_metadata(self, measurement_id):
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