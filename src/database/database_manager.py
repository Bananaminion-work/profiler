from src.shared.data_models import DataComposition
from nicegui import ui

class DatabaseManager:

    def save_measurement(self, measurement: DataComposition):
        """saves the measurement to the database"""
        ui.notify("function to save measurement was called... wait to be implemented", color="orange")
        pass