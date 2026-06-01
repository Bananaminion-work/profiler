from dataclasses import dataclass
from datetime import datetime
from dataclasses import asdict

@dataclass
class Metadata:
    date:str = ""
    startTime:str = ""
    dataSource:str = ""
    ovenNr:int = 0
    product:str = ""
    loadProfile:float = 0.0
    positionMeasurementCooler:str =""
    testCooler_flag:bool = False
    coolerCountOnTray:int = 0
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
    profileName:str = ""
    comment:str = ""
    
    def set_user_input(self, metadata: dict[str,str]):
        
        # set all metadata attributes
        self.ovenNr = int(metadata.get("ovenNr", 0))
        self.product = metadata.get("product", "")
        self.loadProfile = float(metadata.get("loadProfile", 0.0))
        self.positionMeasurementCooler = metadata.get("positionMeasurementCooler", "")
        
        # check if prod_test is "Test" or "Production" and set testCooler_flag accordingly
        if metadata.get("prod_test", "False").lower() == "test":
            self.testCooler_flag = True
        else:
            self.testCooler_flag = False
        
        self.coolerCountOnTray = int(metadata.get("coolerCountOnTray", 0))
        self.nozzlefield = metadata.get("nozzlefield", "")
        self.injection_1 = metadata.get("injection_1", "")
        self.injection_2 = metadata.get("injection_2", "")
        self.injection_3 = metadata.get("injection_3", "")
        self.injection_4 = metadata.get("injection_4", "")
        self.waiting_1 = metadata.get("waiting_1", "")
        self.waiting_2 = metadata.get("waiting_2", "")
        self.waiting_3 = metadata.get("waiting_3", "")
        self.waiting_4 = metadata.get("waiting_4", "")
        self.cooling_freq_1 = metadata.get("cooling_freq_1", "")
        self.cooling_freq_2 = metadata.get("cooling_freq_2", "")
        self.cooling_freq_3 = metadata.get("cooling_freq_3", "")
        self.cooling_freq_4 = metadata.get("cooling_freq_4", "")
        self.cooling_time_1 = metadata.get("cooling_time_1", "")
        self.cooling_time_2 = metadata.get("cooling_time_2", "")
        self.cooling_time_3 = metadata.get("cooling_time_3", "")
        self.cooling_time_4 = metadata.get("cooling_time_4", "")
        self.profileName = metadata.get("profileName", "")
        self.comment = metadata.get("comment", "")
        
    def set_source(self, source:str):
        self.dataSource = source
        
    def set_datetime(self,date: datetime):
        self.date = date.strftime("%Y-%m-%d")
        self.startTime = date.strftime("%H:%M:%S")
        
    def get_metadata_dict(self) -> dict:
        return asdict(self)