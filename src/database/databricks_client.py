import os
from pandas import DataFrame
from pathlib import Path
from databricks import sql
from dotenv import load_dotenv
from typing import Optional


class DatabricksClient:
    def __init__(self):
        
        # Load .env from project root (../.. from src/database/databricks_client.py)
        dotenv_path = Path(__file__).resolve().parents[2] / '.env'
        load_dotenv(dotenv_path=dotenv_path)
        
        self.token = os.environ.get('DATABRICKS_PAT')
        self.http_path = os.environ.get('HTTP_PATH')
        self.host = os.environ.get('DATABRICKS_HOST')
        
        
        # delete the variables coming from Databricks to only use the PAT
        os.environ.pop('DATABRICKS_CLIENT_ID', None)
        os.environ.pop('DATABRICKS_CLIENT_SECRET', None)
        os.environ.pop('DATABRICKS_TOKEN', None)
        # delete the two lines above (or comment them out) if you want to use the App with public tables
        
        
        
        
        if not self.token or not self.http_path or not self.host or self.token == "db_token_vps":
            print("kritischer fehler: .env nicht richtig geladen oder variablen fehlen")
            print(f"verwendete .env: {dotenv_path} (exists={dotenv_path.exists()})")
            print(f"versucht zu verbinden zu: host={self.host}, http_path={self.http_path}")
            print(f"token={self.token}")
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
            
            
            
    def execute_batch_insert(self, table_name: str, records: list, columns: Optional[list] = None):
        try:
            with sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token
            ) as connection:
                cursor = connection.cursor()
                
                chunkSize = 100
                totalRecords = len(records)
                
                # create the string for the columns
                colString = f" (`{'`, `'.join(columns)}`)" if columns else ""
                
                for i in range(0, totalRecords, chunkSize):
                    chunk = records[i:i + chunkSize]
                    
                    # Riesen-String bauen (Die extrem schnelle Methode!)
                    value_strings = []
                    for r in chunk:
                        formatted_vals = []
                        for val in r:
                            # Typen korrekt für SQL formatieren
                            if val is None or str(val).lower() in ['nan', 'nat']:
                                formatted_vals.append("NULL")
                            elif isinstance(val, bool):
                                formatted_vals.append("TRUE" if val else "FALSE")
                            elif isinstance(val, (int, float)):
                                formatted_vals.append(str(val))
                            else:
                                # Strings in ' setzen und einfache Anführungszeichen escapen
                                safe_str = str(val).replace("'", "''")
                                formatted_vals.append(f"'{safe_str}'")
                                
                        # Zeile als (val1, val2, ...) anhängen
                        value_strings.append(f"({', '.join(formatted_vals)})")
                        
                    # Ein einziger Insert-Befehl für 5000 Zeilen
                    insert_query = f"INSERT INTO {table_name}{colString} VALUES " + ", ".join(value_strings)
                    cursor.execute(insert_query)
                    
                    print(f"Uploaded {min(i + chunkSize, totalRecords)} of {totalRecords} records to {table_name}.")
                    
        except Exception as e:
            print(f"Error while executing batch insert on Databricks: {e}")
            raise


        
        
        # old version: Upload with temporary CSV file
            # doesnt work bc Databricks wont let you create a file even if its in your own workspace
        
        ## set measurement_id as first entry
        #measurement_id = records[0][0]
        ## create short name of the table for the temporary file name
        #shortName = table_name.split(".")[-1]
        ## build file name and volume path for the temporary CSV file
        #fileName = f"temp{shortName}-{measurement_id}.csv"
        #volumePath = f"{TableNames.EXCHANGE}/{fileName}"
        ## instantiate the Databricks SDK WorkspaceClient with host and token from .env
        #cfg = Config(host=f"https://{self.host}", token=self.token, auth_type="pat")
        #w = WorkspaceClient(config=cfg)
        #
        #try:
        #    #create csv
        #    buffer = io.StringIO()
        #    writer = csv.writer(buffer)
        #    writer.writerow(["measurement_id","ReadTime","channel","value"])
        #    writer.writerows(records)
#
#
        #    #use SDK to upload the CSV to Databricks volume
        #    w.files.upload(
        #        volumePath,
        #        io.BytesIO(buffer.getvalue().encode('utf-8')),
        #        overwrite=True
        #    )
        #               
        #    # execute bulk load
        #    self.execute_query(
        #        f"""
        #        COPY INTO {table_name}
        #        FROM '{volumePath}'
        #        FILEFORMAT = CSV
        #        FORMAT_OPTIONS ('header' = 'true')
        #        COPY_OPTIONS ('force' = 'true')
        #        """
        #    )
        #
        #except Exception as e:
        #    print(f"Error while executing batch insert on Databricks: {e}")
        #    raise
        #
        #
        #finally:
        #    #delete temporary file
        #    try:
        #        w.files.delete(volumePath)
        #    except:
        #        pass

        
        
        
        # old version: Upload with chunks (10 min for 1.2k lines....)
        
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