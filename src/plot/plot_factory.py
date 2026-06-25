

import importlib
import inspect
from pandas import DataFrame
from src.shared.zeropoint_container import ZeropointContainer

class PlotFactory():
    """class to manage the creation of plots according to the user selections"""
    
    configsDict: dict[str, type]
    
    def __init__(self) -> None:
        self.configsDict = {}
        self._load_configs()
    
    def _load_configs(self):
        # path of the module
        moduleName = "src.plot.plot_configs"
        
        # dynamically import the module
        try:
            configModule = importlib.import_module(moduleName)
            
        except ImportError:
            raise ImportError(f"Module {moduleName} could not be imported.")
        
        # get all classes in the module
        for _, obj in inspect.getmembers(configModule, inspect.isclass):
            if obj.__module__ == moduleName and hasattr(obj, 'configName'):
                self.configsDict[obj.configName] = obj()
                
    
    def create_plot_single(self, data: DataFrame, configName:str, offset:int):
        
        if configName not in self.configsDict:
            raise ValueError(f"Config {configName} not found in PlotFactory.")
        
        # uses the chosen config
        config = self.configsDict[configName]
        
        # apply the offset to the data
        data.index = data.index - offset
        
        # create dict to use config for single and multiple
        dataDict = {"new": data}
        
        # creates the go.Figure object
        return config.build_figure(dataDict)
        
        
       
    def create_plot_multiple(self, dataDict: dict[str, DataFrame], offsetsDict: dict[str,int], configName:str):
        if configName not in self.configsDict:
            raise ValueError(f"Config {configName} not found in PlotFactory.")
        
        # uses the chosen config
        config = self.configsDict[configName]
        
        # dict for the copys
        dataDictCopy = {}
        
        # apply the offsets to the data
        for key, data in dataDict.items():
            
            # create copy of df
            shiftedDf = data.copy()
            
            if key in offsetsDict:
                offset = offsetsDict[key]
                shiftedDf.index = shiftedDf.index - offset
        
            dataDictCopy[key] = shiftedDf
            
            
        # creates the go.Figure object
        return config.build_figure(dataDictCopy)
    
    
    
    def get_available_configs(self) -> list[str]:
        return list(self.configsDict.keys())