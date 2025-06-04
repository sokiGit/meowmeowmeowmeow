"""
Clears the children after a Page is exited.
"""
from PySide6.QtWidgets import QVBoxLayout


def clear_children(layout: QVBoxLayout):
    for i in reversed(range(layout.count())):
        child = layout.takeAt(i)
        widget = child.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            sub_layout = layout.layout()
            if sub_layout is not None:
                sub_layout.deleteLater()