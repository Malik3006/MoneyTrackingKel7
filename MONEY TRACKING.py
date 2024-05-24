# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QCalendarWidget, QListWidget, QInputDialog, QMessageBox, QDialog # type: ignore
import sqlite3

class Riwayat:
    def __init__(self):
        self.catatan_per_tanggal = {}
        self.init_database()

    def init_database(self):
        self.conn = sqlite3.connect('money_tracking.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS riwayat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal_str TEXT,
                catatan TEXT
            )
        ''')
        self.conn.commit()

        
        self.cursor.execute('SELECT tanggal_str, catatan FROM riwayat')
        rows = self.cursor.fetchall()
        for row in rows:
            tanggal_str, catatan = row
            self.catatan_per_tanggal.setdefault(tanggal_str, [])
            self.catatan_per_tanggal[tanggal_str].append(catatan)

    def tambah_catatan(self, tanggal_str, catatan):
        self.catatan_per_tanggal.setdefault(tanggal_str, [])
        self.catatan_per_tanggal[tanggal_str].append(catatan)

        self.cursor.execute('INSERT INTO riwayat (tanggal_str, catatan) VALUES (?, ?)', (tanggal_str, catatan))
        self.conn.commit()

    def hapus_catatan(self, tanggal_str, catatan):
        if tanggal_str in self.catatan_per_tanggal and catatan in self.catatan_per_tanggal[tanggal_str]:
            self.catatan_per_tanggal[tanggal_str].remove(catatan)

            self.cursor.execute('DELETE FROM riwayat WHERE tanggal_str=? AND catatan=?', (tanggal_str, catatan))
            self.conn.commit()

    def get_catatan_by_tanggal(self, tanggal_str):
        return self.catatan_per_tanggal.get(tanggal_str, [])

class RiwayatDialog(QDialog):
    def __init__(self, catatan_per_tanggal):
        super().__init__()

        self.catatan_per_tanggal = catatan_per_tanggal

        self.setWindowTitle('Riwayat')
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()

        self.list_history = QListWidget()
        self.layout.addWidget(self.list_history)

        self.populate_history_list()

        self.button_kembali = QPushButton("Kembali")
        self.button_kembali.setStyleSheet("background-color: #4CAF50; color: white; border: 5px solid #4CAF50; border-radius: 5px;")
        self.button_kembali.clicked.connect(self.kembali)
        self.layout.addWidget(self.button_kembali)

       

        self.setLayout(self.layout)

    def populate_history_list(self):
        for tanggal, catatan in self.catatan_per_tanggal.items():
            for item in catatan:
                self.list_history.addItem(f"{tanggal}: {item}")

    def kembali(self):
        self.accept()

class MoneyTrackingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.saldo = 0
        self.layout = QVBoxLayout()

        self.label_saldo = QLabel(f"Saldo: Rp {self.saldo}")
        self.layout.addWidget(self.label_saldo)

        self.button_tambah_saldo = QPushButton("Tambah Saldo Awal")
        self.button_tambah_saldo.setStyleSheet("background-color: #4CAF50; color: white; border: 5px solid #4CAF50; border-radius: 5px;")
        self.layout.addWidget(self.button_tambah_saldo)

        self.button_input = QPushButton("Input Pengeluaran")
        self.button_input.setStyleSheet("background-color: #008CBA; color: white; border: 5px solid #008CBA; border-radius: 5px;")
        self.layout.addWidget(self.button_input)

        self.button_hapus_catatan = QPushButton("Hapus Catatan")
        self.button_hapus_catatan.setStyleSheet("background-color: #FF5733; color: white; border: 5px solid #FF5733; border-radius: 5px;")
        self.layout.addWidget(self.button_hapus_catatan)

        self.button_view_riwayat = QPushButton("Lihat Riwayat")
        self.button_view_riwayat.setStyleSheet("background-color: #3498db; color: white; border: 5px solid #3498db; border-radius: 5px;")
        self.layout.addWidget(self.button_view_riwayat)

        self.calendar = QCalendarWidget()
        self.layout.addWidget(self.calendar)

        self.list_history = QListWidget()
        self.layout.addWidget(self.list_history)

        self.button_tambah_saldo.clicked.connect(self.tambah_saldo_awal)
        self.button_input.clicked.connect(self.input_pengeluaran)
        self.button_hapus_catatan.clicked.connect(self.hapus_catatan)
        self.button_view_riwayat.clicked.connect(self.view_riwayat)
        self.calendar.selectionChanged.connect(self.filter_catatan)

        self.setLayout(self.layout)
        self.setWindowTitle('Money Tracking')
        self.setGeometry(100, 100, 400, 400)
        self.show()

        self.riwayat = Riwayat()

    def tambah_saldo_awal(self):
        input_saldo, ok = QInputDialog.getDouble(self, "Tambah Saldo Awal", "Masukkan Saldo Awal (Rp):")
        if ok:
            if input_saldo > 0:
                self.saldo += input_saldo
                self.label_saldo.setText(f"Saldo Awal: Rp {self.saldo}")
            else:
                print("Saldo awal harus lebih dari 0")

    def input_pengeluaran(self):
        input_nama, ok1 = QInputDialog.getText(self, "Input Nama Pengeluaran", "Nama Pengeluaran:")
        input_nominal, ok2 = QInputDialog.getDouble(self, "Input Nominal Pengeluaran", "Nominal Pengeluaran (Rp):")

        if ok1 and ok2:
            nama_pengeluaran = input_nama
            nominal_pengeluaran = input_nominal

            if not nama_pengeluaran or nominal_pengeluaran <= 0:
                return

            if self.saldo >= nominal_pengeluaran:
                selected_date = self.calendar.selectedDate()
                tanggal = selected_date.day()
                bulan = selected_date.month()
                tahun = selected_date.year()

                tanggal_str = f"{tanggal}-{bulan}-{tahun}"
                history_text = f"{tanggal_str}: {nama_pengeluaran} (Rp {nominal_pengeluaran:.2f})"
                self.list_history.addItem(history_text)

                self.riwayat.tambah_catatan(tanggal_str, history_text)

                self.saldo -= nominal_pengeluaran
                self.label_saldo.setText(f"Saldo Awal: Rp {self.saldo}")
            else:
                message = QMessageBox()
                message.setIcon(QMessageBox.Warning)
                message.setText("Saldo tidak mencukupi.")
                message.setWindowTitle("Peringatan")
                message.exec()

    def view_riwayat(self):
        riwayat_dialog = RiwayatDialog(self.riwayat.catatan_per_tanggal)
        result = riwayat_dialog.exec_()

    def filter_catatan(self):
        self.list_history.clear()
        selected_date_str = self.get_selected_date_str()

        for item in self.riwayat.get_catatan_by_tanggal(selected_date_str):
            self.list_history.addItem(item)

        self.list_history.setCurrentRow(-1)

    def hapus_catatan(self):
        selected_item = self.list_history.currentItem()
        if selected_item:
            selected_text = selected_item.text()
            tanggal_str = self.get_selected_date_str()

            self.riwayat.hapus_catatan(tanggal_str, selected_text)

            self.list_history.takeItem(self.list_history.currentRow())

    def get_selected_date_str(self):
        selected_date = self.calendar.selectedDate()
        tanggal = selected_date.day()
        bulan = selected_date.month()
        tahun = selected_date.year()
        return f"{tanggal}-{bulan}-{tahun}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MoneyTrackingApp()
    sys.exit(app.exec_())
