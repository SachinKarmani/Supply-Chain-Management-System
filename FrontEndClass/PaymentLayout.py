from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel, ListItemButton
from BackEndClass.PaymentFile import PaymentBackend

Builder.load_file('Design/Payment.kv')

substitute = PaymentBackend
color_alter = 1

class Payment(BoxLayout):

    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)

    def args_converter(self, row_index, rec):
        """"Pre requisite function for a ListView """""
        global color_alter
        text_color = (0.5, 0.5, 0.5, 1)

        if (color_alter>0):
            color = (0.25, 0.25, .25, 1)
        else:
            color = (0.85,0.85,0.85, 1)
        color_alter = color_alter * -1

        return {
            'text': str(rec[0]),
            'size_hint_y': None,
            'padding':-1,
            'spacing':-10,
            'height': 25,
            'cls_dicts': [
                {
                    'cls': ListItemButton,
                    'kwargs': {
                        'text': str(rec[0]),
                        'disabled':True,
                        'background_disabled_normal': '',
                        'color':text_color,
                        'deselected_color':color,
                        'selected_color':(0,0,0,1),
                    }},
                {
                    'cls': ListItemButton,
                    'kwargs': {
                        'text': str(rec[1]),
                        'disabled':True,
                        'background_disabled_normal': '',
                        'color':text_color,
                        'deselected_color':color,
                        'selected_color':(0,0,0,1)
                    }},
                {
                    'cls': ListItemButton,
                    'kwargs': {
                        'text': str(rec[2]),
                        'disabled': True,
                        'background_disabled_normal': '',
                        'color': text_color,
                        'deselected_color': color,
                        'selected_color': (0, 0, 0, 1)

                    }
                },
                {
                    'cls': ListItemButton,
                    'kwargs': {
                        'text': str(rec[3]),
                        'disabled':True,
                        'background_disabled_normal': '',
                        'color':text_color,
                        'deselected_color':color,
                        'selected_color':(0,0,0,1)

                    }
                },
                {
                    'cls': ListItemButton,
                    'kwargs': {
                        'text': str(rec[4]),
                        'disabled':True,
                        'background_disabled_normal': '',
                        'color':text_color,
                        'deselected_color':color,
                        'selected_color':(0,0,0,1)

                    }
                },
                {
                    'cls': ListItemButton,
                    'kwargs': {
                        'text': str(rec[5]),
                        'disabled':True,
                        'background_disabled_normal': '',
                        'color':text_color,
                        'deselected_color':color,
                        'selected_color':(0,0,0,1)

                    }
                }
            ]
        }

    def retreive_data(self,**kwargs):
        global substitute
        data,error = substitute.select(**kwargs)
        if error:
            ErrorPopup = PurchaseOrderError(error)
            ErrorPopup.open()
        else:
            return data


    def update_screen_list(self, **kwargs):
        global color_alter
        color_alter = 1
        data = self.retreive_data(**kwargs)
        if data:
            self.search_results.item_strings = data
            self.search_results.adapter.data.clear()
            self.search_results.adapter.data.extend(data)
            self.search_results._trigger_reset_populate()


    def call_popup(self, option):
        pop_ups = {'Search': PaymentSearch}
        pop = pop_ups[option](self)
        pop.open()


class PaymentSearch(Popup):

    def __init__(self, caller, **kwargs):
        super(PaymentSearch, self).__init__(**kwargs)
        self.caller = caller

    def apply_search(self):

        conditions = {}

        CheckNumber = self.ids['CheckNumber'].text
        if CheckNumber:
            conditions['CheckNumber']=CheckNumber

        InvoiceNumber = self.ids['InvoiceNumber'].text
        if InvoiceNumber:
            conditions['InvoiceNumber']=InvoiceNumber

        CustomerName = self.ids['CustomerName'].text
        if CustomerName:
            conditions['CustomerName']=CustomerName

        CustomerOrderNumber = self.ids['CustomerOrderNumber'].text
        if CustomerOrderNumber:
            conditions['CustomerOrderNumber']=CustomerOrderNumber


        year = str (self.ids['Year_B'].text)
        month = str(self.ids['Month_B'].text)
        date = str(self.ids['Day_B'].text)

        if  year == month == date == '':
            PODateBefore=''
        else :
            if year == '':
                year = 'error'
            if month == '':
                month = 'error'
            if date == '':
                date = '01'
            PODateBefore = [year, month, date]

        if PODateBefore:
            conditions['PODateBefore']=PODateBefore


        year = str(self.ids['Year_A'].text)
        month = str(self.ids['Month_A'].text)
        date = str(self.ids['Day_A'].text)

        if year == month == date == '':
            PODateAfter = ''
        else:
            if year == '':
                year = 'error'
            if month == '':
                month = 'error'
            if date == '':
                date = '01'
            PODateAfter = [year, month, date]

        if PODateAfter:
            conditions['PODateAfter']=PODateAfter

        self.caller.update_screen_list(**conditions)



class PurchaseOrderError(Popup):

    def __init__(self, error, **kwargs):
        super(PurchaseOrderError, self).__init__(**kwargs)
        self.ids['label'].text = str(error)


