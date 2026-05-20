from src.ui.pages import BasePage
from nicegui import ui
from src.shared.exceptions import WrongInputError
from typing import Any


class UiView:
# Attributes
    _pages : dict[str,BasePage]
    _layout : Any
    
# Functions
    def __init__(self, pages: dict[str,BasePage], layout: Any):
        self._pages = pages
        self._layout = layout


    def switch_page(self, pageName: str):
        pageToShow = self._pages.get(pageName)
        
        if pageToShow:# is available
            self._layout.clear()
            with self._layout:
                pageToShow.render(self._layout)
                
        else:
            raise WrongInputError(f"The given string: {pageName} was not found in the dictionary of available pages.")
    
    def get_page(self, pageName:str):
        pageToGet = self._pages.get(pageName)
        
        if pageToGet:
            return pageToGet
        
        else:
            raise WrongInputError(f"The given string: {pageName} was not found")