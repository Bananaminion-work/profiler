from src.shared.violation import Violation
import pandas as pd
from pandas import DataFrame


class TableFactory:
    
    def update_table(self, violations: list[Violation]):
        """takes in a list of Violations, processes it and returns a DataFrame that can be used to create a table with nicegui and "from_pandas" """
        
        # if there are no violations, return an empty DataFrame to avoid errors in the table creation
        if not violations:
            return DataFrame()
        
        
        # create a Dataframe from the lists of found vioations
        tableContent = DataFrame([violation.to_dict() for violation in violations])
        
        return tableContent