import os
from nicegui import ui
from pandas import DataFrame
from pathlib import Path
from databricks import sql
from dotenv import load_dotenv


class DatabricksClient:
    def __init__(self):
        
        # get contents of .env file
        load_dotenv(os.path.join(Path(__file__).parent.parent.parent, '.env'))
        
        self.token = os.environ.get('DATABRICKS_TOKEN')
        self.http_path = os.environ.get('HTTP_PATH')
        self.host = os.environ.get('DATABRICKS_HOST')
        
    def get_data(self, query:str)-> DataFrame:
        
        try:
            # use contents of .env
            with sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token
            ) as connection:
                # execute the query and return the result as a DataFrame
                cursor = connection.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                
                # get column names from cursor description and create DataFrame
                if cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]
                else:
                    columns = []
                    
                return DataFrame(results, columns=columns)
            
            
        except Exception as e:
            ui.notify(f"Error while fetching data from Databricks: {e}", color="red")
            return DataFrame()
        
        
        
        
    def execute_query(self, query:str):
        try:
            # use contents of .env
            with sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token
            ) as connection:
                # execute the query
                cursor = connection.cursor()
                cursor.execute(query)
                
        except Exception as e:
            ui.notify(f"Error while executing query on Databricks: {e}", color="red")
            
            
            
    def execute_batch_insert(self, table_name:str, records:list):
        
        try:
            # use contents of .env
            with sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token
            ) as connection:
                # execute the batch insert
                cursor = connection.cursor()
                
                # create the insert query
                query = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?)"
                
                # execute the batch insert
                cursor.executemany(query, records)
                
        except Exception as e:
            ui.notify(f"Error while executing batch insert on Databricks: {e}", color="red")