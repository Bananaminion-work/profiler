class Metadata:
    date:str
    startTime:int
    dataSource:str
    ovenNr:int
    product:str
    loadProfile:float
    positionMeasurementCooler:str
    testCooler_flag:bool
    coolerCountOnTray:int
    nozzlefield:str
    injectionAmount:dict[str, float]
    waitingTime:dict[str, float]
    coolingFrequency:dict[str, float]
    coolingTime:dict[str, float]
    profileName:str
    comment:str
    