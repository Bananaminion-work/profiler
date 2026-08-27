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
        
    def save_measurement_metadata(self, metadata, measurement_id: str):
        # Code to save measurement metadata to the database
        pass

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
    
    def save_measurement_metadata(self, metadata:Metadata, measurement_id: str):
        """saves the metadata of a measurement to the csv file"""
        
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
        columnOrder = MetaNames.get_names()
        
        metaDf = metaDf[columnOrder]
        
        needsHeader = not self._pathToCsv.exists() or os.path.getsize(self._pathToCsv) == 0
        
        # save df to csv
        metaDf.to_csv(self._pathToCsv, mode='a', header=needsHeader, index=False)
        #return measurement_id
    
    
    
    def get_measurement_metadata(self, measurement_id):
        """returns the metadata for a given measurement_id as a DataFrame"""
        metaDf = self.get_saved_measurements()
        
        if metaDf.empty or "measurement_id" not in metaDf.columns:
            return DataFrame()
        
        return cast(DataFrame, metaDf[metaDf["measurement_id"] == measurement_id])
    
    
    
    def delete_measurement_metadata(self, measurement_id):
        """deletes the metadata for the given id from the csv file"""
        metaDf = self.get_saved_measurements()
        
        if metaDf.empty or "measurement_id" not in metaDf.columns:
            return
        
        # filter out the row with the given measurement_id
        metaDf = metaDf[metaDf["measurement_id"] != measurement_id]
        
        # save the updated DataFrame back to the CSV file
        metaDf.to_csv(self._pathToCsv, index=False)
    
    
    def get_saved_measurements(self) -> DataFrame:
        """returns all saved measurements as a DataFrame"""
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
                MetaNames.TEST_COOLER_FLAG: bool,
                MetaNames.COOLER_COUNT_ON_TRAY: int
            }
            metaDf = metaDf.astype(type_conversions)
            
            return metaDf
        else:
            return DataFrame()
    
    
    
class MetadataRepoDatabricks(MetadataRepository):
    def __init__(self, databricksClient, warning):
        super().__init__()
        self.client = databricksClient
        self._metadataTable = TableNames.METADATA
        self._warning = warning
        
    
    def save_measurement_metadata(self, metadata, measurement_id: str):
        """saves the metadata of a measurement to the database (Databricks SQL endpoint)"""
        
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
        
        # load columns
        query = f"SELECT * FROM {self._metadataTable} LIMIT 0"
        tableColumns = self.client.get_data(query).columns        
        
        # order columns of df
        columnOrder = MetaNames.get_names()
        
        validColumns = []
        
        # find columns that are in the table
        for col in columnOrder:
            if col in tableColumns:
                validColumns.append(col)
            
            else:
                val = metaDf[col].values[0] if col in metaDf.columns else "N/A"
                msg = f"column {col} not in table {self._metadataTable}, skipping \n Value of the column: {val}"
                self._warning.warn(msg)
                print(f"[METADATA REPOSITORY (Databricks)] WARNING:\n {msg}")
        
        # create the meatadata df with the valid columns
        metaDf = metaDf[validColumns]
        
        # save to databricks table
        records = list(metaDf.itertuples(index=False, name=None))
        self.client.execute_batch_insert(self._metadataTable, records, columns=validColumns)
        

    
    def get_measurement_metadata(self, measurement_id):
        """returns the metadata for a given measurement_id as a DataFrame"""
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
        """deletes the metadata for the given measurement_id from the database (Databricks SQL endpoint)"""
        #create query
        query = f"DELETE FROM {self._metadataTable} WHERE measurement_id = '{measurement_id}'"
        self.client.execute_query(query)
    
    def get_saved_measurements(self) -> DataFrame:
        """returns all saved measurements as a DataFrame"""
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