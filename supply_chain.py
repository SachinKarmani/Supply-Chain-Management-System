# File name: layouts.py
import kivy
kivy.require('1.7.0')

from kivy.app import App
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config
from kivy.lang import Builder
from BackEndClass.EmployeeFile import Employee

Config.set('graphics', 'window_state', 'maximized')
Config.set('graphics', 'minimum_width', 800)
Config.set('graphics', 'minimum_height', 600)


substitute = None

class CustomPopup(Popup):

    def __init__(self, *args, **kwargs):  # my_widget is now the object where popup was called from.
        super(CustomPopup, self).__init__(*args, **kwargs)

    def insert(self):
        data = []
        widgets = list(self.ids['inputs'].children)
        for widget in widgets[::-1]:
            data.append(widget.text)
        print(data)

        employee = Employee(*data)
        employee.insert()



class MyGrid(GridLayout):

    def printer(self, text):
        print(text)


    def change_substitute(self, text):
        print(text)
        classes = {'Staff': Staff, 'Employee': Employee}
        choice = text
        global substitute
        substitute = classes[choice]
        print(substitute)

    def show_popup(self):
        p = CustomPopup()
        p.open()

import time

class MyToggleButton(ToggleButton):

    def change(self):
        for item in self.get_widgets(self.group):
            item.background_color = (1,1,1, 0)
            item.height = '40dp'
            item.font_size = 20
        self.background_color = (0.1, 1, 0.1, 1)
        self.height = '60dp'
#        self.font_size = 40

class MyLabel(Label):
    pass


class ProgramApp(App):
    def build(self):
        return MyGrid()


if __name__=="__main__":
    ProgramApp().run()
