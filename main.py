from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.metrics import dp
import sqlite3
import os

# 1. قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clinic.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS appointments 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, patient TEXT, doctor TEXT, time TEXT)""")
    conn.commit()
    conn.close()

def book_appointment(patient, doctor, time):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM appointments WHERE doctor=? AND time=?", (doctor, time))
    if c.fetchone():
        conn.close()
        return False
    c.execute("INSERT INTO appointments (patient, doctor, time) VALUES (?, ?, ?)", (patient, doctor, time))
    conn.commit()
    conn.close()
    return True

# 2. الواجهة
class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_db()
        self.selected_doctor = ""
        self.selected_time = ""
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation="vertical", padding=dp(30), spacing=dp(15))

        # إضافة صورة اللوجو
        logo = Image(
            source='images/logo.png', 
            size_hint_y=None, 
            height=dp(100)
        )
        layout.add_widget(logo)

        layout.add_widget(MDLabel(
            text="Dental Clinic", 
            halign="center", 
            font_style="H4", 
            size_hint_y=None, 
            height=dp(50)
        ))

        self.patient_name = MDTextField(hint_text="Patient Name", mode="rectangle")
        layout.add_widget(self.patient_name)

        # زر اختيار الطبيب (استخدام زر Kivy الأساسي)
        self.doc_btn = Button(
            text="Select Doctor", 
            size_hint_y=None, 
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1) # لون أزرق
        )
        self.doc_btn.bind(on_release=self.open_doctor_menu)
        layout.add_widget(self.doc_btn)

        # زر اختيار الوقت
        self.time_btn = Button(
            text="Select Time", 
            size_hint_y=None, 
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.time_btn.bind(on_release=self.open_time_menu)
        layout.add_widget(self.time_btn)

        layout.add_widget(MDLabel(size_hint_y=None, height=dp(10)))

        # زر التأكيد
        submit_btn = Button(
            text="Confirm Booking", 
            pos_hint={"center_x": .5}, 
            size_hint=(None, None), 
            size=(dp(200), dp(50)),
            background_color=(0, 0.7, 0.3, 1) # لون أخضر
        )
        submit_btn.bind(on_release=self.confirm_booking)
        layout.add_widget(submit_btn)

        self.add_widget(layout)

    def open_doctor_menu(self, instance):
        doctors = ["Dr. Ahmed", "Dr. Sara", "Dr. Khaled"]
        items = [{"viewclass": "OneLineListItem", "text": d, "on_release": lambda x=d: self.set_doctor(x)} for d in doctors]
        self.doc_menu = MDDropdownMenu(caller=self.doc_btn, items=items, width_mult=4)
        self.doc_menu.open()

    def set_doctor(self, doctor):
        self.selected_doctor = doctor
        self.doc_btn.text = doctor
        self.doc_menu.dismiss()

    def open_time_menu(self, instance):
        if not self.selected_doctor:
            self.show_msg("Please select a doctor first!")
            return
        times = ["09:00 AM", "10:00 AM", "11:00 AM", "01:00 PM"]
        items = [{"viewclass": "OneLineListItem", "text": t, "on_release": lambda x=t: self.set_time(x)} for t in times]
        self.time_menu = MDDropdownMenu(caller=self.time_btn, items=items, width_mult=3)
        self.time_menu.open()

    def set_time(self, time):
        self.selected_time = time
        self.time_btn.text = time
        self.time_menu.dismiss()

    def confirm_booking(self, instance):
        name = self.patient_name.text.strip()
        if not name or not self.selected_doctor or not self.selected_time:
            self.show_msg("Please fill all fields!")
            return

        if book_appointment(name, self.selected_doctor, self.selected_time):
            self.show_msg(f"Booked successfully for {name}!")
            self.patient_name.text = ""
            self.selected_doctor = ""
            self.selected_time = ""
            self.doc_btn.text = "Select Doctor"
            self.time_btn.text = "Select Time"
        else:
            self.show_msg("This time slot is already booked!")

    def show_msg(self, text):
        Snackbar(text=text).open()

class DentalApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return MainScreen()

if __name__ == "__main__":
    DentalApp().run()