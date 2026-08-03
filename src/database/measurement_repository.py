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
    
    def delete_measurement(self, measurement_id):
        pass
    
    def _format_measurement(self,df:DataFrame)->DataFrame:
        
        if df.empty:
            return df
        
        # create copy for safety
        df = df.copy()
        
        # define Datatypes
        if 'ReadTime' in df.columns:
            df['ReadTime'] = pd.to_numeric(df['ReadTime'], errors='coerce')
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
        if 'measurement_id' in df.columns:
            df['measurement_id'] = df['measurement_id'].astype(str)
            
        # change from long to wide
        if all(col in df.columns for col in ['measurement_id','ReadTime','channel','value']):
            df = df.pivot_table(
                index=['measurement_id','ReadTime'],
                columns='channel',
                values='value'
            ).reset_index()
            
        # ensure that the columns are in the correct order
        if 'measurement_id' in df.columns and 'ReadTime' in df.columns:
            df = df.sort_values(by=['measurement_id','ReadTime'])
        
        return df
        
    
    
    
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
        return self._format_measurement(filteredGoldDf) #type:ignore
    
    
    
    
    def delete_measurement(self, measurement_id):
        
        # delete measurement from all medallion csv files
        for path in [self._bronzePath, self._silverPath, self._goldPath]:
            if path.exists():
                df = pd.read_csv(path)
                df = df[df['measurement_id'] != measurement_id]
                df.to_csv(path, index=False)
        
        
        

class MeasurementRepoDatabricks(MeasurementRepository):
    def __init__(self, databricksClient):
        super().__init__()
        self.client = databricksClient
        self._bronzeTable = TableNames.BRONZE
        self._silverTable = TableNames.SILVER
        self._goldTable = TableNames.GOLD
        
    ##################---------------------------WIDE FORMAT OF THE TABLE---------------------------##################
        
    def add_measurement(self, measurement_id: str, measurement: dict[str,Data]):
        # get medallion-data-objects
        bronze = measurement.get("bronze")
        silver = measurement.get("silver")
        gold = measurement.get("gold")

        # failiurehandling
        if not (isinstance(bronze, Data) and isinstance(silver, Data) and isinstance(gold, Data)):
            print(f"Failed to add measurement to database. Medallion data should be of type Data.")
            print (f"Medallion data should be of type Data, got Bronze: {type(bronze)}, Silver: {type(silver)}, Gold: {type(gold)} instead.")
            return
        
        # 1. Wir holen die DataFrames (im flachen Original-Format)
        bronzeDf = bronze.get_dataframe().copy()
        silverDf = silver.get_dataframe().copy()
        goldDf = gold.get_dataframe().copy()
        
        # 2. ReadTime aus dem Index holen, BEVOR wir die ID anhängen
        bronzeDf = bronzeDf.reset_index()
        silverDf = silverDf.reset_index()
        goldDf = goldDf.reset_index()
        
        # 3. ID anhängen
        bronzeDf['measurement_id'] = measurement_id
        silverDf['measurement_id'] = measurement_id
        goldDf['measurement_id'] = measurement_id
        
        # 4. DIREKT HOCHLADEN (ohne .melt()!)
        # ACHTUNG: Nur für diesen Cloud-Test nehmen wir dreimal dieselbe Test-Tabelle!
        import time
        start_time = time.time()
        
        test_table = "bmlpdp_x_me_emea_d.x_usr_dea6rt.vps_test_flat_table"
        
        # Wir laden nur Gold hoch, um den Speed zu messen
        self._upload_dataframe(test_table, goldDf)
        
        end_time = time.time()
        print(f"CLOUD SPEED-TEST BEENDET! Dauer: {end_time - start_time:.2f} Sekunden.")


    def _upload_dataframe(self, table_name: str, df: DataFrame):
        if df.empty:
            print(f"No data to upload to {table_name}.")
            return
            
        # 1. Wir müssen die Spaltennamen extrahieren
        columns = list(df.columns)
        
        # 2. Tupel erstellen
        records = list(df.itertuples(index=False, name=None))
        
        # 3. Dem Client die Spaltennamen mitgeben!
        try:
            self.client.execute_batch_insert(table_name, records, columns=columns)
            
        except Exception as e:
            print(f"Failed to upload data to {table_name}. Error: {e}")
            raise e

    
    
    ##################---------------------------LONG FORMAT OF THE TABLE---------------------------##################    
    
    #def add_measurement(self, measurement_id: str, measurement: dict[str,Data]):
    #    
    #    
    #    # get medallion-data-objects
    #    bronze = measurement.get("bronze")
    #    silver = measurement.get("silver")
    #    gold = measurement.get("gold")
    #    
    #    # failiurehandling
    #    if not (isinstance(bronze, Data) and isinstance(silver, Data) and isinstance(gold, Data)):
    #        print(f"Failed to add measurement to database. Medallion data should be of type Data.")
    #        print (f"Medallion data should be of type Data, got Bronze: {type(bronze)}, Silver: {type(silver)}, Gold: {type(gold)} instead.")
    #        return
    #    
    #    #  copy dataframes from medallion-data-objects
    #    bronzeDf = bronze.get_dataframe().copy()
    #    silverDf = silver.get_dataframe().copy()
    #    goldDf = gold.get_dataframe().copy()
    #    
    #    # append measurement_id to each dataframe
    #    bronzeDf['measurement_id'] = measurement_id
    #    silverDf['measurement_id'] = measurement_id
    #    goldDf['measurement_id'] = measurement_id
    #    
    #    # convert dataframes to long format
    #    longBronzeDf = bronzeDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="channel", value_name="value")
    #    longSilverDf = silverDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="channel", value_name="value")
    #    longGoldDf = goldDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="channel", value_name="value")
    #    
    #    # write data to databricks tables
    #    self._upload_dataframe(self._bronzeTable, longBronzeDf)
    #    self._upload_dataframe(self._silverTable, longSilverDf)
    #    self._upload_dataframe(self._goldTable, longGoldDf)
    #    
    #    
    #    
    #    
    #def _upload_dataframe(self, table_name: str, df: DataFrame):
    #    
    #    # if no data to upload, return
    #    if df.empty:
    #        print(f"No data to upload to {table_name}.")
    #        return
    #    
    #    # make list of tuples out of the Dataframes
    #    records = list(df.itertuples(index=False, name=None))
    #    
    #    # use client to upload data to databricks
    #    try:
    #        self.client.execute_batch_insert(table_name, records)
    #        
    #    except Exception as e:
    #        print(f"Failed to upload data to {table_name}. Error: {e}")
    #        raise e
    
    
    
    def get_gold_data_by_id(self, measurement_ids: set)-> DataFrame:
        
        # return empty DataFrame if no measurement_ids are provided
        if not measurement_ids:
            return DataFrame() 
        
        # create a string of measurement_ids for the SQL query
        ids_str = ", ".join([f"'{m}'" for m in measurement_ids])
        
        # create a query to fetch gold data for the given measurement_ids
        query = f"SELECT * FROM {self._goldTable} WHERE measurement_id IN ({ids_str})"
        
        # use client to get data from Databricks
        df = self.client.get_data(query)
        
        # apply formatting to the DataFrame
        return self._format_measurement(df)
            
            
            
    def delete_measurement(self, measurement_id):
        
        # create query to delete measurement from all tables
        for table in [self._bronzeTable, self._silverTable, self._goldTable]:
            query = f"DELETE FROM {table} WHERE measurement_id = '{measurement_id}'"
            self.client.execute_query(query)