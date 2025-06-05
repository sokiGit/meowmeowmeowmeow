from PySide6.QtCore import Signal, QObject

import UI
"""
Works with the Pager to provide an easily manageable way to show/hide/navigate pages.
call_construct makes the page show up (everything needs to be instantiated)
call_remove makes the page disappear (everything is forcibly removed if not taken care of by _remove_callback)
"""
from typing import Callable

from PySide6.QtWidgets import QVBoxLayout

from UI.Maid import clear_children


class Page(QObject):
    _construct_callback: Callable[[], None]
    _remove_callback: Callable[[], None]
    _pager: 'UI.Pager.Pager'
    _parent: QVBoxLayout
    _is_constructed: bool
    change_title: Signal(str)

    def __init__(self, pager: 'UI.Pager.Pager'):
        super().__init__()
        self._pager = pager
        self._parent = pager.content_layout
        self._is_constructed = False
        self.change_title = pager.change_title

    def _construct_callback(self):
        """
        Instantiate new objects and place them as descendants of self._parent.
        Keep track of any stray threads/bits of code that keep running after all the objects have been removed.
        Terminate such processes inside self._remove_callback.
        Objects inside self._parent are removed automatically along with their connections.
        """
        pass

    def _remove_callback(self):
        """
        Stop any independently-running code (e.g.: threads, other objects, etc.).
        Remove any objects that aren't descendants of self._parent.
        Objects placed inside self._parent are automatically removed, which also removes any connections tied to those
        objects.
        """
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