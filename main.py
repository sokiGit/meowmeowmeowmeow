import sys
from PySide6 import QtWidgets, QtGui

from UI.Pager import Pager
from UI.Pages.SelectIface import SelectIface

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationName("MeowMeowMeowMeow")
    app.setWindowIcon(QtGui.QIcon("Icons/meowmeowmeowmeow.png"))

    widget = MyWidget()
    #widget.manager.request_change_title.connect(lambda txt: widget.setWindowTitle(f"MeowMeowMeowMeow{(" | "+txt) if txt or txt.strip() == "" else ""}"))
    widget.resize(800, 600)
    widget.show()

    pager = Pager(widget.layout)
    pager.navigate_to(SelectIface)

    sys.exit(app.exec())