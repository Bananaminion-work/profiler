

import importlib
import inspect


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
                
    
    def create_plot(self, data, configName:str):
        
        if configName not in self.configsDict:
            raise ValueError(f"Config {configName} not found in PlotFactory.")
        
        config = self.configsDict[configName]
        return config.build_figure(data)
        
        
            