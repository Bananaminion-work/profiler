from nicegui import ui
from typing import Literal

NotifyLevel = Literal['positive', 'warning', 'negative', 'info', 'ongoing']

class WarningCollector:

    
    def __init__(self):
        self.warnings: list[tuple[str,NotifyLevel]] = []
        
        
    def warn(self, msg:str, level:NotifyLevel = "negative"):
        """adds a warning to the list of warnings"""
        self.warnings.append((msg, level))
        
    
    def flush(self):
        """clears the list of warnings"""
        for  msg, level in self.warnings:
            ui.notify(msg, type= level)
        self.warnings.clear()
            