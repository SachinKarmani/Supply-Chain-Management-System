import pandas
import datetime
import mysql.connector
from BackEndClass.configs import config


class PaymentBackend:
    def __init__(self, items=[], quantity=[] ):
        self.items = items
        self.quantity = quantity

    @staticmethod
    def insert( *args, **kwargs):

        error = 0
        cur = kwargs['cur']
        try:
            command = 'INSERT INTO Payment VALUES( {}, {}, CURRENT_DATE, {}, "{}", "{}")'\
                .format(kwargs['check_number'],kwargs['invoice_num'],kwargs['check_amount'],kwargs['c_name'],kwargs['co_number'] )
            cur.execute(command)

        except Exception as err:
            error = 'Payment with same check number already exists'


        return error


    @staticmethod
    def select(*args, **kwargs):
        link = mysql.connector.connect(**config)
        cur = link.cursor()

        conditions = kwargs

        error = 0
        while(True):
            try:
                condition = conditions['CheckNumber']

            except:
                conditions['CheckNumber'] = 'CheckNumber'

            try:
                if(conditions['CheckNumber'] != 'CheckNumber'):
                    a = int(conditions['CheckNumber'])
            except:
                error = "Check Number should be integer"
                break

            command = 'SELECT CheckNumber,CustomerName,InvoiceNumber, CustomerOrderNumber, CheckAmount, CheckDate FROM Payment '
            
            command += ' WHERE CheckNumber = {} '.format(conditions['CheckNumber'])

            try:
                command += 'and CustomerOrderNumber like "{}%" '.format(conditions['CustomerOrderNumber'])
            except:
                pass

            try:
                command += 'and CustomerName like "{}%" '.format(conditions['CustomerName'])
            except:
                pass

            try:
                if conditions['InvoiceNumber']:
                    try:
                        invoice = int(conditions['InvoiceNumber'])
                    except:
                        error = 'Invoice number should be a number'
                        break
            except:
                pass


            try:
                command += 'and InvoiceNumber = {} '.format(conditions['InvoiceNumber'])
            except:
                pass


            try:
                date_after = conditions['CheckDateAfter']
                print(date_after)
                try:
                    date_after = datetime.datetime(year=int(date_after[0]), month=int(date_after[1]), day=int(date_after[2]))
                except:
                    error = 'Invalid date (after)'
                    break
                else:
                    CheckDateAfter = str(date_after.year) + '-' + str(date_after.month) + '-' + str(date_after.day)
            except:
                pass
            try:
                command += " and CheckDate >= '{}' ".format(CheckDateAfter)
            except:
                pass

            try:
                date_before = conditions['CheckDateBefore']

                try:
                    date_before = datetime.datetime(year=int(date_before[0]), month=int(date_before[1]), day=int(date_before[2]))
                except:
                    error = 'Invalid date (before)'
                    break
                else:
                    CheckDateBefore = str(date_before.year) + '-' + str(date_before.month) + '-' + str(date_before.day)
            except:
                pass
            try:
                command += " and CheckDate <= '{}' ".format(CheckDateBefore)
            except:
                pass
            break



            break
            
        if error:
            data = 0
        else:
            cur.execute(command)
            data = cur.fetchall()

        cur.close()
        return (data,error)

