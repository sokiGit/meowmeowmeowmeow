import UI.Page
"""
Is supposed to make it easy (in code) to navigate between different pages of the app.
When navigate_to is called, the previous page should end all of its operations and remove its contents and a new one should take its place.
When exit_current_page, the current page is removed, all of its contents are removed and its operations ended.
The ending of operations of course depends on how the specific Page handles the _remove_callback.
"""

from UI.Maid import clear_children
from typing import Type

from PySide6.QtWidgets import QVBoxLayout


class Pager:
    _content_layout: QVBoxLayout
    _current_page: UI.Page.Page | None = None

    def __init__(self, parent: QVBoxLayout):
        self._content_layout = parent

    def navigate_to(self, page: Type[UI.Page.Page]):
        from UI.Page import Page

        self.exit_current_page()

        if issubclass(page, Page):
            self._current_page = page(self)
            self._current_page.call_construct()
        else:
            print(f"Error: {page.__name__} is not a subclass of Page.")
            self._current_page = None

    def exit_current_page(self):
        if self._current_page is not None:
            self._current_page.call_remove()

        self._current_page = None

        clear_children(self._content_layout)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout