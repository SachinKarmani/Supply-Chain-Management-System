import pandas
import datetime
import mysql.connector
from BackEndClass.StockFile import StockBackend
from BackEndClass.configs import config


class PurchaseOrderBackend:
    def __init__(self, items=[], quantity=[] ):
        self.items = items
        self.quantity = quantity


    def insert(self, *args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()

        error = 0
        while(True):
            i = 1

            print(self.items, self.quantity)
            if len(self.items) != len(self.quantity):
                error = 'Values missing'
                break

            if len(self.items) != len(set(self.items)):
                error = 'Repetition of Items found'
                break

            total = 0
            file = 'C:\\Users\\Sachin\\Desktop\\Buffer zone\\project v3\\BackEndClass\\prices.xlsx'
            df = pandas.read_excel(file, index_col='Item_Code')
            for item, qty in zip(self.items, self.quantity):
                if not item:
                    if i == 1:
                        error = 'No item(s) found'
                        break
                    else:
                        break

                try:
                    item = int(item)
                except:
                    error = 'Invalid item entered at row ' + str(i)
                    break
                try:
                    quantity = int(qty)
                except:
                    error = 'Invalid quantity entered at row ' + str(i)
                    break
                try:
                    price = df.loc[item, 'Price']
                    print (price)
                    total += int(price)*int(qty)
                except Exception as err:
                    print(err)
                    error = 'Item # ' + str(i)+ ' does not exist'
                    break
                i+=1

            if not error:
                try:
                    command = 'INSERT INTO PurchaseOrder(Amount, Status, PODate) VALUES( {}, "Pending", CURRENT_DATE)'\
                        .format(total)
                    cur.execute(command)
                    cur.execute('SELECT LAST_INSERT_ID();')
                    data = cur.fetchall()
                    id = data[0][0]
                except Exception as err:
                    error = err
                    print(err)
                try:
                    df = pandas.read_excel(file, index_col='Item_Code')
                    for item, qty in zip(self.items, self.quantity):
                        print(df)
                        price = df.loc[int(item), 'Price']
                        command = 'INSERT INTO PO_items VALUES( {},{},{}, {})'.format(id, item, qty, price)
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
    def mark_status(*args, **kwargs):
        link = mysql.connector.connect(**config)
        cur = link.cursor()

        po_number = kwargs['ID']

        command = 'SELECT Status FROM PurchaseOrder WHERE ID = {} '.format(po_number)
        cur.execute(command)
        status = cur.fetchone()[0]
        if status == 'Received':
            return 'Received'

        else:
            items = PurchaseOrderBackend.select_items(ID=po_number)
            items = [(item[0],item[1]) for item in items]
            StockBackend.update(cur=cur,items=items, type='purchase')

            command = 'Update PurchaseOrder set Status = {} WHERE ID = {} '.format("'Received'", po_number)
            cur.execute(command)

            link.commit()
            cur.close()

            return 'Marked'

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

            command = 'SELECT ID, PODate,Amount,Status FROM PurchaseOrder WHERE ID = {} '.format(conditions['ID'])

            try:
                command += 'and Status = "{}" '.format(conditions['Status'])
            except:
                pass


            try:
                date_after = conditions['PODateAfter']
                print(date_after)
                try:
                    date_after = datetime.datetime(year=int(date_after[0]), month=int(date_after[1]), day=int(date_after[2]))
                except:
                    error = 'Invalid date (after)'
                    break
                else:
                    PODateAfter = str(date_after.year) + '-' + str(date_after.month) + '-' + str(date_after.day)
            except:
                pass
            try:
                command += " and PODate >= '{}' ".format(PODateAfter)
            except:
                pass

            try:
                date_before = conditions['PODateBefore']

                try:
                    date_before = datetime.datetime(year=int(date_before[0]), month=int(date_before[1]), day=int(date_before[2]))
                except:
                    error = 'Invalid date (before)'
                    break
                else:
                    PODateBefore = str(date_before.year) + '-' + str(date_before.month) + '-' + str(date_before.day)
            except:
                pass
            try:
                command += " and PODate <= '{}' ".format(PODateBefore)
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
        command = 'SELECT Item_Code, Quantity, Price FROM po_items WHERE ID = {} '.format(kwargs['ID'])
        cur.execute(command)
        data = cur.fetchall()
        cur.close()
        return data

