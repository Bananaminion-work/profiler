import os
from time import time as _now
from pandas import DataFrame
from pathlib import Path
from databricks import sql
from dotenv import load_dotenv
from typing import Optional

import random
import requests
from io import StringIO, BytesIO

from src.shared.app_name import AppName
from src.shared.table_names import TableNames


class DatabricksClient:
    def __init__(self):
        
        # Load .env from project root (../.. from src/database/databricks_client.py)
        dotenv_path = Path(__file__).resolve().parents[2] / '.env'
        load_dotenv(dotenv_path=dotenv_path) #no op if file missing
        
        self.token = os.environ.get('DATABRICKS_PAT')
        self.http_path = os.environ.get('HTTP_PATH')
        self.host = os.environ.get('DATABRICKS_HOST')
        
        # delete the variables coming from Databricks to only use the PAT
        os.environ.pop('DATABRICKS_CLIENT_ID', None)
        os.environ.pop('DATABRICKS_CLIENT_SECRET', None)
        os.environ.pop('DATABRICKS_TOKEN', None)
        
        # errorhandling if connection fails
        if not self.token or not self.http_path or not self.host or self.token == "db_pat_vps":
            print("critical error: .env not loaded correctly or variables are missing")
            print(f"used .env: {dotenv_path} (exists={dotenv_path.exists()})")
            print(f"attempted to connect to: host={self.host}, http_path={self.http_path}")
            print(f"token={'SET' if self.token else 'MISSING'}")
            return
        
        # connect initially
        self._connection = None
        self._connect()
        
        
        
    def _connect(self):
        """establishes a connection to the Databricks SQL endpoint
        
        in this case the SQL-Warehouse with the given path and host in the .env file"""
        
        try:

            #use proxy while local
            if Path(__file__).resolve().parents[2].joinpath('.env').exists():
                os.environ['HTTPS_PROXY'] = 'http://rb-proxy-de.bosch.com:8080'

            self._connection = sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token
            )
            print("Databricks connection established successfully.")
        except Exception as e:
            print(f"[DATABRICKS CLIENT] Error while connecting to Databricks: {e}")
            raise
    
    
    
    def _get_cursor(self):
        """returns a cursor from the connection, reconnects if connection is closed"""
        
        try:
            # connect if not connected
            if self._connection is None or not self._connection.open:
                self._connect()
            # return a cursor from the connection    
            return self._connection.cursor() #type: ignore
        except Exception:
            self._connect()
            return self._connection.cursor() #type: ignore
        
        
        
    def close(self):
        """closes the connection to the Databricks SQL endpoint"""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
        
        
        
    def get_data(self, query:str) -> DataFrame:
        """executes a SELECT query and returns the result as a DataFrame"""
        
        try:
            # get cursor
            cursor = self._get_cursor()
            # execute query
            cursor.execute(query)
            # return df
            return cursor.fetchall_arrow().to_pandas() 
            
        except Exception as e:
            print(f"Error while fetching data from Databricks: {e}")
            raise
        
        
        
        
    def execute_query(self, query:str):
        """executes a query (INSERT, UPDATE, DELETE, etc.) on the Databricks SQL endpoint"""
        
        try:
            # get cursor
            cursor = self._get_cursor()
            # execute query
            cursor.execute(query)
                
        except Exception as e:
            print(f"Error while executing query on Databricks: {e}")
            raise

    
    ################# ------ UNUSED VERSION ------ #################
    def execute_batch_insert(self, table_name: str, records: list, columns: Optional[list] = None):
        """chunked upload, uses INSERT INTO ... VALUES (...) for each chunk, with a default chunk size of 30k records
        
        CURRENTLY UNUSED BECAUSE OF PERFORMANCE ISSUES, USE bulk_insert_copy_into() or bulk_insert_parquet() INSTEAD"""

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
            start = _now()
            
            # get cursor
            cursor = self._get_cursor()
                
                
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

            duration = _now() - start
            print(f"[DATABRICKS CLIENT] Batch insert completed. Total duration: {duration:.1f}s")

        except Exception as e:
            print(f"Error while executing batch insert: {e}")
            raise
            
            
            
    def bulk_insert_copy_into(
        self,
        table_name: str,
        df: "DataFrame",
        volume_path: str = TableNames.EXCHANGE):
        """bulk insert with COPY INTO and csv as temporary file"""

        # 1) Eindeutige ID generieren (8-stellige Zufallszahl)
        unique_id = random.randint(10_000_000, 99_999_999)
        file_name = f"upload_{unique_id}.csv"

        # REST API erwartet Pfad OHNE fuehrenden Slash
        api_file_path = f"{volume_path.lstrip('/')}/{file_name}"
        upload_url = f"https://{self.host}/api/2.0/fs/files/{api_file_path}"

        # Volume-Pfad fuer COPY INTO (mit fuehrendem Slash)
        volume_file_path = f"{volume_path}/{file_name}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/octet-stream",
        }

        start = _now()
        print(f"[BULK INSERT] Start | Ziel: {table_name} | Datei: {file_name} | Zeilen: {len(df)}")

        try:
            # 2) DataFrame -> CSV bytes im RAM
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False, header=True)
            csv_bytes = csv_buffer.getvalue().encode("utf-8")
            print(f"[BULK INSERT] CSV erzeugt ({len(csv_bytes) / 1024:.1f} KB)")

            # 3) CSV per REST API ins Volume hochladen
            t_upload = _now()
            response = requests.put(upload_url, headers=headers, data=csv_bytes)
            response.raise_for_status()
            print(f"[BULK INSERT] Upload ins Volume abgeschlossen ({_now() - t_upload:.1f}s)")

            # 4) COPY INTO ausfuehren
            t_copy = _now()
            copy_query = f"""
            COPY INTO {table_name}
            FROM (
                SELECT
                    measurement_id::STRING AS measurement_id,
                    ReadTime::STRING AS ReadTime,
                    channel::STRING AS channel,
                    value::DOUBLE AS value
                FROM '{volume_file_path}'
            )
            FILEFORMAT = CSV
            FORMAT_OPTIONS (
                'header' = 'true',
                'inferSchema' = 'false',
                'delimiter' = ','
            )
            """
            self.execute_query(copy_query)
            print(f"[BULK INSERT] COPY INTO abgeschlossen ({_now() - t_copy:.1f}s)")

            # 5) Datei im Volume wieder loeschen
            t_delete = _now()
            del_response = requests.delete(upload_url, headers=headers)
            del_response.raise_for_status()
            print(f"[BULK INSERT] Datei geloescht ({_now() - t_delete:.1f}s)")

            duration = _now() - start
            print(f"[BULK INSERT] Fertig. Gesamtdauer: {duration:.1f}s")

        except requests.exceptions.HTTPError as e:
            print(f"[BULK INSERT] REST API Fehler: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"[BULK INSERT] Fehler: {type(e).__name__}: {e}")
            # Aufraeumen: Datei loeschen falls sie schon hochgeladen wurde
            try:
                requests.delete(upload_url, headers=headers)
                print("[BULK INSERT] Datei im Volume wurde aufgeraeumt.")
            except Exception:
                pass
            raise
            
            
            
    def bulk_insert_parquet(
        self,
        table_name: str,
        df: "DataFrame",
        volume_path: str = TableNames.EXCHANGE):
        """bulk insert with COPY INTO and parquet as temporary file"""

        # 1) Eindeutige ID generieren (8-stellige Zufallszahl)
        unique_id = random.randint(10_000_000, 99_999_999)
        file_name = f"upload_{unique_id}.parquet"

        # REST API erwartet Pfad OHNE fuehrenden Slash
        api_file_path = f"{volume_path.lstrip('/')}/{file_name}"
        upload_url = f"https://{self.host}/api/2.0/fs/files/{api_file_path}"

        # Volume-Pfad fuer COPY INTO (mit fuehrendem Slash)
        volume_file_path = f"{volume_path}/{file_name}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/octet-stream",
        }

        start = _now()
        print(f"[BULK INSERT] Start | Ziel: {table_name} | Datei: {file_name} | Zeilen: {len(df)}")

        try:
            # 2) DataFrame -> Parquet bytes im RAM
            #    Typen explizit setzen damit Parquet das korrekte Schema schreibt
            df_typed = df.copy()
            df_typed["measurement_id"] = df_typed["measurement_id"].astype(str)
            df_typed["ReadTime"] = df_typed["ReadTime"].astype(str)
            df_typed["channel"] = df_typed["channel"].astype(str)
            df_typed["value"] = df_typed["value"].astype(float)

            parquet_buffer = BytesIO()
            df_typed.to_parquet(parquet_buffer, index=False, engine="pyarrow")
            parquet_bytes = parquet_buffer.getvalue()
            print(f"[BULK INSERT] Parquet erzeugt ({len(parquet_bytes) / 1024:.1f} KB)")

            # 3) Parquet per REST API ins Volume hochladen
            t_upload = _now()
            response = requests.put(upload_url, headers=headers, data=parquet_bytes)
            response.raise_for_status()
            print(f"[BULK INSERT] Upload ins Volume abgeschlossen ({_now() - t_upload:.1f}s)")

            # 4) COPY INTO ausfuehren
            #    Kein Schema-Cast noetig - Parquet traegt die Typen bereits in sich
            t_copy = _now()
            copy_query = f"""
                COPY INTO {table_name}
                FROM '{volume_file_path}'
                FILEFORMAT = PARQUET
            """
            self.execute_query(copy_query)
            print(f"[BULK INSERT] COPY INTO abgeschlossen ({_now() - t_copy:.1f}s)")

            # 5) Datei im Volume wieder loeschen
            t_delete = _now()
            del_response = requests.delete(upload_url, headers=headers)
            del_response.raise_for_status()
            print(f"[BULK INSERT] Datei geloescht ({_now() - t_delete:.1f}s)")

            duration = _now() - start
            print(f"[BULK INSERT] Fertig. Gesamtdauer: {duration:.1f}s")

        except requests.exceptions.HTTPError as e:
            print(f"[BULK INSERT] REST API Fehler: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"[BULK INSERT] Fehler: {type(e).__name__}: {e}")
            # Aufraeumen: Datei loeschen falls sie schon hochgeladen wurde
            try:
                requests.delete(upload_url, headers=headers)
                print("[BULK INSERT] Datei im Volume wurde aufgeraeumt.")
            except Exception:
                pass
            raise
        
        
    def check_admin(self, user, app:str = AppName.APP_NAME) -> bool:
        """checks if the user has admin rights"""
        
        # define url and header
        url = f"https://{self.host}/api/2.0/permissions/apps/{app}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # response
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # get list of users and their permissions, check if the user has admin rights
            for acl in response.json().get("access_control_list", []):
                if acl.get("user_name", "").lower() == user.lower():
                    for permission in acl.get("all_permissions", []):
                        if permission.get("permission_level") == "CAN_MANAGE":
                            return True
            
            return False
        
        except requests.exceptions.HTTPError as e:
            print(f"[CHECK ADMIN] REST API Error: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"[CHECK ADMIN] Error: {type(e).__name__}: {e}")
            return False