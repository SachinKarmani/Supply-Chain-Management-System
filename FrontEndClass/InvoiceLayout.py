from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel, ListItemButton
from BackEndClass.InvoiceFile import InvoiceBackend

Builder.load_file('Design/InvoicePopups.kv')
Builder.load_file('Design/Invoice.kv')

substitute = InvoiceBackend
color_alter = 1

class checkbutton (ListItemButton,CheckBox):
    pass


class Invoice(BoxLayout):

    def __init__(self, **kwargs):
        super(Invoice, self).__init__(**kwargs)
        self.initialized = 0

    def listoptions(self, *args, **kwargs):

        if not self.initialized:
            self.ids['search_results_list'].adapter.bind(on_selection_change=self.listoptions)
            self.initialized = 1

        selections = self.search_results.adapter.selection

        if len(selections) == 0:
            self.ids['view'].disabled = True
            self.ids['add'].disabled = True

        if len(selections) == 1:
            self.ids['view'].disabled = False

            selection = selections[0].text
            status = substitute.get_status(ID=selection)
            if status == 'Pending':
                self.ids['add'].disabled = False


        if len(selections) > 1:
            self.ids['view'].disabled = True
            self.ids['add'].disabled = True



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
                        'size_hint':(0.35,1),
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
            ErrorPopup = InvoiceError(error)
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
        pop_ups = {'Add Payment': InvoicePayment, 'Search': InvoiceSearch,
                    'View': InvoiceView}
        pop = pop_ups[option](self)
        pop.open()


class InvoiceInsert(Popup):

    def __init__(self, caller, **kwargs):
        super(InvoiceInsert, self).__init__(**kwargs)
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
            ErrorPopup = InvoiceError(error)
            ErrorPopup.open()
        else:
            self.dismiss()
            self.caller.update_screen_list()

class InvoiceSearch(Popup):

    def __init__(self, caller, **kwargs):
        super(InvoiceSearch, self).__init__(**kwargs)
        self.caller = caller

    def apply_search(self):

        conditions = {   }

        ID = self.ids['ID'].text
        if ID:
            conditions['ID']=ID

        CustomerName = self.ids['CustomerName'].text
        if CustomerName:
            conditions['CustomerName']=CustomerName

        CustomerOrderNumber = self.ids['CustomerOrderNumber'].text
        if CustomerOrderNumber:
            conditions['CustomerOrderNumber']=CustomerOrderNumber

        pending = self.ids['pending'].active
        paid = self.ids['paid'].active

        Status = ''
        if pending == paid:
            pass
        else:
            if pending:
                Status = 'Pending'
            elif paid:
                Status = 'Paid'

        if Status:
            conditions['Status'] = Status

        year = str (self.ids['Year_B'].text)
        month = str(self.ids['Month_B'].text)
        date = str(self.ids['Day_B'].text)

        if  year == month == date == '':
            InvoiceDateBefore=''
        else :
            if year == '':
                year = 'error'
            if month == '':
                month = 'error'
            if date == '':
                date = '01'
            InvoiceDateBefore = [year, month, date]

        if InvoiceDateBefore:
            conditions['InvoiceDateBefore']=InvoiceDateBefore


        year = str(self.ids['Year_A'].text)
        month = str(self.ids['Month_A'].text)
        date = str(self.ids['Day_A'].text)

        if year == month == date == '':
            InvoiceDateAfter = ''
        else:
            if year == '':
                year = 'error'
            if month == '':
                month = 'error'
            if date == '':
                date = '01'
            InvoiceDateAfter = [year, month, date]

        if InvoiceDateAfter:
            conditions['PODateAfter']=InvoiceDateAfter

        self.caller.update_screen_list(**conditions)

class InvoiceView(Popup):

    def __init__(self, caller, **kwargs):
        super(InvoiceView, self).__init__(**kwargs)
        self.caller = caller
        selection = self.caller.search_results.adapter.selection[0]
        data = self.caller.retreive_data(ID=selection.text, Remaining="Remaining")[0]
        items = self.caller.retreive_items(ID=selection.text)
        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget)
            command = 'SELECT ID, CustomerName,CustomerOrderNumber,Amount,InvoiceDate,Status {} FROM Invoice WHERE ID = {} '\

        inputs[0].text = str(data[0])
        inputs[1].text = str(data[1])
        inputs[2].text = str(data[2])
        inputs[3].text = str(data[4])
        inputs[4].text = str(data[5])
        inputs[5].text = str(data[6])

        inputs[-1].text = str(data[3])

        for col0, col1, col2, col3, row in zip(inputs[6::4], inputs[7::4], inputs[8::4],inputs[9::4], items ) :
            col0.text = str(row[0])
            col1.text = str(row[1])
            col2.text = str(row[2])
            col3.text = str(row[1]*row[2])


class InvoicePayment(Popup):

    def __init__(self, caller, **kwargs):
        super(InvoicePayment, self).__init__(**kwargs)
        self.caller = caller
        selection = self.caller.search_results.adapter.selection[0]
        data = self.caller.retreive_data(ID=selection.text, Remaining="Remaining")[0]
        items = self.caller.retreive_items(ID=selection.text)
        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget)


        inputs[0].text = str(data[0])
        inputs[1].text = str(data[1])
        inputs[2].text = str(data[2])
        inputs[3].text = str(data[4])
        inputs[4].text = str(data[5])
        inputs[5].text = str(data[6])


    def add_payment(self):

        widgets = list(self.ids['inputs'].children)
        inputs = []
        for widget in widgets[::-1]:
            if type(widget) is TextInput:
                inputs.append(widget)

        invoice_num = inputs[0].text
        c_name = inputs[1].text
        co_number= inputs[2].text
        co_rem = inputs[5].text
        check_number =  inputs[6].text
        check_amount =  inputs[7].text

        error = substitute.add_payment(invoice_num=invoice_num, c_name=c_name, co_number=co_number,
                               co_rem=co_rem, check_number=check_number, check_amount=check_amount)

        if error:
            ErrorPopup = InvoiceError(error)
            ErrorPopup.open()
        else:
            self.dismiss()
            self.caller.update_screen_list()


class InvoiceError(Popup):

    def __init__(self, error, **kwargs):
        super(InvoiceError, self).__init__(**kwargs)
        self.ids['label'].text = str(error)


