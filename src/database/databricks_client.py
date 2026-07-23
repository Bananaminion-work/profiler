import os
import io
from pandas import DataFrame
import csv
from pathlib import Path
from databricks import sql
from dotenv import load_dotenv
from src.shared.table_names import TableNames
from databricks.sdk import WorkspaceClient


class DatabricksClient:
    def __init__(self):
        
        # Load .env from project root (../.. from src/database/databricks_client.py)
        dotenv_path = Path(__file__).resolve().parents[2] / '.env'
        load_dotenv(dotenv_path=dotenv_path)
        
        self.token = os.environ.get('DATABRICKS_TOKEN')
        self.http_path = os.environ.get('HTTP_PATH')
        self.host = os.environ.get('DATABRICKS_HOST')
        
        if not self.token or not self.http_path or not self.host:
            print("kritischer fehler: .env nicht richtig geladen oder variablen fehlen")
            print(f"verwendete .env: {dotenv_path} (exists={dotenv_path.exists()})")
            print(f"versucht zu verbinden zu: host={self.host}, http_path={self.http_path}")
            return
        
        
    def get_data(self, query:str) -> DataFrame:
        
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
            print(f"Error while fetching data from Databricks: {e}")
            raise
        
        
        
        
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
            print(f"Error while executing query on Databricks: {e}")
            raise
            
            
            
    def execute_batch_insert(self, table_name:str, records:list):
        
        # set measurement_id as first entry
        measurement_id = records[0][0]
        # create short name of the table for the temporary file name
        shortName = table_name.split(".")[-1]
        # build file name and volume path for the temporary CSV file
        fileName = f"temp{shortName}-{measurement_id}.csv"
        volumePath = f"{TableNames.EXCHANGE}/{fileName}"
        # instantiate the Databricks SDK WorkspaceClient with host and token from .env
        w = WorkspaceClient(host=f"https://{self.host}", token=self.token)
        
        try:
            #create csv
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["measurement_id","ReadTime","channel","value"])
            writer.writerows(records)


            #use SDK to upload the CSV to Databricks volume
            w.files.upload(
                volumePath,
                io.BytesIO(buffer.getvalue().encode('utf-8')),
                overwrite=True
            )
                       
            # execute bulk load
            self.execute_query(
                f"""
                COPY INTO {table_name}
                FROM '{volumePath}'
                FILEFORMAT = CSV
                FORMAT_OPTIONS ('header' = 'true')
                COPY_OPTIONS ('force' = 'true')
                """
            )
        
        except Exception as e:
            print(f"Error while executing batch insert on Databricks: {e}")
            raise
        
        
        finally:
            #delete temporary file
            try:
                w.files.delete(volumePath)
            except:
                pass

        
        
        #try:
        #    # use contents of .env
        #    with sql.connect(
        #        server_hostname=self.host,
        #        http_path=self.http_path,
        #        access_token=self.token
        #    ) as connection:
        #        # execute the batch insert
        #        cursor = connection.cursor()
        #        
        #        # count the columns
        #        num_columns = len(records[0])
        #        placeholders = ', '.join(['?'] * num_columns)
        #        
        #        # create the insert query
        #        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        #        
        #        # chunking 
        #        chunkSize = 5000
        #        totalRecords = len(records)
        #        
        #        # upload in chunks to avoid memory issues
        #        for i in range(0, totalRecords, chunkSize):
        #            chunk = records[i:i + chunkSize]
        #            cursor.executemany(query, chunk)
        #            print(f"Uploaded {min(i + chunkSize, totalRecords)} of {totalRecords} records to {table_name}.")
        #        
        #        ui.notify(f"Successfully uploaded {totalRecords} records to {table_name}.", color="green")
        #        
        #except Exception as e:
        #    print(f"Error while executing batch insert on Databricks: {e}")
        #    raise