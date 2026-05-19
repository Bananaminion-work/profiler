from src.ui.ui_view import UiView
from src.ui.pages import BasePage,LandingPage, ImportPage_getData, ImportPage_showData, PlotPage_selectData, PlotPage_showData, Popup_confirm, Popup_warning
from src.shared.data_models import DataComposition, Data, Metadata
import ipywidgets as widgets
from ipywidgets import Output, Layout, VBox
from typing import cast


class AppController:
    
    # Modules:
    
    #data : DataManager
    #database : DatabaseTooling
    #plot : PlotManager
    ui : UiView
    
    # Attributes:
    
    current_session_measurement : DataComposition
    terminalContent : Output
    terminalContainer : VBox
    pageContainer : Output
    _layout : VBox
    pages={}
    
    # Functions:
    
    def __init__(self):
        """
        creates all Pages in a dictionary
        creates the UiView
        creates framework for visual output
        """
        # create boxes
        self.terminalContent = Output()
        pageContainer_layout=Layout(
            max_width='1920px',
            min_width='1200px',
            max_height='1080px',
            min_height='720px',
            overflow='auto',
            justify_content='center',
            align_items='center'
        )
        self.pageContainer = Output(layout=pageContainer_layout)
        self.terminalContainer = VBox()
        
        # create layout to make terminal scrollable
        terminal_layout = Layout(
            width='100%',
            height='80px',
            border='1px solid grey',
            padding='5px',
            overflow_y='auto'
        )
        
        # boxing
        self.terminalContainer = VBox(
            [self.terminalContent], layout=terminal_layout
        )        
        
        self._layout = VBox(
            [self.pageContainer, self.terminalContainer]
        )
        
        # create pages dictionary
        self.create_pages()
        
        # create UiView
        self.ui = UiView(self.pages,self.pageContainer)
        
        # show initial page
        self.handle_navigation_request('landing')
    
        
    
    
    def log(self, text:str):
        with self.terminalContent:
            print(f"{text}")
    
    
    
    @property
    def layout(self)->VBox:
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



    def handle_navigation_request(self,pageName:str):
        """calls UiView to switch the page\n
        resets user input of the pages
        """
        if pageName=='landing':
            self.reset_all_pages()
        
        self.terminalContent.clear_output()
        self.ui.switch_page(pageName)
        
        
        
    def reset_all_pages(self):
        for pageObject in self.pages.values():
            pageObject.reset()
        
        
        
    def handle_data_import_request(self):
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