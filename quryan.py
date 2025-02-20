from PyQt5 import QtWidgets, QtGui, QtCore
import sqlite3
import random
import os

class QuranApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QURAN.E")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #e8f5e9; font-family: Arial;")
        
        # ✅ App Icon Set Karna
        self.setWindowIcon(QtGui.QIcon("icon.ico"))
        
        # Database Connection
        self.db = sqlite3.connect("quran.db")
        self.cursor = self.db.cursor()
        
        # Load Last Session
        self.last_surah = self.load_last_session()
        
        # Main Layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        
        # Three Dots Menu
        self.menu_button = QtWidgets.QPushButton("⋮")
        self.menu_button.setMaximumWidth(40)
        self.menu_button.clicked.connect(self.open_menu)
        self.layout.addWidget(self.menu_button, alignment=QtCore.Qt.AlignLeft)
        
        # Surah Display
        self.text_area = QtWidgets.QTextBrowser()
        self.text_area.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)  # ✅ Text Permanent Ho Gaya
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)
        
        # Load Surah (First Surah if first time, last session otherwise)
        self.load_surah(self.last_surah if self.last_surah else "1")
    
    def open_menu(self):
        menu = QtWidgets.QMenu()
        
        # Search Option
        search_action = QtWidgets.QAction("تلاش کریں", self)
        search_action.triggered.connect(self.open_search)
        menu.addAction(search_action)
        
        # Surah Selection Option
        surah_action = QtWidgets.QAction("سورہ منتخب کریں", self)
        surah_action.triggered.connect(self.open_surah_selection)
        menu.addAction(surah_action)
        
        # Undo Option
        undo_action = QtWidgets.QAction("واپس جائیں", self)
        undo_action.triggered.connect(self.undo_last_action)
        menu.addAction(undo_action)
        
        menu.exec_(self.menu_button.mapToGlobal(QtCore.QPoint(0, self.menu_button.height())))
    
    def open_search(self):
        search_dialog = QtWidgets.QInputDialog()
        search_dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        search_dialog.setWindowTitle("تلاش کریں")
        search_dialog.setLabelText("آیت نمبر یا کوئی لفظ درج کریں:")
        ok = search_dialog.exec_()
        
        if ok:
            query = search_dialog.textValue()
            
            # Search by Ayah number or text
            self.cursor.execute("SELECT surah_name, ayah_id, arabic_text, urdu_translation FROM quran WHERE arabic_text LIKE ? OR urdu_translation LIKE ? OR ayah_id LIKE ?", (f"%{query}%", f"%{query}%", f"%{query}%"))
            results = self.cursor.fetchall()
            
            if results:
                result_text = "\n".join([f"{row[0]} - آیت {row[1]}\n{row[2]}\n{row[3]}" for row in results])
                QtWidgets.QMessageBox.information(self, "نتائج", result_text)
            else:
                QtWidgets.QMessageBox.warning(self, "نتائج نہیں ملے", "کوئی مماثل سورہ یا آیت نہیں ملی۔")
    
    def open_surah_selection(self):
        self.cursor.execute("SELECT DISTINCT surah_name FROM quran")
        surahs = [row[0] for row in self.cursor.fetchall()]
        surah, ok = QtWidgets.QInputDialog.getItem(self, "سورہ منتخب کریں", "سورہ منتخب کریں:", surahs, 0, False)
        
        if ok and surah:
            self.cursor.execute("SELECT surah_id FROM quran WHERE surah_name = ? LIMIT 1", (surah,))
            result = self.cursor.fetchone()
            if result:
                self.load_surah(str(result[0]))
    
    def undo_last_action(self):
        self.load_surah(self.last_surah)
    
    def load_surah(self, surah_id):
        self.cursor.execute("SELECT ayah_id, arabic_text, urdu_translation FROM quran WHERE surah_id=?", (surah_id,))
        ayahs = self.cursor.fetchall()
        
        text = ""
        for ayah in ayahs:
            urdu_color = random.choice(["#8B0000", "#006400", "#00008B", "#4B0082", "#800000", "#2F4F4F"])
            text += f"<b>{ayah[0]}:</b> <span style='color:black;'>{ayah[1]}</span><br><span style='color:{urdu_color};'>{ayah[2]}</span><hr>"
        
        self.text_area.setHtml(text)
        self.save_last_session(surah_id)
    
    def save_last_session(self, surah_id):
        with open("last_session.txt", "w") as file:
            file.write(str(surah_id))
    
    def load_last_session(self):
        if os.path.exists("last_session.txt"):
            with open("last_session.txt", "r") as file:
                return file.read()
        return None
    
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.text_area.zoomIn(1)
        else:
            self.text_area.zoomOut(1)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QuranApp()
    window.show()
    sys.exit(app.exec_())
