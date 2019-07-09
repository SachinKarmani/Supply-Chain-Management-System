from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel, ListItemButton
from BackEndClass.QuotationFile import QuotationBackend

Builder.load_file('Design/QuotationPopups.kv')
Builder.load_file('Design/Quotation.kv')

substitute = QuotationBackend

color_alter = 1

#
# Builder.load_string('''
# <ListItemLabel>:
#
#         # canvas.before:
#         #     Color:
#         #         rgba:0,0,0,1
#         #     BorderImage:
#         #         pos: self.x -1 , self.y -1
#         #         size: self.width + 1, self.height + 1
#         #     Color:
#         #         rgba: 0.1, 1, 0.1, 1
#         #     Rectangle:
#         #         pos: self.x , self.y
#         #         size: self.width, self.height
#
#''')

class checkbutton (ListItemButton,CheckBox):
    pass


class Quotation(BoxLayout):

    def __init__(self, **kwargs):
        super(Quotation, self).__init__(**kwargs)
        self.initialized = 0

    def listoptions(self, *args, **kwargs):

        if not self.initialized:
            self.ids['search_results_list'].adapter.bind(on_selection_change=self.listoptions)
            self.initialized = 1

        selections = self.search_results.adapter.selection


        if len(selections) == 0:
            self.ids['view'].disabled = True

        if len(selections) == 1:
            self.ids['view'].disabled = False

        if len(selections) > 1:
            self.ids['view'].disabled = True

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
                    'cls': checkbutton,
                    'kwargs': {
                        'text': str(rec[0]),
                        'font_size': '1sp',
                        'on_press':self.listoptions,
                        'background_normal': '',
                        'size_hint':(0.33,1),
                        'color':(1,0,1,1),
                        'deselected_color':color,
                        'selected_color':(0,0,0,1)
                    }},
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
            ErrorPopup = QuotationError(error)
            ErrorPopup.open()
        else:
            return data


    def retreive_items(self,**kwargs):
        global substitute
        print(kwargs)
        data = substitute.select_items(**kwargs)
        return data


    def update_screen_list(self, **kwargs):
        global color_alter
        color_alter = 1
        data = self.retreive_data(**kwargs)
        self.search_results.item_strings = data
        self.search_results.adapter.data.clear()
        self.search_results.adapter.data.extend(data)
        self.search_results._trigger_reset_populate()


    def call_popup(self, option):
        pop_ups = {'Add': QuotationInsert, 'Search': QuotationSearch,
                   'View': QuotationView}
        pop = pop_ups[option](self)
        pop.open()


class QuotationInsert(Popup):

    def __init__(self, caller, **kwargs):
        super(QuotationInsert, self).__init__(**kwargs)
        self.caller = caller

    def insert(self):
        global substitute
        data = []
        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget.text)
        cname = inputs[0]
        items = [input for input in inputs[1::2]]
        prices = [input for input in inputs[2::2]]
        items = list(filter(None, items))
        prices = list(filter(None, prices))
        quotation = substitute(cname, items, prices)
        error = quotation.insert()
        if error:
            ErrorPopup = QuotationError(error)
            ErrorPopup.open()
        else:
            self.dismiss()
            self.caller.update_screen_list()

class QuotationSearch(Popup):

    def __init__(self, caller, **kwargs):
        super(QuotationSearch, self).__init__(**kwargs)
        self.caller = caller

    def apply_search(self):

        conditions = {   }

        ID = self.ids['ID'].text
        if ID:
            conditions['ID']=ID
        CustomerName = self.ids['CustomerName'].text
        if CustomerName:
            conditions['CustomerName']=CustomerName

        year = str (self.ids['Year_B'].text)
        month = str(self.ids['Month_B'].text)
        date = str(self.ids['Day_B'].text)

        if  year == month == date == '':
            QDateBefore=''
        else :
            if year == '':
                year = 'error'
            if month == '':
                month = 'error'
            if date == '':
                date = '01'
            QDateBefore = [year, month, date]

        if QDateBefore:
            conditions['QDateBefore']=QDateBefore


        year = str(self.ids['Year_A'].text)
        month = str(self.ids['Month_A'].text)
        date = str(self.ids['Day_A'].text)

        if year == month == date == '':
            QDateAfter = ''
        else:
            if year == '':
                year = 'error'
            if month == '':
                month = 'error'
            if date == '':
                date = '01'
            QDateAfter = [year, month, date]

        if QDateAfter:
            conditions['QDateAfter']=QDateAfter

        self.caller.update_screen_list(**conditions)


class QuotationView(Popup):

    def __init__(self, caller, **kwargs):
        super(QuotationView, self).__init__(**kwargs)
        self.caller = caller
        selection = self.caller.search_results.adapter.selection[0]
        data = self.caller.retreive_data(ID=selection.text)[0]
        items = self.caller.retreive_items(ID=selection.text)
        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget)

        inputs[0].text = str(data[0])
        inputs[1].text = str(data[2])
        inputs[2].text = str(data[1])

        for col0, col1, row in zip(inputs[3::2],inputs[4::2], items ) :
            col0.text = str(row[0])
            col1.text = str(row[1])

class QuotationError(Popup):

    def __init__(self, error, **kwargs):
        super(QuotationError, self).__init__(**kwargs)
        self.ids['label'].text = str(error)

