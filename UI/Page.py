import UI
"""
Works with the Pager to provide an easily manageable way to show/hide/navigate pages.
call_construct makes the page show up (everything needs to be instantiated)
call_remove makes the page disappear (everything is forcibly removed if not taken care of by _remove_callback)
"""
from typing import Callable

from PySide6.QtWidgets import QVBoxLayout

from UI.Maid import clear_children


class Page:
    _construct_callback: Callable[[], None]
    _remove_callback: Callable[[], None]
    _pager: 'UI.Pager.Pager'
    _parent: QVBoxLayout
    def __init__(self, pager: 'UI.Pager.Pager'):
        self._pager = pager
        self._parent = pager.content_layout
        self._is_constructed = False

    _is_constructed: bool

    def _construct_callback(self):
        pass

    def _remove_callback(self):
        pass

    def call_construct(self):
        """
        Calls the _construct_callback which is supposed to instantiate new widgets inside the :param parent:.
        Sets _content_layout to :param parent: for the self.call_remove function to be able to remove all children.
        """
        self._construct_callback()

        self._is_constructed = True

    def call_remove(self):
        """
        Calls self._remove_callback() which is supposed to safely remove all the children and disconnect all events.
        To make sure no stray children remain, the function attempts to forcibly remove any remaining children.
        """
        self._remove_callback()

        if self._is_constructed and self._parent is not None:
            clear_children(self._parent)

        self._is_constructed = False