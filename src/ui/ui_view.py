from src.ui.pages import BasePage
from ipywidgets import Output
from IPython.display import display, clear_output
from src.shared.exceptions import WrongInputError


class UiView:
# Attributes
    _pages : dict[str,BasePage]
    _layout : Output
    
# Functions
    def __init__(self, pages: dict[str,BasePage], layout: Output):
        self._pages = pages
        self._layout = layout


    def switch_page(self, pageName: str):
        pageToShow = self._pages.get(pageName)
        
        if pageToShow:# is available
            
            with self._layout:
                clear_output(wait=True)
                display(pageToShow.layout)
                
        else:
            raise WrongInputError(f"The given string: {pageName} was not found in the dictionary of available pages.")
    
    def get_page(self, pageName:str):
        pageToGet = self._pages.get(pageName)
        
        if pageToGet:
            return pageToGet
        
        else:
            raise WrongInputError(f"The given string: {pageName} was not found")