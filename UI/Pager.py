"""
Is supposed to make it easy (in code) to navigate between different pages of the app.
When navigate_to is called, the previous page should end all of its operations and remove its contents and a new one should take its place.
When exit_current_page, the current page is removed, all of its contents are removed and its operations ended.
The ending of operations of course depends on how the specific Page handles the _remove_callback.
"""
from _pyrepl.commands import clear_screen

from PySide6.QtWidgets import QVBoxLayout

from UI.Page import Page


class Pager:
    _parent: QVBoxLayout
    _current_page: Page | None

    def __init__(self, parent: QVBoxLayout):
        self._parent = parent

    def navigate_to(self, page: Page):
        self.exit_current_page()
        if self._current_page is not None:
            page.call_construct(self._parent)

    def exit_current_page(self):
        if self._current_page is not None:
            self._current_page.call_remove()

        clear_screen(self._parent)