from PyQt5 import QtCore, QtGui, QtWidgets
from MyWidjets import *
import googletrans
import textract
import sqlite3
import sys


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('BEST TRANSLATOR')
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.translator = googletrans.Translator()
        self.req_boxes = {}     # словарь, для сохранения айди и виджета записи. В виде id: requests_box
        # нужен для удаления/загрузки данных в переводчик
        self.all_colls = set()  # множество для созранения данных каждой записи, чтобы не было повторений
        # Хранится в виде (source_lang, source_text, dest_lang, dest_text)
        self.clipboard = QtWidgets.QApplication.clipboard()  # для кнопки копирования текста
        self.now_source_lang = 'russian'    # изначальный исходный язык
        self.now_source_code = 'ru'         # код исходного языка
        self.now_dest_lang = 'english'      # изначальный запрошенный язык
        self.now_dest_code = 'en'           # код запрошенного языка
        self.source_btn.clicked.connect(self.choose_source_lang)            #
        self.dest_btn.clicked.connect(self.choose_dest_lang)                # прикрепляем кнопки к их методам
        self.run_button.clicked.connect(self.translate_source_text)         #
        self.swap_langs_btn.clicked.connect(self.swap_langs_clicked)        #
        self.file_btn.clicked.connect(self.file_btn_clicked)                #
        self.delete_text_btn.clicked.connect(self.delete_text_btn_clicked)  #
        self.copy_btn.clicked.connect(self.copy_btn_clicked)                #
        self.requests_db = sqlite3.connect("translate_request.sqlite")   # открываем бд с запросами перевода
        self.cur = self.requests_db.cursor()
        res = self.cur.execute('''SELECT * FROM requests''').fetchall()  # собираем все записи из бд
        for i in res:
            self.create_requests_history(*i)  # добавляем каждую запись в scrollArea

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(917, 622)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.translate_box = QtWidgets.QGroupBox(self.centralwidget)
        self.translate_box.setStyleSheet("border-radius: 50px;\n"
                                         "background-color: white;")
        self.translate_box.setTitle("")
        self.translate_box.setObjectName("translate_box")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.translate_box)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.vertical_source = QtWidgets.QVBoxLayout()
        self.vertical_source.setObjectName("vertical_source")
        self.source_btn = QtWidgets.QPushButton(self.translate_box)
        self.source_btn.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.source_btn.setFont(font)
        self.source_btn.setStyleSheet("#source_btn{"
                                      "background-color: rgba(1, 1, 1, 0);"
                                      "border-bottom: 2px solid #c7cedf;"
                                      "text-align: right;padding-right: 13px;"
                                      "}"
                                      "#source_btn:hover{"
                                      "background-color: #c7cedf;"
                                      "border-top-left-radius: 3em;"
                                      "border-top-right-radius: 0;"
                                      "border-bottom-left-radius: 0;"
                                      "border-bottom-right-radius: 0;"
                                      "}")
        self.source_btn.setObjectName("source_btn")
        self.vertical_source.addWidget(self.source_btn)
        self.source_text = QtWidgets.QTextEdit(self.translate_box)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.source_text.setFont(font)
        self.source_text.setStyleSheet("")
        self.source_text.setObjectName("source_text")
        self.vertical_source.addWidget(self.source_text)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.delete_text_btn = QtWidgets.QPushButton(self.translate_box)
        self.delete_text_btn.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.delete_text_btn.setFont(font)
        self.delete_text_btn.setStyleSheet("#delete_text_btn{"
                                           "border-top-left-radius: 1em;"
                                           "border-top-right-radius: 0;"
                                           "border-bottom-left-radius: 1em;"
                                           "border-bottom-right-radius: 0;"
                                           "border: 5px solid #c7cedf;"
                                           "border-right: 0;"
                                           "}"
                                           "#delete_text_btn:hover{"
                                           "background-color: #c7cedf;"
                                           "}")
        self.delete_text_btn.setObjectName("delete_text_btn")
        self.horizontalLayout_4.addWidget(self.delete_text_btn)
        self.file_btn = QtWidgets.QPushButton(self.translate_box)
        self.file_btn.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.file_btn.setFont(font)
        self.file_btn.setStyleSheet("#file_btn{"
                                    "border-top-right-radius: 1em;"
                                    "border-top-left-radius: 0;"
                                    "border-bottom-right-radius: 1em;"
                                    "border-bottom-left-radius: 0;"
                                    "border: 5px solid #c7cedf;"
                                    "border-left: 0;"
                                    "}"
                                    "#file_btn:hover{"
                                    "background-color: #c7cedf;"
                                    "}")
        self.file_btn.setObjectName("file_btn")
        self.horizontalLayout_4.addWidget(self.file_btn)
        self.vertical_source.addLayout(self.horizontalLayout_4)
        self.horizontalLayout.addLayout(self.vertical_source)
        self.verticalchange = QtWidgets.QVBoxLayout()
        self.verticalchange.setObjectName("verticalchange")
        self.swap_langs_btn = QtWidgets.QPushButton(self.translate_box)
        self.swap_langs_btn.setMinimumSize(QtCore.QSize(50, 41))
        self.swap_langs_btn.setStyleSheet("#swap_langs_btn:hover {"
                                          "background-color: #c7cedf;"
                                          "border-top-left-radius: 1em;"
                                          "border-top-right-radius: 1em;"
                                          "border-bottom-left-radius: 1em;"
                                          "border-bottom-right-radius: 1em;}")
        self.swap_langs_btn.setObjectName("swap_langs_btn")
        self.verticalchange.addWidget(self.swap_langs_btn)
        self.nothing = QtWidgets.QLabel(self.translate_box)
        self.nothing.setText("")
        self.nothing.setObjectName("nothing")
        self.verticalchange.addWidget(self.nothing)
        self.horizontalLayout.addLayout(self.verticalchange)
        self.verticaldest = QtWidgets.QVBoxLayout()
        self.verticaldest.setObjectName("verticaldest")
        self.dest_btn = QtWidgets.QPushButton(self.translate_box)
        self.dest_btn.setMinimumSize(QtCore.QSize(0, 41))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.dest_btn.setFont(font)
        self.dest_btn.setStyleSheet("#dest_btn{"
                                    "background-color: rgba(1, 1, 1, 0);"
                                    "border-bottom: 2px solid #c7cedf;"
                                    "text-align: left;"
                                    "padding-left: 13px;"
                                    "}"
                                    "#dest_btn:hover{"
                                    "background-color: #c7cedf;"
                                    "border-top-left-radius: 0;"
                                    "border-top-right-radius: 3em;"
                                    "border-bottom-left-radius: 0;"
                                    "border-bottom-right-radius: 0;}")
        self.dest_btn.setObjectName("dest_btn")
        self.verticaldest.addWidget(self.dest_btn)
        self.dest_text = QtWidgets.QTextEdit(self.translate_box)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.dest_text.setFont(font)
        self.dest_text.setStyleSheet("")
        self.dest_text.setReadOnly(True)
        self.dest_text.setObjectName("dest_text")
        self.verticaldest.addWidget(self.dest_text)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.copy_btn = QtWidgets.QPushButton(self.translate_box)
        self.copy_btn.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.copy_btn.setFont(font)
        self.copy_btn.setStyleSheet("#copy_btn{"
                                    "border-radius: 1em;"
                                    "border: 5px solid #c7cedf;"
                                    "}"
                                    "#copy_btn:hover{"
                                    "background-color: #c7cedf;"
                                    "}")
        self.copy_btn.setObjectName("copy_btn")
        self.horizontalLayout_5.addWidget(self.copy_btn)
        self.verticaldest.addLayout(self.horizontalLayout_5)
        self.horizontalLayout.addLayout(self.verticaldest)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.run_button = QtWidgets.QPushButton(self.translate_box)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_button.sizePolicy().hasHeightForWidth())
        self.run_button.setSizePolicy(sizePolicy)
        self.run_button.setMinimumSize(QtCore.QSize(0, 54))
        self.run_button.setMaximumSize(QtCore.QSize(16777215, 54))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.run_button.setFont(font)
        self.run_button.setStyleSheet("#run_button{"
                                      "border-top-left-radius: 0;"
                                      "border-top-right-radius: 0;"
                                      "border-bottom-left-radius: 3em;"
                                      "border-bottom-right-radius: 3em;"
                                      "}"
                                      "#run_button:hover{"
                                      "background-color: #c7cedf;"
                                      "}")
        self.run_button.setObjectName("run_button")
        self.verticalLayout_2.addWidget(self.run_button)
        self.verticalLayout_3.addWidget(self.translate_box)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 880, 237))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.scrollAreaWidgetContents_2.setFont(font)
        self.scrollAreaWidgetContents_2.setTabletTracking(False)
        self.scrollAreaWidgetContents_2.setAutoFillBackground(False)
        self.scrollAreaWidgetContents_2.setStyleSheet("")
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.scrollArea.hide()
        self.verticalLayout_3.addWidget(self.scrollArea)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.source_btn.setText(_translate("MainWindow", "русский"))
        self.source_text.setHtml(_translate("MainWindow",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/"
                                            "REC-html40/strict.dtd\">\n<html><head><meta name=\"qrichtext\" content=\"1"
                                            "\" /><style type=\"text/css\">\np, li { white-space: pre-wrap; }\n</style>"
                                            "</head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:16pt; font"
                                            "-weight:400; font-style:normal;\">\n<p style=\"-qt-paragraph-type:empty; m"
                                            "argin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-b"
                                            "lock-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.source_text.setPlaceholderText(_translate("MainWindow", "пишите текст сюда..."))
        self.delete_text_btn.setText(_translate("MainWindow", "delete"))
        self.file_btn.setText(_translate("MainWindow", "file"))
        self.swap_langs_btn.setText(_translate("MainWindow", "<- ->"))
        self.dest_btn.setText(_translate("MainWindow", "english"))
        self.dest_text.setHtml(_translate("MainWindow",
                                          "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/RE"
                                          "C-html40/strict.dtd\">\n<html><head><meta name=\"qrichtext\" content=\"1\" /"
                                          "><style type=\"text/css\">\np, li { white-space: pre-wrap; }\n</style></head"
                                          "><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:16pt; font-weight:"
                                          "400; font-style:normal;\">\n<p style=\"-qt-paragraph-type:empty; margin-top:"
                                          "0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:"
                                          "0; text-indent:0px; font-size:20pt;\"><br /></p></body></html>"))
        self.dest_text.setPlaceholderText(_translate("MainWindow", "а здесь будет перевод..."))
        self.copy_btn.setText(_translate("MainWindow", "copy"))
        self.run_button.setText(_translate("MainWindow", "TRANSLATE"))

    def translate_source_text(self):  # основная функция перевода текста
        text_to_translate = self.source_text.toPlainText()

        if text_to_translate:  # проверяем исходный текст на пустоту
            translated_text = self.translator.translate(
                text_to_translate, src=self.now_source_code, dest=self.now_dest_lang).text  # переводим текст
            data = (self.now_source_lang, text_to_translate, self.now_dest_lang, translated_text)
            self.dest_text.setPlainText(translated_text)  # вставляем переведенный текст
            if data not in self.all_colls:  # условие для сохранения уникальных записей
                self.cur.execute('INSERT INTO requests(src_lang, src_text, dest_lang, dest_text) '
                                 'VALUES(?, ?, ?, ?)', data)  # добавляем запись в бд с нашими данными
                self.requests_db.commit()                     # коммитим!!!
                id_num = self.cur.execute('SELECT id FROM requests '
                                          'WHERE src_lang = ? and src_text = ? and '
                                          'dest_lang = ? and dest_text = ?', data).fetchall()[0][0]
                # ищем id только что вставленной записи, для добавления в scrollArea
                self.create_requests_history(id_num, *data) # добавляем запись в scrollArea
        else:  # если исходный текст пустой то
            self.dest_text.setText('')

    def translate_widjets(self):  # переводим текст на виджетах
        try:
            placeholders = PLACEHOLDER_TRANSLATE[self.now_source_lang]     # берем текст из плейсхолдеров
            self.source_btn.setText(self.now_source_lang)                  #
            self.source_text.setPlaceholderText(placeholders[0])           # вставляем переведенный текст
            self.dest_btn.setText(self.now_dest_lang)                      # в виджеты
            self.dest_text.setPlaceholderText(placeholders[1])             #
        except Exception:    # если не нашлелся язык в константе
            placeholders = self.translator.translate(['пишите текст здесь...', 'а здесь будет перевод...'],
                                                     src=self.now_source_lang, dest=self.now_dest_lang)
            print(placeholders)
            self.source_btn.setText(self.now_source_lang)              #
            self.source_text.setPlaceholderText(placeholders[0].text)  # вставляем переведенный текст
            self.dest_btn.setText(self.now_dest_lang)                  # в виджеты
            self.dest_text.setPlaceholderText(placeholders[1].text)    #

    def choose_source_lang(self):  # метод изменения исходного языка
        dialog = LangDialog()      # вызываем окно выбора языка
        dialog.show()              # показываем окно
        if dialog.exec_():
            self.now_source_lang = dialog.get_choosen_lang()                 # меняем язык на выбранный в окне
            self.now_source_code = googletrans.LANGCODES[self.now_source_lang]

            self.translate_widjets()

    def choose_dest_lang(self):   # метод изменения запрошенного языка
        dialog = LangDialog()     # вызываем окно выбора языка
        dialog.show()             # показываем окно
        if dialog.exec_():
            self.now_dest_lang = dialog.get_choosen_lang()                  # меняем язык на выбранный в окне
            self.now_dest_code = googletrans.LANGCODES[self.now_dest_lang]  #
            self.dest_btn.setText(self.now_dest_lang)                       #

    def swap_langs_clicked(self):  # метод для перестановки местами исходного и запрошенного языков
        self.now_source_lang, self.now_dest_lang = self.now_dest_lang, self.now_source_lang
        self.now_source_code, self.now_dest_code = self.now_dest_code, self.now_source_code
        self.translate_widjets()

    def go_to_translate_btn_clicked(self):  # метод для загрузки данных из записи в переводчик
        try:        # на всякий случай try, но ошибок вроде не возникает
            id_num = self.sender().getNum()  # вытаскиваем номер кнопки
            res = self.cur.execute('SELECT * FROM requests WHERE id = ?', (id_num, )).fetchall()[0]  # находим запись
            self.now_source_lang = res[1]
            self.now_source_code = googletrans.LANGCODES[self.now_source_lang]  # меняем исходный язык и код
            self.source_btn.setText(self.now_source_lang)
            self.source_text.setText(res[2])  # меняем исходный текст и кнопку
            self.now_dest_lang = res[3]
            self.now_dest_code = googletrans.LANGCODES[self.now_dest_lang]  # меняем запрошенный язык и код
            self.dest_btn.setText(self.now_dest_lang)
            self.dest_text.setText(res[4])  # меняем запрошенный текст и кнопку
            self.translate_widjets()
        except Exception as ex:
            print(ex.__class__.__name__)

    def delete_from_bd_btn_clicked(self):
        try:    # на всякий случай try, но ошибок вроде не возникает
            id_num = self.sender().getNum()  # вытаскиваем номер кнопки
            res = self.cur.execute('SELECT * FROM requests WHERE id = ?', (id_num,)).fetchall()  # ищем данные с id
            # для того чтобы потом удалить данные записи из all_colls
            self.cur.execute('DELETE FROM requests WHERE id = ?', (id_num,))  # удаляем запись с id из бд
            self.requests_db.commit()    # КОММИТИМ!!!
            self.all_colls.discard(res[0][1:])  # удаляем данные записи
            self.req_boxes[id_num].hide()       # скрываем и удаляем requests_box нашей записи
            self.req_boxes[id_num].destroy()    #
            if not self.all_colls:      # если записей уже нет
                self.scrollArea.hide()  # скрываем пустую scrollArea для красоты!!!
        except Exception as ex:
            print(ex.__class__.__name__)

    def file_btn_clicked(self):
        try:
            file = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Выбрать файл', '',
                'Text (*.txt);;Word (*.docx);;Word (*.doc);; CSV (*.csv)')[0]  # диалог для выбора текстового файла
            print(file[-4:])
            if file[-4:] in ('.txt', '.csv'):    # открываем .txt или .csv файл
                with open(file, encoding='utf-8') as file:
                    self.source_text.setText(file.read())    # читаем файл и вставляем его в исходный текст
                    self.translate_source_text()             # переводим текст
            else:
                text = textract.process(file)
                text = text.decode("utf-8")
                self.source_text.setText(text)
                self.translate_source_text()
        except Exception as ex:
            print('Слишком большой файл')

    def delete_text_btn_clicked(self):  # опустошить исходный и запрошенные тексты
        self.source_text.setText('')
        self.dest_text.setText('')

    def copy_btn_clicked(self):  # метод для вставки текста в буфер обмена
        self.clipboard.clear()
        self.clipboard.setText(self.dest_text.toPlainText())

    def create_requests_history(self, id_num, src_lang, src_text, dest_lang, dest_text):
        # метод для добавления 1-ой записи в scrollArea
        # сгенерировано из pyuic
        self.all_colls.add((src_lang, src_text, dest_lang, dest_text))  # добавляем данные в set()
        self.scrollArea.show()
        self.requests_box = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_2)
        font = QtGui.QFont()
        font.setFamily("Fixedsys")
        self.requests_box.setFont(font)
        self.requests_box.setStyleSheet("")
        self.requests_box.setTitle("")
        self.requests_box.setObjectName("requests_box")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.requests_box.sizePolicy().hasHeightForWidth())
        self.requests_box.setSizePolicy(sizePolicy)
        self.requests_box.setMinimumSize(QtCore.QSize(16777215, 150))
        self.requests_box.setMaximumSize(QtCore.QSize(16777215, 150))
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.requests_box)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.req_source_box = QtWidgets.QGroupBox(self.requests_box)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.req_source_box.setFont(font)
        self.req_source_box.setStyleSheet("background-color: rgb(150, 187, 235);"
                                          "border-top-left-radius: 3.1em;"
                                          "border-top-right-radius: 1em;"
                                          "border-bottom-left-radius: 3.1em;"
                                          "border-bottom-right-radius: 1em;")
        self.req_source_box.setObjectName("req_source_box")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.req_source_box)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.req_source_box)
        self.scrollArea_2.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_6 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_6.setGeometry(QtCore.QRect(0, 0, 295, 221))
        self.scrollAreaWidgetContents_6.setObjectName("scrollAreaWidgetContents_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.req_source_text = QtWidgets.QLabel(self.scrollAreaWidgetContents_6)
        font = QtGui.QFont()
        font.setPointSize(17)
        self.req_source_text.setFont(font)
        self.req_source_text.setText("")
        self.req_source_text.setObjectName("req_source_text")
        self.verticalLayout_4.addWidget(self.req_source_text)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_6)
        self.horizontalLayout_2.addWidget(self.scrollArea_2)
        self.horizontalLayout_3.addWidget(self.req_source_box)
        self.req_dest_box = QtWidgets.QGroupBox(self.requests_box)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.req_dest_box.setFont(font)
        self.req_dest_box.setStyleSheet("background-color: rgb(150, 235, 184);"
                                        "border-radius: 1em;")
        self.req_dest_box.setObjectName("req_dest_box")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.req_dest_box)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.scrollArea_3 = QtWidgets.QScrollArea(self.req_dest_box)
        self.scrollArea_3.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_5 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_5.setGeometry(QtCore.QRect(0, 0, 294, 221))
        self.scrollAreaWidgetContents_5.setObjectName("scrollAreaWidgetContents_5")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.req_dest_text = QtWidgets.QLabel(self.scrollAreaWidgetContents_5)
        font = QtGui.QFont()
        font.setPointSize(17)
        self.req_dest_text.setFont(font)
        self.req_dest_text.setText("")
        self.req_dest_text.setObjectName("req_dest_text")
        self.verticalLayout_6.addWidget(self.req_dest_text)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_5)
        self.verticalLayout_5.addWidget(self.scrollArea_3)
        self.horizontalLayout_3.addWidget(self.req_dest_box)
        self.go_to_translate_btn = PushButtonWithNum(self.requests_box)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.go_to_translate_btn.sizePolicy().hasHeightForWidth())
        self.go_to_translate_btn.setSizePolicy(sizePolicy)
        self.go_to_translate_btn.setMinimumSize(QtCore.QSize(80, 0))
        self.go_to_translate_btn.setMaximumSize(QtCore.QSize(90, 16777215))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.go_to_translate_btn.setFont(font)
        self.go_to_translate_btn.setStyleSheet("#go_to_translate_btn{"
                                               "background-color: rgb(200, 232, 140);"
                                               "border-radius: 1em;"
                                               "}"
                                               "#go_to_translate_btn:hover{"
                                               "background-color:rgb(151, 207, 48);"
                                               "}")
        self.go_to_translate_btn.setObjectName("go_to_translate_btn")
        self.horizontalLayout_3.addWidget(self.go_to_translate_btn)
        self.delete_from_bd_btn = PushButtonWithNum(self.requests_box)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.delete_from_bd_btn.sizePolicy().hasHeightForWidth())
        self.delete_from_bd_btn.setSizePolicy(sizePolicy)
        self.delete_from_bd_btn.setMinimumSize(QtCore.QSize(90, 0))
        self.delete_from_bd_btn.setMaximumSize(QtCore.QSize(91, 16777215))
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.delete_from_bd_btn.setFont(font)
        self.delete_from_bd_btn.setStyleSheet("#delete_from_bd_btn{"
                                              "border-top-left-radius: 1em;"
                                              "border-top-right-radius: 3.1em;"
                                              "border-bottom-left-radius: 1em;"
                                              "border-bottom-right-radius: 3.1em;"
                                              "background-color: rgb(247, 110, 110);"
                                              "}"
                                              "#delete_from_bd_btn:hover{"
                                              "background-color: rgb(213, 56, 56);"
                                              "}")
        self.delete_from_bd_btn.setObjectName("delete_from_bd_btn")
        self.horizontalLayout_3.addWidget(self.delete_from_bd_btn)
        self.verticalLayout.addWidget(self.requests_box)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.req_source_box.setTitle(src_lang)
        self.req_source_text.setText(src_text)
        self.req_dest_box.setTitle(dest_lang)
        self.req_dest_text.setText(dest_text)
        self.go_to_translate_btn.setText("RUN")
        self.go_to_translate_btn.setNum(id_num)
        self.delete_from_bd_btn.setText("DEL")
        self.delete_from_bd_btn.setNum(id_num)
        self.go_to_translate_btn.clicked.connect(self.go_to_translate_btn_clicked)         # соединяем две кнопки
        self.delete_from_bd_btn.clicked.connect(self.delete_from_bd_btn_clicked)           #
        self.req_boxes[id_num] = self.requests_box    # добавляем requests_box для использования в других методах


# НАДЕЮСЬ ВЫ ПОНЯЛИ ВЕСЬ МОЙ КОД
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
