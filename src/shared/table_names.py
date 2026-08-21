class TableNames():
    """this class contains the table names for Databricks
    
    to migration or first deployment, please change _user to your own nt-user
    
    therefore write "x_usr_<nt-user>" and the paths of the tables will be set automatically"""
    
    _user           = "x_usr_dea6rt"
    
    BRONZE          = f"bmlpdp_x_me_emea_d.{_user}.vps_bronze_measurements"
    SILVER          = f"bmlpdp_x_me_emea_d.{_user}.vps_silver_measurements"
    GOLD            = f"bmlpdp_x_me_emea_d.{_user}.vps_gold_measurements"
    
    METADATA        = f"bmlpdp_x_me_emea_d.{_user}.vps_metadata"
    
    VVT             = f"bmlpdp_x_me_emea_d.{_user}.vps_vvt_limits"
    
    EXCHANGE_SQL    = f"bmlpdp_x_me_emea_d.{_user}.vps_exchange_volume"
    
    EXCHANGE        = f"/Volumes/bmlpdp_x_me_emea_d/{_user}/vps_exchange_volume"