from __future__ import annotations # for forward references in type hints, since AppController also imports BasePage
from abc import ABC, abstractmethod
from nicegui import ui

from typing import TYPE_CHECKING # to avoid circular imports when using type hints, since AppController also imports BasePage
if TYPE_CHECKING:
    from src.ui.appcontroller import AppController


class BasePage(ABC):
    controller: "AppController"

    def __init__(self, controller: "AppController"):
        self.controller = controller

    @abstractmethod
    def render(self, parent: ui.column) -> None:
        pass

    def reset(self) -> None:
        pass


class SubPage(BasePage):
    @abstractmethod
    def build_content(self) -> None:
        pass

    def render(self, parent: ui.column) -> None:
        with parent:
            ui.button(
                "Home",
                icon="home",
                on_click=lambda: self.controller.handle_navigation_request("landing"),
            ).props("outline")
            ui.separator()
            self.build_content()