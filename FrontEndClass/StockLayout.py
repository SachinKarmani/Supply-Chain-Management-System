from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel, ListItemButton
from BackEndClass.StockFile import StockBackend

Builder.load_file('Design/Stock.kv')

substitute = StockBackend
color_alter = 1

class Stock(BoxLayout):

    def __init__(self, **kwargs):
        super(Stock, self).__init__(**kwargs)

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
        pop_ups = {'Search': StockSearch}
        pop = pop_ups[option](self)
        pop.open()


class StockSearch(Popup):

    def __init__(self, caller, **kwargs):
        super(StockSearch, self).__init__(**kwargs)
        self.caller = caller

    def apply_search(self):

        conditions = {}

        ID = self.ids['ID'].text
        if ID:
            conditions['ID']=ID

        Description = self.ids['description'].text
        if Description:
            conditions['Description']=Description

        short = self.ids['short'].active
        sufficient = self.ids['sufficient'].active

        Status = ''
        if short == sufficient:
            pass
        else:
            if short:
                Status = 'short'
            elif sufficient:
                Status = 'Sufficient'

        if Status:
            conditions['Status'] = Status

        self.caller.update_screen_list(**conditions)


class PurchaseOrderError(Popup):

    def __init__(self, error, **kwargs):
        super(PurchaseOrderError, self).__init__(**kwargs)
        self.ids['label'].text = str(error)


