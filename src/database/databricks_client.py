import os
from time import time as _now
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

        # chunk size, lenth of records, and column string for SQL query
        chunk_size = 30000
        total_records = len(records)
        col_string = f" (`{'`, `'.join(columns)}`)" if columns else ""

        print(f"[DATABRICKS CLIENT] Starting batch insert of {total_records} records into {table_name} in chunks of {chunk_size}...")

        
        
        # Helper function to format values for SQL insertion
        def _format_value(val):
            if val is None or str(val).lower() in ('nan', 'nat'):
                return "NULL"
            elif isinstance(val, bool):
                return "TRUE" if val else "FALSE"
            elif isinstance(val, (int, float)):
                return str(val)
            else:
                return f"'{str(val).replace(chr(39), chr(39)+chr(39))}'"
            
        
        # try to save, raise exception if failed
        try:
            # split the records in chunks
            chunks = [records[i:i + chunk_size] for i in range(0, total_records, chunk_size)]
            total_chunks = len(chunks)
            
            # save the time for evaluation
            start_total = _now()
            
            # create connector and cursor
            with sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token
            ) as connection:
                cursor = connection.cursor()
                
                # insert chunks one by one
                for idx, chunk in enumerate(chunks):
                    # starttime for evaluation
                    start_chunk = _now()
                    
                    print(f"[DATABRICKS CLIENT] Inserting chunk {idx + 1}/{total_chunks} with {len(chunk)} records...")
                    
                    # create the value strings for the SQL insert
                    value_strings = [
                        f"({', '.join(_format_value(val) for val in r)})"
                        for r in chunk
                    ]
                    
                    # create the insert query
                    insert_query = f"INSERT INTO {table_name}{col_string} VALUES " + ", ".join(value_strings)
                    
                    # execute query
                    cursor.execute(insert_query)
                    
                    duration = _now() - start_chunk
                    print(f"[DATABRICKS CLIENT] Chunk {idx + 1}/{total_chunks} inserted in {duration:.1f}s.")
                    
                cursor.close()

            total_duration = _now() - start_total
            print(f"[DATABRICKS CLIENT] Batch insert completed. Total duration: {total_duration:.1f}s")

        except Exception as e:
            print(f"Error while executing batch insert: {e}")
            raise
            
            
    #def execute_batch_insert(self, table_name: str, records: list, columns: Optional[list] = None):
    #    try:
    #        with sql.connect(
    #            server_hostname=self.host,
    #            http_path=self.http_path,
    #            access_token=self.token
    #        ) as connection:
    #            cursor = connection.cursor()
    #            
    #            chunkSize = 5000
    #            totalRecords = len(records)
    #            
    #            # create the string for the columns
    #            colString = f" (`{'`, `'.join(columns)}`)" if columns else ""
    #            
    #            for i in range(0, totalRecords, chunkSize):
    #                chunk = records[i:i + chunkSize]
    #                
    #                # Riesen-String bauen (Die extrem schnelle Methode!)
    #                value_strings = []
    #                for r in chunk:
    #                    formatted_vals = []
    #                    for val in r:
    #                        # Typen korrekt für SQL formatieren
    #                        if val is None or str(val).lower() in ['nan', 'nat']:
    #                            formatted_vals.append("NULL")
    #                        elif isinstance(val, bool):
    #                            formatted_vals.append("TRUE" if val else "FALSE")
    #                        elif isinstance(val, (int, float)):
    #                            formatted_vals.append(str(val))
    #                        else:
    #                            # Strings in ' setzen und einfache Anführungszeichen escapen
    #                            safe_str = str(val).replace("'", "''")
    #                            formatted_vals.append(f"'{safe_str}'")
    #                            
    #                    # Zeile als (val1, val2, ...) anhängen
    #                    value_strings.append(f"({', '.join(formatted_vals)})")
    #                    
    #                # Ein einziger Insert-Befehl für 5000 Zeilen
    #                insert_query = f"INSERT INTO {table_name}{colString} VALUES " + ", ".join(value_strings)
    #                cursor.execute(insert_query)
    #                
    #                print(f"Uploaded {min(i + chunkSize, totalRecords)} of {totalRecords} records to {table_name}.")
    #                
    #    except Exception as e:
    #        print(f"Error while executing batch insert on Databricks: {e}")
    #        raise