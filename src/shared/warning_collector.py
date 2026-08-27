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
            
            # if the warning is a negative one, show it as a notification
            if level in ["negative","warning"]:
                ui.notify(
                    msg,
                    type= level,
                    timeout=10000,
                    multi_line=True,
                    close_button='OK'
                )
                
            else:
                ui.notify(
                    msg,
                    type= level,
                    close_button='OK'
                )
            
        self.warnings.clear()