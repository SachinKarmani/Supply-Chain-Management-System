import pandas
import datetime
import mysql.connector
from BackEndClass.configs import config


class StockBackend:
    def __init__(self, items=[], quantity=[] ):
        self.items = items
        self.quantity = quantity


    @staticmethod
    def update(*args, **kwargs):


        cur = kwargs['cur']

        items = kwargs['items']
        type = kwargs['type']
        if type == 'customer_order':
            items = [(item[0], -1*item[1]) for item in items ]

        for item, quantity in items:
            command = 'UPDATE STOCK SET QUANTITY = QUANTITY + ({}) where item_code = {}'.format(quantity, item)
            print(command)
            cur.execute(command)




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
                conditions['ID'] = 'Item_Code'

            try:
                if(conditions['ID'] != 'Item_Code'):
                    a = int(conditions['ID'])
            except:
                error = "ID should be integer"
                break

            command = 'SELECT Description,Item_Code, QUANTITY, IF(Quantity>Min_Quantity, "Sufficient", "Short") as Status FROM Stock '

            if conditions['ID'] != 'Item_Code':
                command += " WHERE CONCAT(Item_Code, '') like '{}%' ".format(conditions['ID'])
            else:
                command += ' WHERE Item_Code = {} '.format(conditions['ID'])

            try:
                command += 'and Description like "{}%" '.format(conditions['Description'])
            except:
                pass

            try:
                command += 'and IF(Quantity>Min_Quantity, "Sufficient", "Short") = "{}" '.format(conditions['Status'])
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
    def get_quantity(*args, **kwargs):
        link = mysql.connector.connect(**config)
        cur = link.cursor()

        conditions = kwargs

        error = 0
        while(True):
            try:
                condition = conditions['ID']
            except:
                error = "Error in conversion"
                break

            command = 'SELECT QUANTITY FROM Stock where item_code = {}'.format(str(condition))


            break


        if error:
            data = 0

        else:
            cur.execute(command)
            data = cur.fetchall()

        cur.close()
        return (data,error)

