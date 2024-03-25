import sys
import json
from PyQt5.QtWidgets import QMessageBox, QComboBox, QApplication ,QHeaderView , QDialog, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QTableWidget, QTableWidgetItem
import time
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# Połączenie z bazą danych MongoDB
uri = "mongodb+srv://deskabiznes:HORnKWuYWTU1NQ3m@addressbook.dzbgyet.mongodb.net/?retryWrites=true&w=majority&appName=addressbook"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['ksiazkaadresowa']
collection = db['users']

registered = True  # Flaga informująca o tym, czy użytkownik jest zarejestrowany
lista_kontaktow = []  # Lista kontaktów
try:
    client.admin.command('ping')
except Exception as e:
    print(e)
# Funkcja wczytująca kontakty z pliku JSON
def wczytaj_z_json(nazwa_pliku):
    kontakty = []
    with open(nazwa_pliku, 'r') as plik:
        dane = json.load(plik)
        # print(dane)
        for kontakt in dane:
            kontakty.append(Kontakt(**kontakt))
    return kontakty
# Widget rejestracji użytkownika
class RegisterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        registered = False

        label_login = QLabel("Login:")
        self.input_login = QLineEdit()
        layout.addWidget(label_login)
        layout.addWidget(self.input_login)

        label_haslo = QLabel("Hasło:")
        self.input_haslo = QLineEdit()
        self.input_haslo.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_haslo)
        layout.addWidget(self.input_haslo)

        label_powtorz_haslo = QLabel("Powtórz hasło:")
        self.input_powtorz_haslo = QLineEdit()
        self.input_powtorz_haslo.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_powtorz_haslo)
        layout.addWidget(self.input_powtorz_haslo)

        button_zarejestruj = QPushButton("Zarejestruj się")
        button_zarejestruj.clicked.connect(self.zarejestruj)
        layout.addWidget(button_zarejestruj)

        self.setLayout(layout)

    def zarejestruj(self):
        login = self.input_login.text()
        haslo = self.input_haslo.text()
        powtorz_haslo = self.input_powtorz_haslo.text()

        if haslo != powtorz_haslo:
            # print("Hasła nie są takie same!")
            QMessageBox.warning(self, 'Błąd', 'Hasła nie są takie same!')
            return
        else:
            mydict = {"login": login, "haslo": haslo}
            sprawdzCzyIstnieje = collection.find_one({"login": login})
            if sprawdzCzyIstnieje:
                QMessageBox.warning(self, 'Błąd', 'Taki użytkownik już istnieje!')
                # print("Użytkownik o podanym loginie już istnieje")
            else:
                # print("Zarejestrowano")
                # print(collection.insert_one(mydict))
                self.parent().zaloguj(login, haslo)
                # print(self.parent())

class StatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wybierz parametr statystyk")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.parameter_combo = QComboBox()
        self.parameter_combo.addItems(["Imie", "Nazwisko", "Miasto"])
        layout.addWidget(self.parameter_combo)

        button_show_stats = QPushButton("Pokaż statystyki")
        button_show_stats.clicked.connect(self.show_statistics)
        layout.addWidget(button_show_stats)

        self.setLayout(layout)

    def show_statistics(self):
        selected_parameter = self.parameter_combo.currentText().lower()
        self.accept()
        self.result = selected_parameter
class StatisticsWindow(QDialog):
    def __init__(self, stats_data):
        super().__init__()
        self.setWindowTitle("Statystyki")
        self.setGeometry(100, 100, 400, 300)
        self.stats_data = stats_data
        layout = QVBoxLayout()


        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Wyszukaj...")
        self.search_bar.textChanged.connect(self.filter_stats)
        layout.addWidget(self.search_bar)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Wartość", "Liczba kontaktów"])

        self.populate_table(stats_data)

        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def filter_stats(self):
        search_text = self.search_bar.text().lower()
        filtered_stats = {key: value for key, value in self.stats_data.items() if search_text in str(key).lower()}
        self.populate_table(filtered_stats)

    def populate_table(self, stats_data):
        sorted_stats = sorted(stats_data.items(), key=lambda x: x[1], reverse=True)

        self.table_widget.setRowCount(len(sorted_stats))

        for row, (value, count) in enumerate(sorted_stats):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(value)))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(count)))




class AddContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        label_imie = QLabel("Imię:")
        self.input_imie = QLineEdit()
        layout.addWidget(label_imie)
        layout.addWidget(self.input_imie)

        label_nazwisko = QLabel("Nazwisko:")
        self.input_nazwisko = QLineEdit()
        layout.addWidget(label_nazwisko)
        layout.addWidget(self.input_nazwisko)

        label_numer = QLabel("Numer telefonu:")
        self.input_numer = QLineEdit()
        layout.addWidget(label_numer)
        layout.addWidget(self.input_numer)

        label_miasto = QLabel("Miasto:")
        self.input_miasto = QLineEdit()
        layout.addWidget(label_miasto)
        layout.addWidget(self.input_miasto)

        button_dodaj = QPushButton("Dodaj")
        button_dodaj.clicked.connect(self.dodaj_kontakt)
        layout.addWidget(button_dodaj)

        self.setLayout(layout)

    def dodaj_kontakt(self):
        print("Dodaj kontakt")
        for kontakt in wczytaj_z_json("kontakty.json"):
            print(kontakt.imie)
            if kontakt.imie == self.input_imie.text() and kontakt.nazwisko == self.input_nazwisko.text():
                QMessageBox.warning(self, 'Błąd', 'Kontakt już istnieje!')
                return
            else:
                continue

        imie = self.input_imie.text()
        nazwisko = self.input_nazwisko.text()
        numer = self.input_numer.text()
        miasto = self.input_miasto.text()
        self.kontakt = Kontakt(imie, nazwisko, numer, miasto)
        KsiazkaAdresowa().zapisz_do_json("kontakty.json", self.kontakt)
        self.parent().update_table()
        self.accept()



class LoginWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)
        layout = QVBoxLayout()

        label_login = QLabel("Login:")
        self.input_login = QLineEdit()
        layout.addWidget(label_login)
        layout.addWidget(self.input_login)

        label_haslo = QLabel("Hasło:")
        self.input_haslo = QLineEdit()
        self.input_haslo.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_haslo)
        layout.addWidget(self.input_haslo)

        button_zaloguj = QPushButton("Zaloguj")
        button_zaloguj.clicked.connect(self.zaloguj)
        layout.addWidget(button_zaloguj)

        button_zarejestruj = QPushButton("Zarejestruj się")
        button_zarejestruj.clicked.connect(self.show_register_screen)
        layout.addWidget(button_zarejestruj)

        self.setLayout(layout)


    def zaloguj(self, *args):
        if registered == False:
            # print("Zarejestruj się")
            if args:
                self.parent().zaloguj(args[0], args[1])
            else:
                QMessageBox.warning(self, 'Błąd', 'Pola są puste!')
        else:
            # print("Zaloguj się")
            loginInput = self.input_login.text()
            hasloInput = self.input_haslo.text()
            # /(loginInput)
            # print(hasloInput)
            self.parent().zaloguj(loginInput, hasloInput)

    def show_register_screen(self):
        self.register_widget = RegisterWidget(self)
        self.layout().addWidget(self.register_widget)
        self.layout().removeWidget(self)


