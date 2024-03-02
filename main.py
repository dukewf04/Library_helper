# pyinstaller --onefile --noconsole --icon "D:\libraryGUI_temp\database.ico" main.py

import sys
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem, QTableWidgetItem, QDialog
import psycopg2
from ui_main import *
from ui_connect_db import *
from ui_add_data import *
from datetime import datetime as dt
import json
from geopy.geocoders import Nominatim


class GUI(QMainWindow, Ui_MainWindow):
    # Вспомогательные данные таблиц (tname - имя таблицы, data - список записей, column_list - структура таблицы)
    __table_list = {
        'books': {
            'tname': 'books',
            'data': [],
            'column_list': []
        },
        'persons': {
            'tname': 'persons',
            'data': [],
            'column_list': []
        }
    }

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection

        self.ui = QDialog()
        self.ui_form2 = Ui_form2(db_connection)
        self.ui_form2.setupUi(self.ui)
        self.setupUi(self)
        self.btn_examples.clicked.connect(self.create_example_data)

        # Кнопки на вкладке Список книг
        self.btn_add_data_ext.clicked.connect(lambda: self.add_data_ext(
                tname=self.__table_list['books']['tname'],
                field_list=[self.book_list.horizontalHeaderItem(i).text() for i in range(self.book_list.columnCount())])
                                              )
        self.btn_clear_data_ext.clicked.connect(lambda: self.delete_data(twidget=self.book_list, tname=self.__table_list['books']['tname']))
        self.btn_save_data_ext.clicked.connect(lambda: self.save_data(twidget=self.book_list, tname=self.__table_list['books']['tname']))

        # Кнопки на вкладке Список читателей
        self.btn_add_persons.clicked.connect(lambda: self.add_data_ext(
                tname=self.__table_list['persons']['tname'],
                field_list=[self.person_list.horizontalHeaderItem(i).text() for i in range(self.person_list.columnCount())])
                                              )
        self.btn_delete_persons.clicked.connect(lambda: self.delete_data(twidget=self.person_list, tname=self.__table_list['persons']['tname']))
        self.btn_save_persons.clicked.connect(lambda: self.save_data(twidget=self.person_list, tname=self.__table_list['persons']['tname']))

        # Кнопки на вкладке Отчеты
        self.btn_show_report.clicked.connect(self.show_report)
        self.btn_expiration_date.clicked.connect(self.books_expiration_date)
        self.btn_books_location.clicked.connect(self.get_books_location)

        self.load_field_tables()
        self.show_table_fields(self.__table_list['books']['tname'])
        self.show_table_fields(self.__table_list['persons']['tname'])
        self.save_data_books()
        self.save_data_persons()

    # Запрос к базе данных (sql - запрос, err_msg - текст ошибки)
    def sql_query(self, sql: str, err_msg: str):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
                self.db_connection.commit()
                return res
        except Exception as er:
            self.db_connection.rollback()
            QMessageBox.critical(self, 'Error', f'{err_msg}:\n\n{er}')
            return False

    # Загружаем структуру таблиц books и visitors
    def load_field_tables(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{self.__table_list['books']['tname']}' ORDER BY ORDINAL_POSITION")
            data = cursor.fetchall()
            self.__table_list['books']['column_list'] = [f"\"{name[0]}\"" for name in data]

            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{self.__table_list['persons']['tname']}' ORDER BY ORDINAL_POSITION")
            data = cursor.fetchall()
            self.__table_list['persons']['column_list'] = [f"\"{name[0]}\"" for name in data]

    # Вспомогательная функция для сохранения списка записей в таблице books
    def save_data_books(self):
        if self.book_list.rowCount() > 0:
            self.__table_list['books']['data'] = []
            for row in range(self.book_list.rowCount()):
                self.__table_list['books']['data'].append([f"'{self.book_list.item(row, col).text()}'" for col in range(self.book_list.columnCount())])

    # Вспомогательная функция для сохранения списка записей в таблице persons
    def save_data_persons(self):
        if self.person_list.rowCount() > 0:
            self.__table_list['persons']['data'] = []
            for row in range(self.person_list.rowCount()):
                self.__table_list['persons']['data'].append([f"'{self.person_list.item(row, col).text()}'" for col in range(self.person_list.columnCount())])

    # Загрузка полей, данных выбранной таблицы
    def show_table_fields(self, tname: str):
        if tname == self.__table_list['persons']['tname']:
            data = self.sql_query(sql=f"SELECT * FROM \"{tname}\" ORDER BY visit_date", err_msg="Ошибка при загрузке данных таблицы")
        else:
            data = self.sql_query(sql=f"SELECT * FROM \"{tname}\"", err_msg="Ошибка при загрузке данных таблицы")
        if not data: return False

        if tname == self.__table_list['books']['tname']:
            for i in range(len(data)):
                self.book_list.insertRow(i)
                for j in range(len(data[i])):
                    self.book_list.setItem(i, j, QTableWidgetItem(str(data[i][j])))
        else:
            for i in range(len(data)):
                self.person_list.insertRow(i)
                for j in range(len(data[i])):
                    self.person_list.setItem(i, j, QTableWidgetItem(str(data[i][j])))


        if self.book_list.rowCount() > 0:
            self.btn_clear_data_ext.setEnabled(True)
        else:
            self.btn_clear_data_ext.setEnabled(False)

        if self.person_list.rowCount() > 0:
            self.btn_delete_persons.setEnabled(True)
        else:
            self.btn_delete_persons.setEnabled(False)

    # Добавление данных в существующую таблицу
    def add_data_ext(self, tname: str, field_list: list):
        self.ui_form2.retranslateUi(self.ui, tablename=tname)
        self.ui_form2.set_table_columns(field_list)
        self.ui.exec_()

        if self.ui_form2.add_data:
            if tname == self.__table_list['books']['tname']:
                self.book_list.insertRow(self.book_list.rowCount())
                for i in range(self.book_list.columnCount()):
                    self.book_list.setItem(self.book_list.rowCount()-1, i, QTableWidgetItem(self.ui_form2.data_list[i][1:-1]))
            else:
                self.person_list.insertRow(self.person_list.rowCount())
                for i in range(self.person_list.columnCount()):
                    self.person_list.setItem(self.person_list.rowCount()-1, i, QTableWidgetItem(self.ui_form2.data_list[i][1:-1]))

            self.btn_clear_data_ext.setEnabled(True)
            self.btn_save_persons.setEnabled(True)
            self.btn_delete_persons.setEnabled(True)
            self.statusbar.showMessage(f'Запись успешно добавлена в таблицу {tname}', 2000)
            self.save_data_books()
            self.save_data_persons()

    # Удалить данные из таблицы
    def delete_data(self, twidget, tname: str):
        if twidget.rowCount() > 0:
            selected_rows = twidget.selectionModel().selectedRows()
            lst = [selected_rows[i].row() for i in range(len(selected_rows))]
            lst.sort(reverse=True)
            try:
                with self.db_connection.cursor() as cursor:
                    for row in lst:
                        field_list = [f"{self.__table_list[tname]['column_list'][col]}={self.__table_list[tname]['data'][row][col]}" for col in
                             range(twidget.columnCount())]

                        sql = f"""DELETE FROM {tname}
                                  WHERE {" AND ".join(field_list)}
                        """

                        cursor.execute(sql)
                        self.db_connection.commit()

                        twidget.removeRow(row)

                        self.statusbar.showMessage(f'Записи таблицы {tname} успешно удалены', 2000)
                self.save_data_books()
                self.save_data_persons()

                if self.book_list.rowCount() == 0:
                    self.btn_clear_data_ext.setEnabled(False)
                if self.person_list.rowCount() == 0:
                    self.btn_delete_persons.setEnabled(False)
            except Exception as er:
                self.db_connection.rollback()
                QMessageBox.critical(self, 'Error', f'Ошибка при удалении записей из таблицы {tname}:\n\n{er}')

    # Сохранение изменений записей в таблицах
    def save_data(self, twidget, tname: str):
        if twidget.rowCount() > 0:
            try:
                with self.db_connection.cursor() as cursor:
                    for row in range(twidget.rowCount()):
                        field_list = [f"{self.__table_list[tname]['column_list'][col]}='{twidget.item(row, col).text()}'" for col in
                             range(twidget.columnCount())]

                        last_field_list = [f"{self.__table_list[tname]['column_list'][col]}={self.__table_list[tname]['data'][row][col]}" for col in
                             range(twidget.columnCount())]

                        sql = f"""UPDATE {tname}
                                  SET {", ".join(field_list)}
                                  WHERE {" AND ".join(last_field_list)}
                        """
                        cursor.execute(sql)
                        self.db_connection.commit()

                        self.statusbar.showMessage(f'Записи таблицы {tname} успешно изменены', 2000)
                self.save_data_books()
                self.save_data_persons()
            except Exception as er:
                self.db_connection.rollback()
                QMessageBox.critical(self, 'Error', f'Ошибка при редактировании записей таблицы {tname}:\n\n{er}')

    # Создаем тестовые записи во все таблицы
    def create_example_data(self):
        sql = f"""DELETE FROM {self.__table_list['books']['tname']};
                  DELETE FROM {self.__table_list['persons']['tname']};
                  
                    INSERT INTO {self.__table_list['books']['tname']}
                    VALUES
                    ('Мастер и маргарита', 'Фантастика', 'Михаил Булгаков', 'Библиотека'),
                    ('Лолита', 'Роман', 'Владимир Набоков', 'Библиотека'),
                    ('Звук и ярость', 'Роман', 'Уильям Фолкнер', 'Егор Сеченов'),
                    ('Человек-невидимка', 'Научная фантастика', 'Герберт Уэллс', 'Максим Колачев'),
                    ('Война и мир', 'историческая проза', 'Лев Толстой', 'Алена Желтовских'),
                    ('Преступление и наказание', 'Детектив', 'Федор Достоевский', 'Библиотека'),
                    ('1984', 'Фантастика', 'Джордж Оруэлл', 'Денис Назаров'),
                    ('Анна Каренина', 'драма', 'Лев Толстой', 'Денис Назаров'),                                                            
                    ('Гордость и предубеждение', 'Сатира', 'Джейн Остен', 'Денис Назаров');
                    
                    INSERT INTO {self.__table_list['persons']['tname']}
                    VALUES
                    ('Александр Попов', 'ул. Мичурина, д. 12, Самара', 'Звук и ярость', '2023-02-28', '2023-03-20'),                  
                    ('Денис Назаров', 'пр. Кирова, д. 95, Самара', 'Анна Каренина', '2023-03-25', '2023-03-27'),
                    ('Денис Назаров', 'пр. Кирова, д. 95, Самара', '1984', '2023-04-25', '2023-05-30'),
                    ('Егор Сеченов', 'ул. Гагарина, д. 7, Самара', 'Звук и ярость', '2023-06-06', '2023-07-15'),
                    ('Максим Колачев', 'ул. Красноармейская, д. 88, Самара', 'Человек-невидимка', '2023-07-25', '2023-08-01'),
                    ('Максим Колачев', 'ул. Красноармейская, д. 88, Самара', 'Мастер и маргарита', '2023-08-13', '2023-08-20'),
                    ('Алена Желтовских', 'ул. Советская, д. 14, Самара', 'Война и мир', '2024-01-20', '2024-02-15'),                                 
                    ('Денис Назаров', 'пр. Кирова, д. 95, Самара', 'Гордость и предубеждение', '2024-01-25', '2024-02-10');
              """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(sql)
                self.db_connection.commit()
            self.person_list.setRowCount(0)
            self.book_list.setRowCount(0)
            self.show_table_fields(self.__table_list['books']['tname'])
            self.show_table_fields(self.__table_list['persons']['tname'])
            self.save_data_books()
            self.save_data_persons()
            self.statusbar.showMessage(f'Тестовые данные успешно добавлены!', 2000)
        except Exception as er:
            self.db_connection.rollback()
            QMessageBox.critical(self, 'Error', f'Ошибка при добавлении тестовых записей в таблицы:\n\n{er}')

    # =================== Методы для вывода отчетов =============================
    def show_report(self):
        if self.report_list.currentIndex() == 0:
            self.books_persons_amount(tname=self.__table_list['books']['tname'], header_label='Всего книг в библиотеке')
        elif self.report_list.currentIndex() == 1:
            self.books_persons_amount(tname=self.__table_list['persons']['tname'], header_label='Всего читателей')
        elif self.report_list.currentIndex() == 2:
            self.books_amount_for_person()
        elif self.report_list.currentIndex() == 3:
            self.books_amount_for_person_now()
        elif self.report_list.currentIndex() == 4:
            self.last_visit_date()
        elif self.report_list.currentIndex() == 5:
            self.most_read_author()
        elif self.report_list.currentIndex() == 6:
            self.genre_list_desc()

    # Сколько книг есть в библиотеке, сколько всего читателей
    def books_persons_amount(self, tname: str, header_label: str):
        if tname == self.__table_list['books']['tname']:
            sql = f"""SELECT COUNT(book_title) FROM {tname}"""
        else: sql = f"""SELECT COUNT(DISTINCT name) FROM {tname} """

        res = self.sql_query(sql=sql, err_msg='Ошибка запроса к базе данных')
        if not res:
            self.output_report.setColumnCount(0)
            self.output_report.setRowCount(0)
            return False

        self.output_report.setColumnCount(1)
        self.output_report.setHorizontalHeaderLabels([header_label])
        self.output_report.setRowCount(1)
        self.output_report.setItem(0, 0, QTableWidgetItem(str(res[0][0])))

    # Сколько книг брал каждый читатель за все время
    def books_amount_for_person(self):
        sql = f"""SELECT name, COUNT(name) FROM {self.__table_list['persons']['tname']}
            GROUP BY name
        """
        res = self.sql_query(sql=sql, err_msg='Ошибка запроса к базе данных')
        if not res:
            self.output_report.setColumnCount(0)
            self.output_report.setRowCount(0)
            return False

        self.output_report.setColumnCount(2)
        self.output_report.setHorizontalHeaderLabels(['Читатель', 'Сколько книг брал за все время'])
        self.output_report.setRowCount(len(res))
        for i in range(len(res)):
            self.output_report.setItem(i, 0, QTableWidgetItem(str(res[i][0])))
            self.output_report.setItem(i, 1, QTableWidgetItem(str(res[i][1])))

    # Сколько книг сейчас находится на руках у каждого читателя
    def books_amount_for_person_now(self):
        sql = f"""SELECT owner, COUNT(owner) FROM {self.__table_list['books']['tname']}
            GROUP BY owner
            HAVING LOWER(owner) <> 'библиотека'
        """
        res = self.sql_query(sql=sql, err_msg='Ошибка запроса к базе данных')
        if not res:
            self.output_report.setColumnCount(0)
            self.output_report.setRowCount(0)
            return False

        self.output_report.setColumnCount(2)
        self.output_report.setHorizontalHeaderLabels(['Читатель', 'Сколько книг на руках'])
        self.output_report.setRowCount(len(res))
        for i in range(len(res)):
            self.output_report.setItem(i, 0, QTableWidgetItem(str(res[i][0])))
            self.output_report.setItem(i, 1, QTableWidgetItem(str(res[i][1])))

    # Дата последнего посещения читателем библиотеки
    def last_visit_date(self):
        sql = f"""SELECT name, MAX(visit_date) FROM {self.__table_list['persons']['tname']}
            GROUP BY name
            ORDER BY MAX(visit_date) DESC
            LIMIT 1
        """
        res = self.sql_query(sql=sql, err_msg='Ошибка запроса к базе данных')
        if not res:
            self.output_report.setColumnCount(0)
            self.output_report.setRowCount(0)
            return False

        self.output_report.setColumnCount(2)
        self.output_report.setHorizontalHeaderLabels(['Читатель', 'Дата последнего посещения'])
        self.output_report.setRowCount(len(res))
        self.output_report.setItem(0, 0, QTableWidgetItem(str(res[0][0])))
        self.output_report.setItem(0, 1, QTableWidgetItem(str(res[0][1])))

    # Самый читаемый автор
    def most_read_author(self):
        sql = f"""SELECT author FROM {self.__table_list['persons']['tname']}
            INNER JOIN books ON persons.book_title = books.book_title
            GROUP BY author
            ORDER BY COUNT(*) DESC
            LIMIT 1                   

        """
        res = self.sql_query(sql=sql, err_msg='Ошибка запроса к базе данных')
        if not res:
            self.output_report.setColumnCount(0)
            self.output_report.setRowCount(0)
            return False

        self.output_report.setColumnCount(1)
        self.output_report.setHorizontalHeaderLabels(['Самый читаемый автор'])
        self.output_report.setRowCount(len(res))
        self.output_report.setItem(0, 0, QTableWidgetItem(str(res[0][0])))

    # Самые предпочитаемые читателями жанры по убыванию
    def genre_list_desc(self):
        sql = f"""SELECT genre FROM {self.__table_list['persons']['tname']}
            INNER JOIN books ON persons.book_title = books.book_title
            GROUP BY genre
            ORDER BY COUNT(*) DESC
        """
        res = self.sql_query(sql=sql, err_msg='Ошибка запроса к базе данных')
        if not res:
            self.output_report.setColumnCount(0)
            self.output_report.setRowCount(0)
            return False

        self.output_report.setColumnCount(1)
        self.output_report.setHorizontalHeaderLabels(['Самые предпочитаемые читателями жанры по убыванию'])
        self.output_report.setRowCount(len(res))
        for i in range(len(res)):
            self.output_report.setItem(i, 0, QTableWidgetItem(str(res[i][0])))

    # Вывод отчета по просрокам возврата книг
    def books_expiration_date(self):
        sql = f"""SELECT name, book_title, exp_date FROM {self.__table_list['persons']['tname']}
                 WHERE (name, book_title) IN (SELECT owner, book_title FROM {self.__table_list['books']['tname']}
                                              WHERE LOWER(owner) <> 'библиотека'
                                             )
        """
        res = self.sql_query(sql=sql, err_msg='Ошибка при составлении отчета о просроках возврата книг')
        if not res: return False

        with open('Отчет по просрокам.txt', 'w') as f:
            f.write('--- Списко читателей, которе вовремя не вернули книги ---\n\n')
            date_now = dt.now().strftime('%Y-%m-%d')
            for i in range(len(res)):
                if date_now > str(res[i][2]):
                    f.write(f'[{i+1}] {res[i][0]}, книга "{res[i][1]}", должен быть вернуть до {res[i][2]}\n\n')

        self.statusbar.showMessage(f'Отчет записан в файл "Отчет по просрокам.txt"', 2000)

    # Формирование файла GeoJSON
    def get_books_location(self):
        sql = f"""SELECT owner, {self.__table_list['books']['tname']}.book_title, address FROM {self.__table_list['books']['tname']}
                  INNER JOIN {self.__table_list['persons']['tname']} ON 
                                    {self.__table_list['books']['tname']}.owner={self.__table_list['persons']['tname']}.name
                  GROUP BY owner, {self.__table_list['books']['tname']}.book_title, address
                  HAVING LOWER(owner) <> 'библиотека'
        """
        res = self.sql_query(sql=sql, err_msg='Ошибка при формировании отчета о расположнии книг на карте')
        if not res: return False

        # Создаем список читателей, всех взятых ими книг и их адреса
        res = [list(res[i]) for i in range(len(res))]
        new_list = []
        while True:
            new_item = ['', '', '']
            b = False
            for i in range(len(res)):
                if res[i] != None and (new_item[0] == '' or new_item[0] == res[i][0]):
                    new_item[0] = res[i][0]
                    new_item[1] += ', ' + res[i][1]
                    new_item[2] = res[i][2]
                    b = True
            if b:
                new_item[1] = new_item[1][2:]
                new_list.append(new_item)
                for i in range(len(res)):
                    if res[i] == None or res[i][0] == new_item[0]: res[i] = None
            else: break

        # Инициализация геокодера
        geolocator = Nominatim(user_agent="geojson_builder")
        features = []
        for user in new_list:
            location = geolocator.geocode(user[2])

            # Структура JSON элемента для каждого пользователя
            if location:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "name": user[0],
                        "book": user[1],
                        "address": user[2]
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [location.longitude, location.latitude]
                    }
                }
                features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        # Сохраняем GeoJSON в файл
        with open("book_lication.geojson", "w") as outfile:
            json.dump(geojson, outfile)

        self.statusbar.showMessage(f'Отчет записан в файл "book_lication.geojson"', 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    db_connect = QDialog()
    ui_connect = Ui_Form1()
    ui_connect.setupUi(db_connect)
    db_connect.exec_()
    # Подключение к БД прошло успешно
    if ui_connect.connected:
        db = GUI(db_connection=ui_connect.db_connection)
        db.show()
        sys.exit(app.exec_())