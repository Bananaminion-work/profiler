import os

import pandas as pd
from pandas import DataFrame
from src.shared.data_models import Data
from pathlib import Path

from src.shared.exceptions import WrongInputError
from src.shared.table_names import TableNames

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class MeasurementRepository:
    """
    Repository for storing and managing measurements.
    """
    def __init__(self):
        self._measurements = []
    
    def add_measurement(self,measurement_id: str, measurement: dict[str,Data]):
        pass
    
    def get_measurements(self):
        return self._measurements
    
    def get_gold_data_by_id(self, measurement_ids: set)-> DataFrame:
        return DataFrame()
    
    
    
class MeasurementRepoCsv(MeasurementRepository):
    def __init__(self):
        super().__init__()
        self._bronzePath = PROJECT_ROOT / "tests" / "fixtures" / "vps_bronze_data.csv"
        self._silverPath = PROJECT_ROOT / "tests" / "fixtures" / "vps_silver_data.csv"
        self._goldPath = PROJECT_ROOT / "tests" / "fixtures" / "vps_gold_data.csv"
    
    def add_measurement(self, measurement_id: str, measurement: dict[str,Data]):
        """adds a measurement to the database (csv-files)"""
        
        
        # get medallion-data-objects
        bronze = measurement.get("bronze")
        silver = measurement.get("silver")
        gold = measurement.get("gold")
        
        if isinstance(bronze, Data) and isinstance(silver, Data) and isinstance(gold, Data):
            # get Dataframes from medallion-data-objects
            bronzeDf = bronze.get_dataframe()
            silverDf = silver.get_dataframe()
            goldDf = gold.get_dataframe()
        
            # append measurement_id to each dataframe
            bronzeDf['measurement_id'] = measurement_id
            silverDf['measurement_id'] = measurement_id
            goldDf['measurement_id'] = measurement_id
            
            # cretae long format Df for meallion data
            longBronzeDf = bronzeDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="channel", value_name="value")
            longSilverDf = silverDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="channel", value_name="value")
            longGoldDf = goldDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="channel", value_name="value")
            
            # helpingfunction to check if csv needs header
            def needs_header(filepath):
                return not filepath.exists() or os.path.getsize(filepath) == 0
            
            # chekc if folder exists
            if self._bronzePath.parent.exists():
                
                # save longs to csv
                longBronzeDf.to_csv(self._bronzePath, mode='a', header=needs_header(self._bronzePath), index=False)
                longSilverDf.to_csv(self._silverPath, mode='a', header=needs_header(self._silverPath), index=False)
                longGoldDf.to_csv(self._goldPath, mode='a', header=needs_header(self._goldPath), index=False)
                
            else:
                raise FileNotFoundError("The folder for storing measurement csv files does not exist.")
            
        else:
            raise WrongInputError("Measurement Data are none of type Data. Cannot add measurement to database.")
        
            
        
        
    def get_gold_data_by_id(self, measurement_ids: set)-> DataFrame:
        """retrieves gold data for a given measurement id from the csv file"""

        # get dataframe with all gold data
        goldDf = pd.read_csv(self._goldPath)
        
        # filter for rows with the given ids
        filteredGoldDf = goldDf[goldDf['measurement_id'].isin(measurement_ids)]
        
        # always return since its always a DataFrame even if its empty
        return filteredGoldDf #type:ignore
        
        
        

class MeasurementRepoDatabricks(MeasurementRepository):
    def __init__(self, databricksClient):
        super().__init__()
        self.client = databricksClient
        self._bronzeTable = TableNames.BRONZE
        self._silverTable = TableNames.SILVER
        self._goldTable = TableNames.GOLD
    
    def add_measurement(self, measurement_id: str, measurement: dict[str,Data]):
        pass
    
    def get_gold_data_by_id(self, measurement_ids: set)-> DataFrame:
        
        # return empty DataFrame if no measurement_ids are provided
        if not measurement_ids:
            return DataFrame() 
        
        # create a string of measurement_ids for the SQL query
        ids_str = ', '.join(measurement_ids)
        
        # create a query to fetch gold data for the given measurement_ids
        query = f"SELECT * FROM {self._goldTable} WHERE measurement_id IN ({ids_str})"
        
        # use client to get data from Databricks
        return self.client.get_data(query)