from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt


class TableView(QtWidgets.QTableWidget):
    enterPressed = Signal()

    def __init__(self, columns: int, description: list[str], /):
        '''
            Easier handling for displaying info in a table.
            TableView.table is the actual QTableWidget object.
        '''
        super().__init__(1, columns)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        self.setHorizontalHeaderLabels(description)

        for col_index in range(columns):
            self.horizontalHeader().setSectionResizeMode(col_index, QtWidgets.QHeaderView.ResizeMode.Interactive if col_index != columns-1 else QtWidgets.QHeaderView.ResizeMode.Stretch)

        self._arrow_selection_allowed = False

    def keyPressEvent(self, event, /):
        if event.key() == Qt.Key.Key_Return:
            self.enterPressed.emit()
        elif event.key() == Qt.Key.Key_Down:
            self.selectRow(min(self.selectedIndexes()[0].row()+1, self.rowCount()-1))
        elif event.key() == Qt.Key.Key_Up:
            self.selectRow(max(self.selectedIndexes()[0].row()-1, 0))

    def add_row(self, fields : list[str]):
        '''
            Adds a row with the list of strings as row items, e.g.: ["8.8.8.8", "53", "UDP"]
            Returns the row_index at which these were inserted.
        '''
        row_count = self.rowCount()
        row_index = 0

        # Utilize empty rows at end or create new row
        for i in reversed(range(row_count)):
            is_empty = self.is_row_empty(i)

            if not is_empty:
                row_index = i+1
                if i == row_count-1:
                    self.insertRow(row_count)
                break

        i = 0
        for field in fields:
            self.create_item(field, row_index, i)
            i += 1
        
        return row_index
    
    def modify_item(self, row : int, col : int, new_text : str):
        '''
            Sets the text of the item at the specified row, col coordinates to new_text.
            Useful with TableView.addRow which returns the index of the added row.
        '''
        self.item(row, col).setText(new_text)


    def create_item(self, text : str, row_index : int, col_index : int):
        '''
            Creates a new text item at specified coordinates.
        '''
        item = QtWidgets.QTableWidgetItem()
        item.setText(text)
        self.setItem(row_index, col_index, item)

    def is_row_empty(self, row_index : int):
        '''
            Checks whether row at row_index is empty or has empty strings
        '''
        col_count = self.columnCount()

        for col_index in range(col_count):
            item = self.item(row_index, col_index)
            if item is not None and item.text().strip() != "":
                return False
        
        return True
