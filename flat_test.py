from src.database.database_manager import DatabaseManager
from src.database.databricks_client import DatabricksClient
import time

def wide_test():

    database = DatabaseManager(source="csv")
    client = DatabricksClient()
    
    id = "4649a449-e35b-480e-a153-ec6880cbd366"
    id_set = {id}
    
    # get data and reset index
    gold = database._measurementRepository.get_gold_data_by_id(id_set)
    
    # append measurement_id column
    gold["measurement_id"] = id
    
    
    records = list(gold.itertuples(index=False, name=None))
    columns = list(gold.columns)
    
    #start measurement
    start_time = time.time()
    
    client.execute_batch_insert("bmlpdp_x_me_emea_d.x_usr_dea6rt.vps_test_flat_table", records=records, columns=columns)
    
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
    
    
if __name__ == "__main__":
    wide_test()