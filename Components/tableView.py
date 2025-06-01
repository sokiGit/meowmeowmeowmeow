from PySide6 import QtWidgets

class TableView():
    def __init__(self, columns : int, description : [str]):
        '''
            Easier handling for displaying info in a table.
            TableView.table is the actual QTableWidget object.
        '''
        self.table = QtWidgets.QTableWidget(1, columns)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        self.table.setHorizontalHeaderLabels(description)

        for col_index in range(columns):
            self.table.horizontalHeader().setSectionResizeMode(col_index, QtWidgets.QHeaderView.ResizeMode.Interactive if col_index != columns-1 else QtWidgets.QHeaderView.ResizeMode.Stretch)

    def addRow(self, fields : [str]):
        '''
            Adds a row with the list of strings as row items, e.g.: ["8.8.8.8", "53", "UDP"]
            Returns the row_index at which these were inserted.
        '''
        row_count = self.table.rowCount()
        row_index = 0

        # Utilize empty rows at end or create new row
        for i in reversed(range(row_count)):
            is_empty = self.isRowEmpty(i)

            if not is_empty:
                row_index = i+1
                if i == row_count-1:
                    self.table.insertRow(row_count)
                break

        i = 0
        for field in fields:
            self.createItem(field, row_index, i)
            i += 1
        
        return row_index
    
    def modifyItem(self, row : int, col : int, new_text : str):
        '''
            Sets the text of the item at the specified row, col coordinates to new_text.
            Useful with TableView.addRow which returns the index of the added row.
        '''
        self.table.item(row, col).setText(new_text)


    def createItem(self, text : str, row_index : int, col_index : int):
        '''
            Creates a new text item at specified coordinates.
        '''
        item = QtWidgets.QTableWidgetItem()
        item.setText(text)
        self.table.setItem(row_index, col_index, item)

    def isRowEmpty(self, row_index : int):
        '''
            Checks whether row at row_index is empty or has empty strings
        '''
        col_count = self.table.columnCount()

        for col_index in range(col_count):
            item = self.table.item(row_index, col_index)
            if item is not None and item.text().strip() != "":
                return False
        
        return True