from src.ui.ui_view import UiView
from src.ui.pages import LandingPage, ImportPage_getData, ImportPage_showData, PlotPage_selectData, PlotPage_showData
from src.shared.data_models import DataComposition, Data, Metadata
import ipywidgets as widgets
from ipywidgets import Output, Layout, VBox


class AppController:
    
# Modules
    #data : DataManager
    #database : DatabaseTooling
    #plot : PlotManager
    ui : UiView
    
# Attributes
    current_session_measurement : DataComposition
    terminalContent : Output
    terminalContainer : VBox
    pageContainer : Output
    _layout : VBox
    
# Functions
    def __init__(self):
        """
        creates all Pages in a dictionary
        creates the UiView
        creates framework for visual output
        """
        # create boxes
        self.terminalContent = Output()
        self.pageContainer = Output()
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
        pages = {
            'landing' : LandingPage(self),
            'import-get' : ImportPage_getData(self),
            'import-show' : ImportPage_showData(self),
            'plot-select' : PlotPage_selectData(self),
            'plot-show' : PlotPage_showData(self)
        }
        
        # create UiView
        self.ui = UiView(pages,self.pageContainer)
        
        # show initial page
        self.handle_navigation_request('landing')
        

    def handle_navigation_request(self,pageName:str):
        self.terminalContent.clear_output()
        self.ui.switch_page(pageName)
        
    def handle_data_import_request(self):
        self.log("here is handle-method: i will call Data-Component to create Data")
        
    def log(self, text:str):
        with self.terminalContent:
            print(f"{text}")
    
    @property
    def layout(self)->VBox:
        return self._layout