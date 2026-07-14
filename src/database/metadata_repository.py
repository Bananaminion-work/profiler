from datetime import datetime
from pathlib import Path
from attrs import fields
import pandas as pd
from pandas import DataFrame
import os

from src.shared.meta_names import MetaNames
from src.shared.metadata import Metadata
from typing import cast

from src.shared.table_names import TableNames

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class MetadataRepository:
    def __init__(self) -> None:
        pass
        
    def save_measurement_metadata(self, metadata, measurement_id: str) -> str:
        # Code to save measurement metadata to the database
        return""

    def get_measurement_metadata(self, measurement_id) -> DataFrame:
        # Code to retrieve measurement metadata from the database
        return DataFrame()

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
            MetaNames.LOAD_PROFILE  : float,
            MetaNames.TEST_COOLER_FLAG  : bool,
            MetaNames.COOLER_COUNT_ON_TRAY  : int
        }
        metaDf = metaDf.astype(type_conversions,errors='ignore')
        
        # move Values in the right order
        columnOrder = [
            MetaNames.MEASUREMENT_ID,            MetaNames.DATE,
            MetaNames.START_TIME,            MetaNames.DATA_SOURCE,
            MetaNames.OVEN_RECIPE,            MetaNames.OVEN_NR,
            MetaNames.PRODUCT,            MetaNames.LOAD_PROFILE,
            MetaNames.POSITION_MEASUREMENT_COOLER,            MetaNames.TEST_COOLER_FLAG,
            MetaNames.COOLER_COUNT_ON_TRAY,            MetaNames.NOZZLEFIELD,
            MetaNames.PROFILE_NAME,            MetaNames.COMMENT,
            MetaNames.INJECTION_1,            MetaNames.INJECTION_2,
            MetaNames.INJECTION_3,            MetaNames.INJECTION_4,
            MetaNames.WAITING_1,            MetaNames.WAITING_2,
            MetaNames.WAITING_3,            MetaNames.WAITING_4,
            MetaNames.COOLING_FREQ_1,            MetaNames.COOLING_FREQ_2,
            MetaNames.COOLING_FREQ_3,            MetaNames.COOLING_FREQ_4,
            MetaNames.COOLING_TIME_1,            MetaNames.COOLING_TIME_2,
            MetaNames.COOLING_TIME_3,            MetaNames.COOLING_TIME_4
        ]
        metaDf = metaDf[columnOrder]
        
        needsHeader = not self._pathToCsv.exists() or os.path.getsize(self._pathToCsv) == 0
        
        # save df to csv
        metaDf.to_csv(self._pathToCsv, mode='a', header=needsHeader, index=False)
        return measurement_id
    
    
    
    def get_measurement_metadata(self, measurement_id):
        
        metaDf = self.get_saved_measurements()
        
        if metaDf.empty or "measurement_id" not in metaDf.columns:
            return DataFrame()
        
        return cast(DataFrame, metaDf[metaDf["measurement_id"] == measurement_id])
    
    
    
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
                MetaNames.LOAD_PROFILE: float,
                MetaNames.TEST_COOLER_FLAG: bool,
                MetaNames.COOLER_COUNT_ON_TRAY: int
            }
            metaDf = metaDf.astype(type_conversions)
            
            return metaDf
        else:
            return DataFrame()
    
    
    
