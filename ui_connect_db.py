import psycopg2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox


class Ui_Form1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connected = False
        self.db_connection = False
    def setupUi(self, Form1):
        Form1.setObjectName("Form1")
        Form1.resize(275, 215)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("D:\PythonProjects\DesktopApp_Database\database.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form1.setWindowIcon(icon)
        self.form1_btn_connect = QtWidgets.QPushButton(Form1)
        self.form1_btn_connect.setGeometry(QtCore.QRect(40, 170, 91, 23))
        self.form1_btn_connect.setObjectName("form1_btn_connect")
        self.form1_btn_cancel = QtWidgets.QPushButton(Form1)
        self.form1_btn_cancel.setGeometry(QtCore.QRect(140, 170, 91, 23))
        self.form1_btn_cancel.setObjectName("form1_btn_cancel")
        self.widget = QtWidgets.QWidget(Form1)
        self.widget.setGeometry(QtCore.QRect(30, 20, 213, 126))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.form1_host = QtWidgets.QLineEdit(self.widget)
        self.form1_host.setPlaceholderText("")
        self.form1_host.setObjectName("form1_host")
        self.gridLayout.addWidget(self.form1_host, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.form1_bd = QtWidgets.QLineEdit(self.widget)
        self.form1_bd.setObjectName("form1_bd")
        self.gridLayout.addWidget(self.form1_bd, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.form1_user = QtWidgets.QLineEdit(self.widget)
        self.form1_user.setObjectName("form1_user")
        self.gridLayout.addWidget(self.form1_user, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.widget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.form1_pass = QtWidgets.QLineEdit(self.widget)
        self.form1_pass.setObjectName("form1_pass")
        self.gridLayout.addWidget(self.form1_pass, 3, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.form1_port = QtWidgets.QLineEdit(self.widget)
        self.form1_port.setObjectName("form1_port")
        self.gridLayout.addWidget(self.form1_port, 4, 1, 1, 1)

        self.retranslateUi(Form1)
        self.form1_btn_cancel.clicked.connect(Form1.close) # type: ignore
        # self.form1_btn_connect.clicked.connect(Form1.close) # type: ignore
        self.form = Form1
        self.form1_btn_connect.clicked.connect(self.connect_db)
        QtCore.QMetaObject.connectSlotsByName(Form1)

    def retranslateUi(self, Form1):
        _translate = QtCore.QCoreApplication.translate
        Form1.setWindowTitle(_translate("Form1", "Подключение к БД"))
        self.form1_btn_connect.setText(_translate("Form1", "Подключиться"))
        self.form1_btn_cancel.setText(_translate("Form1", "Отмена"))
        self.label.setText(_translate("Form1", "Хост"))
        self.form1_host.setText(_translate("Form1", "localhost"))
        self.label_2.setText(_translate("Form1", "База данных"))
        self.form1_bd.setText(_translate("Form1", "library_db"))
        self.label_3.setText(_translate("Form1", "Пользователь"))
        self.form1_user.setText(_translate("Form1", "postgres"))
        self.label_4.setText(_translate("Form1", "Пароль"))
        self.form1_pass.setText(_translate("Form1", "postgres"))
        self.label_5.setText(_translate("Form1", "Порт"))
        self.form1_port.setText(_translate("Form1", "5432"))

    # Подключение к БД
    def connect_db(self):
        try:
            self.db_connection = psycopg2.connect(
                host=self.form1_host.text(),
                database=self.form1_bd.text(),
                user=self.form1_user.text(),
                password=self.form1_pass.text(),
                port=self.form1_port.text()
            )
        except Exception as er:
            QMessageBox.critical(self, 'Ошибка подключения', f'Ошибка при подключении к базе данных "{self.form1_bd.text()}"')

        # Создаем таблицы persons, books
        try:
            with self.db_connection.cursor() as cursor:
                sql = """
                        CREATE TABLE IF NOT EXISTS books
                        (
                            book_title VARCHAR(100),
                            genre VARCHAR(100) NOT NULL,
                            author VARCHAR(100) NOT NULL,
                            owner VARCHAR(100) NOT NULL,
                            PRIMARY KEY (book_title)
                        );
                        
                        CREATE TABLE IF NOT EXISTS persons
                        (
                            name VARCHAR(100) NOT NULL, 
                            address TEXT NOT NULL,                           
                            book_title VARCHAR(100),
                            visit_date DATE,
                            exp_date DATE
                        );                 
                    """

                cursor.execute(sql)
                self.db_connection.commit()
                self.connected = True
                self.form.close()
        except BaseException as er:
            self.db_connection.rollback()
            QMessageBox.critical(self, 'Ошибка подключения', f'Ошибка при создании таблицы. {er}')
