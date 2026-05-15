class Metadata:
    date:str
    ovenNr:int
    startTime:int
    profileName:str

    def __init__(self, date:str, ovenNr:int, startTime:int, profileName:str):
        self.date = date
        self.ovenNr = ovenNr
        self.startTime = startTime
        self.profileName = profileName
        
    def get_date(self)->str:
        return self.date
    
    def get_ovenNr(self)->int:
        return self.ovenNr
    
    def get_startTime(self)->int:
        return self.startTime
    
    def get_profileName(self)->str:
        return self.date
    