from src.shared.upload_container import UploadContainer
from src.ui.ui_view import UiView
from src.ui.pages import LandingPage, ImportPage_getData, ImportPage_showData, PlotPage_selectData, PlotPage_showData, Popup_confirm, Popup_warning
from src.shared.data_models import DataComposition
from src.data.data_manager import DataManager
from nicegui import ui
from typing import Any, cast


class AppController:
    
    # Modules:
    
    data : DataManager
    #database : DatabaseTooling
    #plot : PlotManager
    ui : UiView
    
    # Attributes:
    
    current_session_measurement : DataComposition
    terminalContent : Any
    terminalContainer : Any
    pageContainer : Any
    _layout : Any
    pages={}
    
    # Functions:
    
    def __init__(self):
        """
        creates all Pages in a dictionary
        creates the UiView
        creates framework for visual output
        """
        with ui.column().classes("w-full max-w-[1920px] mx-auto") as root:
            self.pageContainer = ui.column().classes("w-full min-h-[720px]")
            ui.separator()
            self.terminalContainer = ui.column().classes("w-full h-24 border p-2 overflow-auto")
        self.terminalContent = self.terminalContainer
        self._layout = root
        
        # create pages dictionary
        self.create_pages()
        
        # create UiView
        self.ui = UiView(self.pages,self.pageContainer)
        
        # create DataManager
        self.data = DataManager()
        
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
        self.data.create_data_from_measurement(uploadContainer, source)
        self.log("here is handle-method: i will call Data-Component to create Data")
        
        
    
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