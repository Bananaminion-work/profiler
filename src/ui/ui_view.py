from src.ui.pages.base_pages import BasePage
from src.shared.exceptions import WrongInputError
from typing import Any

import importlib
from pathlib import Path
import inspect


class UiView:
# Attributes
    _pages : dict[str,BasePage]
    _layout : Any
    _controller : Any
    
# Functions
    def __init__(self, layout: Any, controller: Any):
        self._controller = controller
        self._pages = self._load_pages()
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
        
    def _load_pages(self):
        
        pagesDict = {}
        
        # get direktory
        pagesDir = Path(__file__).parent / "pages"
        
        # find all python files in the pages directory and import them
        for file in pagesDir.glob("*.py"):
            
            # ignore basepages and __init__.py
            if file.name.startswith("base_pages") or file.name == "__init__.py":
                continue
            
            #create module name
            moduleName = f"src.ui.pages.{file.stem}"
            
            #import the module
            module = importlib.import_module(moduleName)
            
            try:
            
                # for any found class
                for _,obj in inspect.getmembers(module, inspect.isclass):
                    
                    # check if the page has a PageName and instaciate
                    if hasattr(obj, 'pageName') and obj.__module__ == moduleName:
                        pagesDict[obj.pageName] = obj(self._controller)
            except Exception as e:
                print(f"Failed to create Page ({moduleName}): {e}")
        
        return pagesDict
    
    def get_pages(self):
        return self._pages