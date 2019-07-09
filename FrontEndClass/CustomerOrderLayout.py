from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel, ListItemButton
from BackEndClass.CustomerOrderFile import CustomerOrderBackend

Builder.load_file('Design/CustomerOrderPopups.kv')
Builder.load_file('Design/CustomerOrder.kv')

substitute = CustomerOrderBackend
color_alter = 1

class checkbutton (ListItemButton,CheckBox):
    pass


class CustomerOrder(BoxLayout):

    def __init__(self, **kwargs):
        super(CustomerOrder, self).__init__(**kwargs)
        self.initialized = 0

    def listoptions(self, *args, **kwargs):

        if not self.initialized:
            self.ids['search_results_list'].adapter.bind(on_selection_change=self.listoptions)
            self.initialized = 1

        selections = self.search_results.adapter.selection

        if len(selections) == 0:
#            self.ids['delete'].disabled = True
            self.ids['view'].disabled = True
            self.ids['invoice'].disabled = True

        if len(selections) == 1:
            self.ids['view'].disabled = False

            selection = selections[0].text
            status = substitute.get_status(ID=selection)
            if status == 'Pending':
                self.ids['invoice'].disabled = False

        if len(selections) > 1:
            self.ids['view'].disabled = True
            self.ids['invoice'].disabled = True

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
                }
            ]
        }

    def retreive_data(self,**kwargs):
        global substitute
        data,error = substitute.select(**kwargs)
        if error:
            ErrorPopup = CustomerOrderError(error)
            ErrorPopup.open()
        else:
            return data


    def retreive_items(self,**kwargs):
        global substitute
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
        pop_ups = {'Add': CustomerOrderInsert, 'Search': CustomerOrderSearch,# 'Delete':CustomerOrderDelete,
                   'View': CustomerOrderView, 'Create Invoice': CustomerOrderInvoice}
        pop = pop_ups[option](self)
        pop.open()


class CustomerOrderInvoice(Popup):

    def __init__(self, caller, **kwargs):
        super(CustomerOrderInvoice, self).__init__(**kwargs)
        self.caller = caller
        selection = self.caller.search_results.adapter.selection[0]
        data = self.caller.retreive_data(ID=selection.text)[0]
        items,availability,error = self.caller.retreive_items(ID=selection.text, StockAvailable=1)


        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget)

        inputs[0].text = str(data[0])
        inputs[1].text = str(data[1])
        inputs[2].text = str(data[3])

        for col0, col1, col2, col3, row, available in zip(inputs[3::5],inputs[4::5], inputs[5::5],inputs[6::5], items, availability ) :
            col0.text = str(row[0])
            col1.text = str(row[1])
            col2.text = str(row[2])
            col3.text = str(available[0][0])


    def insert(self):
        global substitute
        data = []
        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget.text)

        co_number = inputs[0]


        items = [input for input in inputs[3::5]]
        remaining = [input for input in inputs[5::5]]
        available = [input for input in inputs[6::5]]
        quantity = [input for input in inputs[7::5]]



        quantity = list(map(lambda x: 0 if x=='' else x, quantity))
        items = list(map(lambda x: 0 if x=='' else x, items))
        available = list(map(lambda x: 0 if x=='' else x, available))
        remaining = list(map(lambda x: 0 if x=='' else x, remaining))

        error = substitute.create_invoice(co_number=co_number, items=items,
                                          remaining=remaining,
                                          available=available, quantity=quantity)

        if error:
            ErrorPopup = CustomerOrderError(error)
            ErrorPopup.open()
        else:
            self.dismiss()
            self.caller.update_screen_list()

class CustomerOrderInsert(Popup):

    def __init__(self, caller, **kwargs):
        super(CustomerOrderInsert, self).__init__(**kwargs)
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
        co_number = inputs[1]
        items = [input for input in inputs[2::3]]
        quantities = [input for input in inputs[3::3]]
        prices = [input for input in inputs[4::3]]

        items = list(filter(None, items))
        quantities = list(filter(None, quantities))
        prices = list(filter(None, prices))

        co = substitute(cname, co_number, items, quantities, prices)
        error = co.insert()

class CustomerOrderSearch(Popup):

    def __init__(self, caller, **kwargs):
        super(CustomerOrderSearch, self).__init__(**kwargs)
        self.caller = caller

    def apply_search(self):

        conditions = {   }

        ID = self.ids['ID'].text
        if ID:
            conditions['ID']=ID

        c_name = self.ids['CustomerName'].text
        if c_name:
            conditions['CustomerName']= c_name

        pending = self.ids['pending'].active
        delivered = self.ids['delivered'].active

        Status = ''
        if pending == delivered:
            pass
        else:
            if pending:
                Status = 'Pending'
            elif delivered:
                Status = 'Delivered'

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


class CustomerOrderView(Popup):

    def __init__(self, caller, **kwargs):
        super(CustomerOrderView, self).__init__(**kwargs)
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
        inputs[3].text = str(data[4])

        inputs[-1].text = str(data[2])

        for col0, col1, col2, col3, col4, row in zip(inputs[4::5],inputs[5::5], inputs[6::5], inputs[7::5],inputs[8::5], items ) :
            col0.text = str(row[0])
            col1.text = str(row[1])
            col2.text = str(row[2])
            col3.text = str(row[3])
            col4.text = str(row[1]*row[3])



class CustomerOrderError(Popup):

    def __init__(self, error, **kwargs):
        super(CustomerOrderError, self).__init__(**kwargs)
        self.ids['label'].text = str(error)

#
# class CustomerOrderDelete(Popup):
#
#     def __init__(self, caller, **kwargs):
#         super(CustomerOrderDelete, self).__init__(**kwargs)
#         self.caller = caller
#
#     def delete(self):
#         global substitute
#         selections = self.caller.search_results.adapter.selection
#         for selection in selections:
#             substitute.delete(value=selection.text)
#         self.caller.update_screen_list()
#

