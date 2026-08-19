from dataclasses import dataclass
from datetime import datetime
from dataclasses import asdict

from src.shared.meta_names import MetaNames

@dataclass
class Metadata:
    date:str = ""
    start_time:str = ""
    data_source:str = ""
    oven_nr:str = ""
    oven_recipe:str = ""
    product:str = ""
    load_profile:str = ""
    position_measurement_cooler:str =""
    test_cooler_flag:bool = False
    cooler_count_on_tray:int = 0
    nozzlefield:str = ""
    injection_1:str = ""
    injection_2:str = ""
    injection_3:str = ""
    injection_4:str = ""
    waiting_1:str = ""
    waiting_2:str = ""
    waiting_3:str = ""
    waiting_4:str = ""
    cooling_freq_1:str = ""
    cooling_freq_2:str = ""
    cooling_freq_3:str = ""
    cooling_freq_4:str = ""
    cooling_time_1:str = ""
    cooling_time_2:str = ""
    cooling_time_3:str = ""
    cooling_time_4:str = ""
    profile_name:str = ""
    comment:str = ""
    description:str = ""
    file_name:str = ""
    
    def set_user_input(self, metadata: dict[str,str]):
        
        # set all metadata attributes
        self.oven_recipe = metadata.get(MetaNames.OVEN_RECIPE, "")
        self.oven_nr = metadata.get(MetaNames.OVEN_NR, "")
        self.product = metadata.get(MetaNames.PRODUCT, "")
        self.load_profile = metadata.get(MetaNames.LOAD_PROFILE, "")
        self.position_measurement_cooler = metadata.get(MetaNames.POSITION_MEASUREMENT_COOLER, "")
        
        # check if prod_test is "Test" or "Production" and set testCooler_flag accordingly
        if metadata.get(MetaNames.TEST_COOLER_FLAG, "False").lower() == "test":
            self.test_cooler_flag = True
        else:
            self.test_cooler_flag = False
        
        self.cooler_count_on_tray = int(metadata.get(MetaNames.COOLER_COUNT_ON_TRAY, 0))
        self.nozzlefield = metadata.get(MetaNames.NOZZLEFIELD, "")
        self.injection_1 = metadata.get(MetaNames.INJECTION_1, "")
        self.injection_2 = metadata.get(MetaNames.INJECTION_2, "")
        self.injection_3 = metadata.get(MetaNames.INJECTION_3, "")
        self.injection_4 = metadata.get(MetaNames.INJECTION_4, "")
        self.waiting_1 = metadata.get(MetaNames.WAITING_1, "")
        self.waiting_2 = metadata.get(MetaNames.WAITING_2, "")
        self.waiting_3 = metadata.get(MetaNames.WAITING_3, "")
        self.waiting_4 = metadata.get(MetaNames.WAITING_4, "")
        self.cooling_freq_1 = metadata.get(MetaNames.COOLING_FREQ_1, "")
        self.cooling_freq_2 = metadata.get(MetaNames.COOLING_FREQ_2, "")
        self.cooling_freq_3 = metadata.get(MetaNames.COOLING_FREQ_3, "")
        self.cooling_freq_4 = metadata.get(MetaNames.COOLING_FREQ_4, "")
        self.cooling_time_1 = metadata.get(MetaNames.COOLING_TIME_1, "")
        self.cooling_time_2 = metadata.get(MetaNames.COOLING_TIME_2, "")
        self.cooling_time_3 = metadata.get(MetaNames.COOLING_TIME_3, "")
        self.cooling_time_4 = metadata.get(MetaNames.COOLING_TIME_4, "")
        self.profile_name = metadata.get(MetaNames.PROFILE_NAME, "")
        self.comment = metadata.get(MetaNames.COMMENT, "")
        
    def set_source(self, source:str):
        self.data_source = source
        
    def set_datetime(self,date: datetime):
        self.date = date.strftime("%Y-%m-%d")
        self.start_time = date.strftime("%H:%M:%S")
        
    def get_metadata_dict(self) -> dict:
        return asdict(self)
    
    def set_description(self, description:str):
        self.description = description
        
    def set_file_name(self, file_name:str):
        self.file_name = file_name