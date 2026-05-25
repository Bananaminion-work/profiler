from src.shared.data_composition import DataComposition
from nicegui import ui

class DatabaseManager:
    
    def connect_to_database(self):
        """connects to the database"""
        ui.notify("function to connect to database was called... wait to be implemented", color="orange")
        
    def disconnect_from_database(self):
        """disconnects from the database"""
        ui.notify("function to disconnect from database was called... wait to be implemented", color="orange")

    def save_measurement(self, measurement: DataComposition):
        """saves the measurement to the database"""
        ui.notify("function to save measurement was called... wait to be implemented", color="orange")
    
    def load_vvt(self)-> dict[str, dict[str, str]]:
        """loads the vvt from the database"""
        ui.notify("function to load vvt was called... wait to be implemented", color="orange")
        
        
        
        # TODO: ausgelesene vvt werte aus DB übergeben
        return dict[str, dict[str, str]]()