from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
import googletrans
import sqlite3
import time
from pprint import pprint

table = sqlite3.connect('translate_request.sqlite')
cur = table.cursor()
PLACEHOLDER_TRANSLATE = {}    # плейсхолдерсы
for_support = cur.execute('SELECT * FROM translate_placeholders').fetchall()
for i in for_support:
    PLACEHOLDER_TRANSLATE[i[1]] = i[2].split(' ;;;;;;; ')

pprint(PLACEHOLDER_TRANSLATE)


def update_placeholder_table():    # для обновления таблицы плейсхолдерсов
    trans = googletrans.Translator()
    count = 1
    for i in list(googletrans.LANGUAGES.values())[37:60]:
        count += 1
        traslated_words = trans.translate('пишите текст сюда... ;;;;;;; а здесь будет перевод...', dest=i).text
        # переводим текст на определенный язык
        print(i, traslated_words)
        cur.execute('INSERT INTO translate_placeholders(lang, words) VALUES(?, ?)', (i, traslated_words))
        # записываем язык в таблицу
        table.commit()  # коммитим
        time.sleep(10)  # ждем время чтобы слишком много в минуту не обращаться к API переводчика


class LangDialog(QtWidgets.QDialog):  # класс диалога для выбора языка
    def __init__(self):
        self.needed_lang = 'russian'
        super(LangDialog, self).__init__()
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle('CHOOSE LANGUAGE')
        self.setModal(True)
        self.gridbox = QtWidgets.QGridLayout()
        self.set_lang_radios()   # добавляем radiobutton`ы в грид
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        # кнопки для выхода из окна диалога
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.gridbox.addWidget(self.buttons, 8, self.buttons_pos)  # добавляем кнопки в грид
        self.setLayout(self.gridbox)

    def set_lang_radios(self):
        langs = list(googletrans.LANGUAGES.values())  # берем константы языков
        len_langs = len(langs)                        # вычиляем его длину
        print(len_langs)
        self.buttons_pos = len_langs // 8 + 1         # исходя из этого вычисляем расположение кнопок ok|cancel в грид
        count = 0                                     # счетчик
        for i in range(len(langs) // 8 + 1):         # prange можно не использовать, но так вроде быстрее намного
            for j in range(8):
                but = QtWidgets.QRadioButton(langs[count])    # создаем radiobutton (rb)
                but.clicked.connect(self.set_choosen_lang)    # привязываем rb к методу
                self.gridbox.addWidget(but, j, i)             # добавляем в грид, положение вычисляем по j, i
                count += 1                        # увеличиваем счетчик
                if count >= len_langs:    # если уже не осталось языков, то выходим из метода
                    return
        return  # если вдруг в API языков станет больше, может лет через 10-20

    def set_choosen_lang(self):   # ставим выбранный язык
        self.needed_lang = self.sender().text()

    def get_choosen_lang(self):   # при выходе из диалога по нажатию, можно вытащить выбранные данные
        return self.needed_lang


class PushButtonWithNum(QtWidgets.QPushButton):
    def __init__(self, *args):
        super(PushButtonWithNum, self).__init__(*args)
        self.num = 0

    def setNum(self, number):
        self.num = number

    def getNum(self):
        return self.num