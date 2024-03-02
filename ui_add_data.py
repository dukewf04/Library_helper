from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox


class Ui_form2(QMainWindow):
    def __init__(self, db_connection):
        self.db_connection = db_connection
        super().__init__()
    def setupUi(self, form2):
        form2.setObjectName("form2")
        form2.resize(510, 100)
        form2.setMinimumSize(QtCore.QSize(510, 130))
        form2.setMaximumSize(QtCore.QSize(99999, 130))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("D:\PythonProjects\DesktopApp_Database\database.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        form2.setWindowIcon(icon)
        self.form2_ = form2
        self.verticalLayout = QtWidgets.QVBoxLayout(form2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.form2_row_data = QtWidgets.QTableWidget(form2)
        self.form2_row_data.setMaximumSize(QtCore.QSize(16777215, 80))
        self.form2_row_data.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.form2_row_data.setObjectName("form2_row_data")
        self.form2_row_data.setColumnCount(0)
        self.form2_row_data.setRowCount(0)
        self.form2_row_data.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.form2_row_data)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.form2_btn_add = QtWidgets.QPushButton(form2)
        self.form2_btn_add.setMaximumSize(QtCore.QSize(100, 16777215))
        self.form2_btn_add.setObjectName("form2_btn_add")
        self.horizontalLayout.addWidget(self.form2_btn_add)
        self.form2_btn_cancel = QtWidgets.QPushButton(form2)
        self.form2_btn_cancel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.form2_btn_cancel.setObjectName("form2_btn_cancel")
        self.horizontalLayout.addWidget(self.form2_btn_cancel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(form2)
        self.form2_btn_cancel.clicked.connect(form2.close) # type: ignore
        self.form2_btn_add.clicked.connect(self.save_field_in_table)
        QtCore.QMetaObject.connectSlotsByName(form2)

    def retranslateUi(self, form2, tablename='table'):
        self.tablbe_name = tablename
        self.add_data = False
        _translate = QtCore.QCoreApplication.translate
        form2.setWindowTitle(_translate("form2", f'Добавить запись в таблицу {tablename}'))
        self.form2_btn_add.setText(_translate("form2", "Добавить"))
        self.form2_btn_cancel.setText(_translate("form2", "Отмена"))

    # Метод для задания колонок таблицы, при создании новой записи
    def set_table_columns(self, col_list: list):
        self.col_count = len(col_list)
        self.form2_row_data.setColumnCount(len(col_list))
        self.form2_row_data.setHorizontalHeaderLabels(col_list)
        self.form2_row_data.removeRow(0)
        self.form2_row_data.insertRow(0)
        for i in range(len(col_list)):
            self.form2_row_data.setItem(0, i, QTableWidgetItem(''))

    # Добавить новое поле в таблицу
    def save_field_in_table(self):
        self.data_list = [f"'{self.form2_row_data.item(0, i).text()}'" for i in range(self.col_count)]
        sql = f"""INSERT INTO "{self.tablbe_name}"
        VALUES ({', '.join(self.data_list)});
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(sql)
                self.db_connection.commit()
                self.add_data = True
                self.form2_.close()
        except Exception as er:
            self.db_connection.rollback()
            QMessageBox.critical(self, 'Error', f'Ошибка при добавлении записи в таблицу:\n\n{er}')
