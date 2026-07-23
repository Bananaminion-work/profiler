from src.shared.meta_names import MetaNames

def generate_metadata_sql():
    # 1. Deine exakte Reihenfolge aus dem Repo
    columnOrder = [
        MetaNames.MEASUREMENT_ID,            MetaNames.DATE,
        MetaNames.START_TIME,                MetaNames.DATA_SOURCE,
        MetaNames.OVEN_RECIPE,               MetaNames.OVEN_NR,
        MetaNames.PRODUCT,                   MetaNames.LOAD_PROFILE,
        MetaNames.POSITION_MEASUREMENT_COOLER, MetaNames.TEST_COOLER_FLAG,
        MetaNames.COOLER_COUNT_ON_TRAY,      MetaNames.NOZZLEFIELD,
        MetaNames.PROFILE_NAME,              MetaNames.COMMENT,
        MetaNames.INJECTION_1,               MetaNames.INJECTION_2,
        MetaNames.INJECTION_3,               MetaNames.INJECTION_4,
        MetaNames.WAITING_1,                 MetaNames.WAITING_2,
        MetaNames.WAITING_3,                 MetaNames.WAITING_4,
        MetaNames.COOLING_FREQ_1,            MetaNames.COOLING_FREQ_2,
        MetaNames.COOLING_FREQ_3,            MetaNames.COOLING_FREQ_4,
        MetaNames.COOLING_TIME_1,            MetaNames.COOLING_TIME_2,
        MetaNames.COOLING_TIME_3,            MetaNames.COOLING_TIME_4
    ]

    # 2. Deine spezifischen Datentypen
    type_conversions = {
        MetaNames.LOAD_PROFILE: float,
        MetaNames.TEST_COOLER_FLAG: bool,
        MetaNames.COOLER_COUNT_ON_TRAY: int
    }

    # 3. SQL-Generator Logik
    sql_columns = []
    for col in columnOrder:
        # Standard ist immer STRING
        sql_type = "STRING"
        
        # Falls es eine Sonderregel gibt, Typ mappen
        if col in type_conversions:
            py_type = type_conversions[col]
            if py_type == float:
                sql_type = "DOUBLE"
            elif py_type == bool:
                sql_type = "BOOLEAN"
            elif py_type == int:
                sql_type = "INT"
        
        # Zeile für SQL formatieren
        sql_columns.append(f"  {col} {sql_type}")

    # Tabelle zusammenbauen
    columns_str = ",\n".join(sql_columns)
    table_name = "bmlpdp_x_me_emea_d.x_usr_dea6rt.vps_metadata"
    
    sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n{columns_str}\n);"
    
    print("\n--- KOPIERE DIESEN BEFEHL IN DEIN DATABRICKS NOTEBOOK ---\n")
    print(sql_query)
    print("\n--------------------------------------------------------\n")

if __name__ == "__main__":
    generate_metadata_sql()