from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel, ListItemButton
from BackEndClass.PurchaseOrderFile import PurchaseOrderBackend

Builder.load_file('Design/PurchaseOrderPopups.kv')
Builder.load_file('Design/PurchaseOrder.kv')

substitute = PurchaseOrderBackend

color_alter = 1

class checkbutton (ListItemButton,CheckBox):
    pass


class PurchaseOrder(BoxLayout):

    def __init__(self, **kwargs):
        super(PurchaseOrder, self).__init__(**kwargs)
        self.initialized = 0

    def listoptions(self, *args, **kwargs):

        if not self.initialized:
            self.ids['search_results_list'].adapter.bind(on_selection_change=self.listoptions)
            self.initialized = 1

        selections = self.search_results.adapter.selection

        if len(selections) == 0:

            self.ids['view'].disabled = True
            self.ids['mark_received'].disabled = True

        if len(selections) == 1:
            self.ids['mark_received'].disabled = False
            self.ids['view'].disabled = False

        if len(selections) > 1:
            self.ids['mark_received'].disabled = True
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


    def retreive_items(self,**kwargs):
        global substitute
        print(kwargs)
        data = substitute.select_items(**kwargs)
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
        pop_ups = {'Add': PurchaseOrderInsert, 'Search': PurchaseOrderSearch,
                   'View': PurchaseOrderView, 'Mark Received': PurchaseOrderMark}
        pop = pop_ups[option](self)
        pop.open()


class PurchaseOrderInsert(Popup):

    def __init__(self, caller, **kwargs):
        super(PurchaseOrderInsert, self).__init__(**kwargs)
        self.caller = caller

    def insert(self):
        global substitute
        data = []
        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget.text)
                print(widget, "   ", widget.text)
        items = [input for input in inputs[0::2]]
        quantity = [input for input in inputs[1::2]]
        items = list(filter(None, items))
        quantity = list(filter(None, quantity))
        po = substitute(items, quantity)
        error = po.insert()
        if error:
            ErrorPopup = PurchaseOrderError(error)
            ErrorPopup.open()
        else:
            self.dismiss()
            self.caller.update_screen_list()

class PurchaseOrderSearch(Popup):

    def __init__(self, caller, **kwargs):
        super(PurchaseOrderSearch, self).__init__(**kwargs)
        self.caller = caller

    def apply_search(self):

        conditions = {   }

        ID = self.ids['ID'].text
        if ID:
            conditions['ID']=ID

        pending = self.ids['pending'].active
        received = self.ids['received'].active

        Status = ''
        if pending == received:
            pass
        else:
            if pending:
                Status = 'Pending'
            elif received:
                Status = 'Received'

        if Status:
            conditions['Status'] = Status

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


class PurchaseOrderView(Popup):

    def __init__(self, caller, **kwargs):
        super(PurchaseOrderView, self).__init__(**kwargs)
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
        inputs[1].text = str(data[1])
        inputs[2].text = str(data[3])
        inputs[-1].text = str(data[2])

        for col0, col1, col2, col3, row in zip(inputs[3::4],inputs[4::4], inputs[5::4], inputs[6::4], items ) :
            col0.text = str(row[0])
            col1.text = str(row[1])
            col2.text = str(row[2])
            col3.text = str(row[1]*row[2])

class PurchaseOrderMark(Popup):

    def __init__(self, caller, **kwargs):
        global substitute
        super(PurchaseOrderMark, self).__init__(**kwargs)
        selection = caller.search_results.adapter.selection[0]

        status = substitute.mark_status(ID=selection.text)

        if status == 'Marked':
            self.ids['status_label'].text = 'Purchase order marked received'
            caller.update_screen_list()

        else:
            self.ids['status_label'].text = 'Purchase order already received'



class PurchaseOrderError(Popup):

    def __init__(self, error, **kwargs):
        super(PurchaseOrderError, self).__init__(**kwargs)
        self.ids['label'].text = str(error)


