import pandas
import datetime
import mysql.connector
from BackEndClass.configs import config

class QuotationBackend:
    def __init__(self, cname, items=[], prices=[] ):
        self.cname = cname
        self.items = items
        self.prices = prices

    def insert(self, *args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()

        error = 0
        file = 'C:\\Users\\Sachin\\Desktop\\Buffer zone\\project v3\\BackEndClass\\prices.xlsx'
        df = pandas.read_excel(file, index_col='Item_Code')

        while(True):

            i = 1

            if len(self.items) != len(self.prices):
                error = 'Values missing'
                break

            if len(self.items) != len(set(self.items)):
                error = 'Repetition of Items found'
                break

            if (len(self.items)) == 0:
                error = 'No item(s) found'
                break

            for item, price in zip(self.items, self.prices):
                if not item:
                    break

                try:
                    item = int(item)
                except:
                    error = 'Invalid item entered at row ' + str(i)
                    break
                try:
                    price = int(price)
                except:
                    error = 'Invalid price entered at row ' + str(i)
                    break
                try:
                    price = df.loc[item, 'Price']
                except Exception as err:
                    print(err)
                    error = 'Item # ' + str(i)+ ' does not exist'
                    break
                i+=1

            if not error:
                if self.cname:
                    command = 'INSERT INTO customer VALUES( "{}" )'.format(self.cname)
                else:
                    error = 'No company entered'
                    break

                try:
                    cur.execute(command)
                except:
                    pass

                command = 'INSERT INTO quotation(CustomerName, QDate) VALUES( "{}", CURRENT_DATE)'.format(self.cname)
                cur.execute(command)

                cur.execute('SELECT LAST_INSERT_ID();')
                data = cur.fetchall()
                id = data[0][0]

                for item, price in zip(self.items, self.prices):
                    try:
                        command = 'INSERT INTO quotation_items VALUES( {},{},{})'.format(id, item, price)
                        cur.execute(command)
                    except Exception as err:
                        error = err
                        print(err)

            break

        if error:
            link.rollback()
        else:
            link.commit()
        cur.close()
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

            command = 'SELECT * FROM quotation WHERE ID = {} '.format(conditions['ID'])

            try:
                command += 'and CustomerName like "{}%" '.format(conditions['CustomerName'])
            except:
                pass

            try:
                date_after = conditions['QDateAfter']
                print(date_after)
                try:
                    date_after = datetime.datetime(year=int(date_after[0]), month=int(date_after[1]), day=int(date_after[2]))
                except:
                    error = 'Invalid date (after)'
                    break
                else:
                    QDateAfter = str(date_after.year) + '-' + str(date_after.month) + '-' + str(date_after.day)
            except:
                pass
            try:
                command += " and QDate >= '{}' ".format(QDateAfter)
            except:
                pass

            try:
                date_before = conditions['QDateBefore']

                try:
                    date_before = datetime.datetime(year=int(date_before[0]), month=int(date_before[1]), day=int(date_before[2]))
                except:
                    error = 'Invalid date (before)'
                    break
                else:
                    QDateBefore = str(date_before.year) + '-' + str(date_before.month) + '-' + str(date_before.day)
            except:
                pass
            try:
                command += " and QDate <= '{}' ".format(QDateBefore)
            except:
                pass
            break


        if error:
            data = 0
        else:
            cur.execute(command)
            data = cur.fetchall()

        cur.close()
        return (data,error)

    @staticmethod
    def select_items(*args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()
        command = 'SELECT Item_Code, Price FROM quotation_items WHERE ID = {} '.format(kwargs['ID'])
        cur.execute(command)
        data = cur.fetchall()
        cur.close()
        return data
