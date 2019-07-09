import pandas
import datetime
import mysql.connector
from BackEndClass.configs import config
from BackEndClass.PaymentFile import PaymentBackend


class InvoiceBackend:
    def __init__(self, co_number, co_name, prices = [], items=[], quantities=[] ):
        self.items = items
        self.quantities = quantities
        self.prices = prices
        self.co_number = co_number
        self.co_name = co_name


    def insert(self, *args, **kwargs):

        cur = kwargs['cur']

        error = 0
        while(True):
            i = 1

            total = 0
            for qty,price in zip(self.quantities, self.prices):
                total += qty*price

            try:
                command = 'INSERT INTO Invoice(CustomerOrderNumber, CustomerName, InvoiceDate, ' \
                          'Status, Amount, Remaining) VALUES( "{}", "{}", CURRENT_DATE, "Pending", {},{})'\
                    .format(self.co_number, self.co_name, total, total)
                cur.execute(command)
                cur.execute('SELECT LAST_INSERT_ID();')
                data = cur.fetchall()
                id = data[0][0]
            except Exception as err:
                error = err
                break

            try:
                for item, qty,price in zip(self.items, self.quantities, self.prices):
                    command = 'INSERT INTO Invoice_items VALUES( {},{},{}, {})'\
                        .format(id, item, qty, price)
                    cur.execute(command)
            except Exception as err:
                error = err
                break

            break

        return error

    @staticmethod
    def select(*args, **kwargs):
        link = mysql.connector.connect(**config)
        cur = link.cursor()

        conditions = kwargs

        error = 0
        while(True):
            try:
                condition = conditions['ID']
            except:
                conditions['ID'] = 'ID'

            try:
                if(conditions['ID'] != 'ID'):
                    a = int(conditions['ID'])
            except:
                error = "ID should be integer"
                break

            try:
                remaining_req = ',' + conditions['Remaining']
            except:
                remaining_req = ''

            command = 'SELECT ID, CustomerName,CustomerOrderNumber,Amount,InvoiceDate,Status {} FROM Invoice WHERE ID = {} '\
                .format( remaining_req, conditions['ID'])

            try:
                command += 'and Status = "{}" '.format(conditions['Status'])
            except:
                pass

            try:
                command += 'and CustomerName like "{}%" '.format(conditions['CustomerName'])
            except:
                pass

            try:
                command += 'and CustomerOrderNumber like "{}%" '.format(conditions['CustomerOrderNumber'])
            except:
                pass


            try:
                date_after = conditions['InvoiceDateAfter']
                print(date_after)
                try:
                    date_after = datetime.datetime(year=int(date_after[0]), month=int(date_after[1]), day=int(date_after[2]))
                except:
                    error = 'Invalid date (after)'
                    break
                else:
                    InvoiceDateAfter = str(date_after.year) + '-' + str(date_after.month) + '-' + str(date_after.day)
            except:
                pass
            try:
                command += " and InvoiceDate >= '{}' ".format(InvoiceDateAfter)
            except:
                pass

            try:
                date_before = conditions['InvoiceDateBefore']

                try:
                    date_before = datetime.datetime(year=int(date_before[0]), month=int(date_before[1]), day=int(date_before[2]))
                except:
                    error = 'Invalid date (before)'
                    break
                else:
                    InvoiceDateBefore = str(date_before.year) + '-' + str(date_before.month) + '-' + str(date_before.day)
            except:
                pass
            try:
                command += " and InvoiceDate <= '{}' ".format(InvoiceDateBefore)
            except:
                pass
            break


        if error:
            data = 0
        else:
            print('here', command)
            cur.execute(command)
            data = cur.fetchall()

        cur.close()
        return (data,error)

    @staticmethod
    def select_items(*args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()
        command = 'SELECT Item_Code, Quantity, Price FROM invoice_items WHERE ID = {} '.format(kwargs['ID'])
        cur.execute(command)
        data = cur.fetchall()
        cur.close()
        return data

    @staticmethod
    def add_payment(*args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()
        error = 0

        invoice_num = int(kwargs['invoice_num'])
        c_name = kwargs['c_name']
        co_number = kwargs['co_number']
        co_rem = int(kwargs['co_rem'])

        try:
            check_number = kwargs['check_number']
            check_amount = kwargs['check_amount']
        except:
            error = 'Values Missing'
            return error

        try:
            check_number = int(check_number)
            check_amount = int(check_amount)
        except:
            error = 'Invalid values'
            return error

        balance =  co_rem - check_amount
        if balance < 0:
            error = 'Check amount greater than remaining amount'
            return error

        status = 'Pending'
        if  balance == 0:
            status = 'Paid'

        error = PaymentBackend.insert(invoice_num=invoice_num, c_name=c_name, cur=cur,
                              co_number=co_number, check_amount=check_amount, check_number=check_number)

        if error:
            return error

        command = 'Update Invoice set Remaining = {}, Status = "{}" WHERE ID = {} '\
            .format(balance, status, invoice_num)

        cur.execute(command)

        if error:
            link.rollback()
        else:
            link.commit()

        cur.close()
        return error

    def get_status(*args, **kwargs):
        link1 = mysql.connector.connect(**config)
        cur1 = link1.cursor()
        command = 'SELECT Status FROM Invoice WHERE ID = "{}"'\
            .format(kwargs['ID'])
        cur1.execute(command)
        data = cur1.fetchone()[0]
        cur1.close()
        return data