class MetadataRepoDatabricks(MetadataRepository):
    def __init__(self, databricksClient):
        super().__init__()
        self.client = databricksClient
        self._metadataTable = TableNames.METADATA
        #self.create_metadata_table_if_not_exists()
    
    def save_measurement_metadata(self, metadata, measurement_id: str) -> str:
        
        # get metadata as dict
        metaDict = metadata.get_metadata_dict()
        metaDict[MetaNames.MEASUREMENT_ID] = measurement_id
        # convert dict to df
        metaDf = DataFrame([metaDict])
        
        # convert datatypes from string as needed
        type_conversions = {
            MetaNames.LOAD_PROFILE: float,
            MetaNames.TEST_COOLER_FLAG: bool,
            MetaNames.COOLER_COUNT_ON_TRAY: int
        }
        metaDf = metaDf.astype(type_conversions, errors='ignore')
        
        # order columns of df
        columnOrder = [
            MetaNames.MEASUREMENT_ID,            MetaNames.DATE,
            MetaNames.START_TIME,            MetaNames.DATA_SOURCE,
            MetaNames.OVEN_RECIPE,            MetaNames.OVEN_NR,
            MetaNames.PRODUCT,            MetaNames.LOAD_PROFILE,
            MetaNames.POSITION_MEASUREMENT_COOLER,            MetaNames.TEST_COOLER_FLAG,
            MetaNames.COOLER_COUNT_ON_TRAY,            MetaNames.NOZZLEFIELD,
            MetaNames.PROFILE_NAME,            MetaNames.COMMENT,
            MetaNames.INJECTION_1,            MetaNames.INJECTION_2,
            MetaNames.INJECTION_3,            MetaNames.INJECTION_4,
            MetaNames.WAITING_1,            MetaNames.WAITING_2,
            MetaNames.WAITING_3,            MetaNames.WAITING_4,
            MetaNames.COOLING_FREQ_1,            MetaNames.COOLING_FREQ_2,
            MetaNames.COOLING_FREQ_3,            MetaNames.COOLING_FREQ_4,
            MetaNames.COOLING_TIME_1,            MetaNames.COOLING_TIME_2,
            MetaNames.COOLING_TIME_3,            MetaNames.COOLING_TIME_4
        ]
        metaDf = metaDf[columnOrder]
        
        # save to databricks table
        records = list(metaDf.itertuples(index=False, name=None))
        self.client.upload_dataframe(self._metadataTable, records)
        
        # return measurement_id if successful so other data is correct
        return measurement_id

    
    def get_measurement_metadata(self, measurement_id):
        
        
        #create the query
        query = f"SELECT * FROM {self._metadataTable} WHERE measurement_id = '{measurement_id}'"
        metaDf = self.client.get_data(query)
        
        # convert time and date
        if not metaDf.empty and MetaNames.DATE in metaDf.columns and MetaNames.START_TIME in metaDf.columns:
            # if date and starttime is set, convert them to datetime objects
            metaDf[MetaNames.DATE] = pd.to_datetime(
                metaDf[MetaNames.DATE],
                format = "%Y-%m-%d",
                errors='coerce'
                ).dt.date #type:ignore
            metaDf[MetaNames.START_TIME] = pd.to_datetime(
                metaDf[MetaNames.START_TIME],
                format = "%H:%M:%S",
                errors='coerce'
                ).dt.time #type:ignore
        return metaDf
    
    def delete_measurement_metadata(self, measurement_id):
        
        #create query
        query = f"DELETE FROM {self._metadataTable} WHERE measurement_id = '{measurement_id}'"
        self.client.execute_query(query)
    
    def get_saved_measurements(self) -> DataFrame:
            
        # create query
        query = f"SELECT * FROM {self._metadataTable}"
        metaDf = self.client.get_data(query)
        
        # convert time and date
        if not metaDf.empty and MetaNames.DATE in metaDf.columns and MetaNames.START_TIME in metaDf.columns:
            # if date and starttime is set, convert them to datetime objects
            metaDf[MetaNames.DATE] = pd.to_datetime(
                metaDf[MetaNames.DATE],
                format = "%Y-%m-%d",
                errors='coerce'
                ).dt.date #type:ignore
            metaDf[MetaNames.START_TIME] = pd.to_datetime(
                metaDf[MetaNames.START_TIME],
                format = "%H:%M:%S",
                errors='coerce'
                ).dt.time #type:ignore
        return metaDf
            
            
                    
    def create_metadata_table_if_not_exists(self):
        #create types
        sqlTypes = {
            MetaNames.MEASUREMENT_ID: "STRING",
            MetaNames.DATE: "DATE",
            MetaNames.START_TIME: "STRING", 
            MetaNames.OVEN_NR: "INT",
            MetaNames.LOAD_PROFILE: "DOUBLE",
            MetaNames.TEST_COOLER_FLAG: "BOOLEAN",
            MetaNames.COOLER_COUNT_ON_TRAY: "INT",
        }
        
        #create list of float values
        floatColumns = [
            MetaNames.INJECTION_1, MetaNames.INJECTION_2, MetaNames.INJECTION_3, MetaNames.INJECTION_4,
            MetaNames.WAITING_1, MetaNames.WAITING_2, MetaNames.WAITING_3, MetaNames.WAITING_4,
            MetaNames.COOLING_FREQ_1, MetaNames.COOLING_FREQ_2, MetaNames.COOLING_FREQ_3, MetaNames.COOLING_FREQ_4,
            MetaNames.COOLING_TIME_1, MetaNames.COOLING_TIME_2, MetaNames.COOLING_TIME_3, MetaNames.COOLING_TIME_4
        ]
        
        # apply type
        for col in floatColumns:
            sqlTypes[col] = "DOUBLE"
            
        # order the columns
        columnOrder = [
            MetaNames.MEASUREMENT_ID, MetaNames.DATE, MetaNames.START_TIME,
            MetaNames.DATA_SOURCE, MetaNames.OVEN_RECIPE, MetaNames.OVEN_NR,
            MetaNames.PRODUCT, MetaNames.LOAD_PROFILE, MetaNames.POSITION_MEASUREMENT_COOLER,
            MetaNames.TEST_COOLER_FLAG, MetaNames.COOLER_COUNT_ON_TRAY, MetaNames.NOZZLEFIELD,
            MetaNames.PROFILE_NAME, MetaNames.COMMENT
        ] + floatColumns
        
        # create sql block
        columnsSql = []
        for col in columnOrder:
            colType = sqlTypes.get(col, "STRING")  # default to STRING if not found
            columnsSql.append(f"{col} {colType}")
        
        # create sql string    
        columnsSqlStr = ",\n".join(columnsSql)
        
        # create query
        query = f"""
        CREATE TABLE IF NOT EXISTS {self._metadataTable} (
            {columnsSqlStr}
        )
        """
        
        self.client.execute_query(query)