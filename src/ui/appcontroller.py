from datetime import time

from src.plot.plot_factory import PlotFactory
from src.shared.exceptions import WrongInputError
from src.shared.metadata import Metadata
from src.shared.upload_container import UploadContainer
from src.ui.ui_view import UiView
from src.ui.pages import LandingPage, ImportPage_getData, ImportPage_showData, PlotPage_selectData, PlotPage_showData, Popup_confirm, Popup_warning
from src.shared.data_models import Data, DataComposition
from src.data.data_manager import DataManager
from src.database.database_manager import DatabaseManager
from nicegui import ui
from typing import Any, cast


class AppController:
    
    # Modules:
    
    data : DataManager
    database : DatabaseManager
    plot : PlotFactory
    ui : UiView
    
    # Attributes:
    
    current_session_measurement : DataComposition
    terminalContent : Any
    terminalContainer : Any
    pageContainer : Any
    _layout : Any
    pages={}
    
    # Functions:
    
    def __init__(self, pageContainer, terminalContainer):
        """
        creates all Pages in a dictionary
        creates the UiView
        creates framework for visual output
        """
        #with ui.column().classes("w-full max-w-[1920px] mx-auto") as root:
        #    self.pageContainer = ui.column().classes("w-full min-h-[720px]")
        #    ui.separator()
        #    self.terminalContainer = ui.column().classes("w-full h-24 border p-2 overflow-auto")
        #    
        #self.terminalContent = self.terminalContainer
        #self._layout = root
        
        # assign containers to instance of AppController -> multiple users get their own instance of AppController
        self.pageContainer = pageContainer
        self.terminalContainer = terminalContainer
        self.terminalContent = terminalContainer
        self._layout = pageContainer.parent_slot.parent
            
        # create pages dictionary
        self.create_pages()
        
        # create UiView
        self.ui = UiView(self.pages,self.pageContainer)
        
        # create DataManager
        self.data = DataManager()
        
        # create PlotFactory
        self.plot = PlotFactory()
        
        #create DatabaseManager
        self.database = DatabaseManager()
        
        # instanciate current session measurement with empty data
        self.current_session_measurement = DataComposition()
        
        # show initial page
        self.handle_navigation_request('landing')
    
        
    
    
    def log(self, text: str):
        with self.terminalContent:
            ui.label(text)
        self.terminalContent.update()
    
    
    
    @property
    def layout(self)->Any:
        return self._layout
    
    
    
    def create_pages(self):
        """initiates all pages, also used to clear input-cells after home-navigation
        """
    
        self.pages['landing'] = LandingPage(self)
        self.pages['import-get'] = ImportPage_getData(self)
        self.pages['import-show'] = ImportPage_showData(self)
        self.pages['plot-select'] = PlotPage_selectData(self)
        self.pages['plot-show'] = PlotPage_showData(self)
        self.pages['popup-confirm'] = Popup_confirm(self)
        self.pages['popup-warning'] = Popup_warning(self)



    def handle_navigation_request(self, pageName: str):
        """calls UiView to switch the page\n
        resets user input of the pages
        """
        if pageName == 'landing':
            self.reset_all_pages()
            self.terminalContent.clear()

        self.ui.switch_page(pageName)
        
        
        
    def reset_all_pages(self):
        for pageObject in self.pages.values():
            pageObject.reset()
        
        
        
    def handle_data_import_request(self, uploadContainer: UploadContainer, source:str):
        """creates the medallion objects from input data"""
        
        # if return is valid, medallion objects get structured in current session measurement
        medallionObjects = self.data.create_data_from_measurement(uploadContainer, source)
        
        if isinstance(medallionObjects, dict):
            self.current_session_measurement.set_medallion_data(medallionObjects)
        else:
            raise WrongInputError(f"Expected a dict of Data objects, got {type(medallionObjects)} instead.")
        
        # store the source in metadata
        self.current_session_measurement.get_metadata().set_source(source)
        
    
    def handle_popup(self, type:str, message:str,returnPage:str):
        
        """use type:['confirm','warning']
        enter message to be displayed in popup
        """
        
        if type == 'confirm':
            pageObject=self.ui.get_page('popup-confirm')
            popupObject=cast(Popup_confirm,pageObject)
            popupObject.set_message(message)
            popupObject.set_returnPage(returnPage)
            self.handle_navigation_request('popup-confirm')
            
            
        elif type == 'warning':
            pageObject=self.ui.get_page('popup-warning')
            popupObject=cast(Popup_warning,pageObject)
            popupObject.set_message(message)
            popupObject.set_returnPage(returnPage)
            self.handle_navigation_request('popup-warning')
            
            
    def handle_import_preview(self,config:str):
        goldData = self.current_session_measurement.get_medallion_data().get("gold")
        if isinstance(goldData, Data):
            ui.plotly(self.plot.create_plot(goldData.get_dataframe(), config)).classes("w-full h-full")
        else:
            raise WrongInputError(f"Expected a Data object for gold data, got {type(goldData)} instead.")
        
    def handle_save_request(self, metadata: dict[str,str], chosenZeropoints):
                
        # set metadata for current session measurement
        self.current_session_measurement.get_metadata().set_user_input(metadata)
        
        # check if current session objects are valid
        for data in self.current_session_measurement.get_medallion_data().values():
            if not isinstance(data, Data):
                raise WrongInputError(f"Expected a Data object in medallion array, got {type(data)} instead.")
            
        if not isinstance(self.current_session_measurement.get_metadata(), Metadata):
            raise WrongInputError(f"Expected a Metadata-object in current session, got {type(self.current_session_measurement.get_metadata())} instead.")
        
        # create final gold object with zeropoints and set it in current session measurement
        finalGoldObject = self.data.create_final_data(chosenZeropoints)
        if not isinstance(finalGoldObject, Data):
            raise WrongInputError(f"Expected a Data object for final gold data, got {type(finalGoldObject)} instead.")
        
        else:
            self.current_session_measurement.set_final_gold_object(finalGoldObject)
        
        # save measurement to database
        self.database.save_measurement(self.current_session_measurement)
        ui.notify("Measurement saved successfully!", color="green")
        
        # reset current session after saving
        self.current_session_measurement = DataComposition()
        self.handle_navigation_request('landing')
        