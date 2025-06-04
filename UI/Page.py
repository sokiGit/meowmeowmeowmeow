"""
Works with the Pager to provide an easily manageable way to show/hide/navigate pages.
call_construct makes the page show up (everything needs to be instantiated)
call_remove makes the page disappear (everything is forcibly removed if not taken care of by _remove_callback)
"""
from typing import Callable

from PySide6.QtWidgets import QVBoxLayout

from UI.Maid import clear_children


class Page:
    _construct_callback: Callable[[QVBoxLayout], None]
    _remove_callback: Callable[[], None]
    _current_parent: QVBoxLayout | None

    def __init__(self, construct_callable: Callable[[QVBoxLayout], None], remove_callable: Callable[[], None]):
        self._construct_callback = construct_callable
        self._remove_callback = remove_callable

    def call_construct(self, parent: QVBoxLayout):
        """
        Calls the _construct_callback which is supposed to instantiate new widgets inside the :param parent:.
        Sets _current_parent to :param parent: for the self.call_remove function to be able to remove all children.
        """
        self._current_parent = parent
        self._construct_callback(parent)

    def call_remove(self):
        """
        Calls self._remove_callback() which is supposed to safely remove all the children and disconnect all events.
        To make sure no stray children remain, the function attempts to forcibly remove any remaining children.
        """
        self._remove_callback()
        if self._current_parent is not None:
            clear_children(self._current_parent)

        self._current_parent = None