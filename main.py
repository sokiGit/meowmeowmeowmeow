import sys
from PySide6 import QtWidgets, QtGui
from UI.manager import Manager

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.manager = Manager(self.layout)
        self.manager.create_topbar()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationName("MeowMeowMeowMeow")
    app.setWindowIcon(QtGui.QIcon("Icons/meowmeowmeowmeow.png"))

    widget = MyWidget()
    widget.manager.request_change_title.connect(lambda txt: widget.setWindowTitle(f"MeowMeowMeowMeow{(" | "+txt) if txt or txt.strip() == "" else ""}"))
    widget.resize(800, 600)
    widget.show()

    widget.manager.prompt_iface_selection()

    sys.exit(app.exec())