class ContactsWidget(QWidget):
    def __init__(self,  parent=None):
        super().__init__(parent)
        lista_kontaktow = wczytaj_z_json("kontakty.json")
        self.filtered_contacts = lista_kontaktow.copy()
        self.kontakty = lista_kontaktow

        layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Wyszukaj...")
        self.search_bar.textChanged.connect(self.filter_contacts)
        layout.addWidget(self.search_bar)

        self.search_parameter_combo = QComboBox()
        self.search_parameter_combo.addItems(["Imie", "Nazwisko", "Numer telefonu", "Miasto"])
        layout.addWidget(self.search_parameter_combo)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Imię", "Nazwisko", "Numer telefonu", "Miasto"])

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.update_table()

        layout.addWidget(self.table_widget)

        button_dodaj = QPushButton("Dodaj kontakt")
        button_dodaj.clicked.connect(self.show_add_contact_dialog)
        layout.addWidget(button_dodaj)

        button_statystyki = QPushButton("Statystyki")
        button_statystyki.clicked.connect(self.show_statistics_dialog)
        layout.addWidget(button_statystyki)

        self.setLayout(layout)

    def show_statistics(self):
        stats_data = self.calculate_statistics()
        self.show_statistics_window(stats_data)

    def show_statistics_dialog(self):
        dialog = StatisticsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_parameter = dialog.result
            stats_data = self.calculate_statistics(selected_parameter)
            self.show_statistics_window(stats_data)

    def calculate_statistics(self, selected_parameter):
        stats_data = {}
        for contact in lista_kontaktow:
            value = getattr(contact, selected_parameter)
            stats_data[value] = stats_data.get(value, 0) + 1

        return stats_data

    def show_statistics_window(self, stats_data):
        stats_window = StatisticsWindow(stats_data)
        stats_window.exec_()

    def update_table(self):

        self.table_widget.setRowCount(0)
        for row, kontakt in enumerate(self.filtered_contacts):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(kontakt.imie))
            self.table_widget.setItem(row, 1, QTableWidgetItem(kontakt.nazwisko))
            self.table_widget.setItem(row, 2, QTableWidgetItem(kontakt.numer_telefonu))
            self.table_widget.setItem(row, 3, QTableWidgetItem(kontakt.miasto))

    def filter_contacts(self):
        search_text = self.search_bar.text().lower()
        search_parameter_index = self.search_parameter_combo.currentIndex()
        search_parameter = self.search_parameter_combo.itemText(search_parameter_index)

        if search_parameter == "Imię":
            self.filtered_contacts = [contact for contact in self.kontakty if search_text in contact.imie.lower()]
        elif search_parameter == "Nazwisko":
            self.filtered_contacts = [contact for contact in self.kontakty if search_text in contact.nazwisko.lower()]
        elif search_parameter == "Numer telefonu":
            self.filtered_contacts = [contact for contact in self.kontakty if
                                      search_text in contact.numer_telefonu.lower()]
        elif search_parameter == "Miasto":
            self.filtered_contacts = [contact for contact in self.kontakty if search_text in contact.miasto.lower()]
        self.update_table()
    def show_add_contact_dialog(self):
        dialog = AddContactDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            lista_kontaktow.append(dialog.kontakt)
            self.filter_contacts()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Książka adresowa")
        self.setGeometry(100, 100, 600, 400)

        self.login_widget = LoginWidget(self)
        self.setCentralWidget(self.login_widget)

        self.lista_kontaktow = []
        self.logged_in = False
        registered = True
    def zaloguj(self, login, haslo):
        myquery = {"login": login, "haslo": haslo}
        mydoc = collection.find(myquery)
        for data in mydoc:
            # print(data)
            if data['haslo'] == haslo and data['login'] == login:
                # print("Zalogowano")
                ksiazka_adresowa = KsiazkaAdresowa()
                self.logged_in = True
                self.show_contacts_view()

    def show_contacts_view(self):
        if not self.logged_in:
            return

        self.contacts_widget = ContactsWidget()  # Przekazanie listy kontaktów do widżetu
        self.setCentralWidget(self.contacts_widget)


class Kontakt:
    def __init__(self, imie, nazwisko, numer_telefonu, miasto):
        self.imie = imie
        self.nazwisko = nazwisko
        self.numer_telefonu = numer_telefonu
        self.miasto = miasto

    def to_dict(self):
        return {
            "imie": self.imie,
            "nazwisko": self.nazwisko,
            "numer_telefonu": self.numer_telefonu,
            "miasto": self.miasto
        }


class KsiazkaAdresowa:
    def __init__(self):
        pass   # Konstruktor nie jest wymagany
    def zapisz_do_json(self, nazwa_pliku, kontakt):
        try:
            with open(nazwa_pliku, 'r') as plik:
                dane = json.load(plik)
        except FileNotFoundError:
            dane = []

        dane.append(kontakt.to_dict())

        with open(nazwa_pliku, 'w') as plik:
            json.dump(dane, plik)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

