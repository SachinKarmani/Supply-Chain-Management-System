import pandas
import datetime
import mysql.connector
from BackEndClass.configs import config
from BackEndClass.StockFile import StockBackend
from BackEndClass.InvoiceFile import InvoiceBackend

class CustomerOrderBackend:
    def __init__(self, cname, co_number, items=[], quantity=[], prices = []):
        self.cname = cname
        self.co_number = co_number
        self.items = items
        self.quantity = quantity
        self.prices = prices


    def insert(self, *args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()

        error = 0
        while(True):
            i = 1



            if len(self.items) != len(self.quantity):
                if len(self.items) != len(self.prices):
                    error = 'Values missing'
                    break

            if (len(self.items)) == 0:
                error = 'No item(s) found'
                break

            if len(self.items) != len(set(self.items)):
                error = 'Repetition of Items found'
                break

            total = 0
            file = 'C:\\Users\\Sachin\\Desktop\\Buffer zone\\project v3\\BackEndClass\\prices.xlsx'
            df = pandas.read_excel(file, index_col='Item_Code')
            for item, qty, price in zip(self.items, self.quantity, self.prices):
                if not item:
                    break

                try:
                    item = int(item)
                except:
                    error = 'Invalid item entered at row ' + str(i)
                    break
                try:
                    qty = int(qty)
                except:
                    error = 'Invalid quantity entered at row ' + str(i)
                    break
                try:
                    price = int(price)
                except:
                    error = 'Invalid price entered at row ' + str(i)
                    break
                try:
                    item_check = df.loc[item, 'Price']
                    total += int(price)*int(qty)
                except Exception as err:
                    print(err)
                    error = 'Item # ' + str(i)+ ' does not exist'
                    break
                i+=1

            if not error:

                if self.cname:
                    pass
                else:
                    error = 'No company entered'
                    break

                if self.co_number:
                    pass
                else:
                    error = 'No customer order number entered'
                    break

                try:
                    command = 'INSERT INTO CustomerOrder(CustomerOrderNumber, CustomerName, CODate, ' \
                              'Amount, Status) VALUES( "{}", "{}",  CURRENT_DATE, {}, "Pending")'\
                        .format(self.co_number, self.cname, total )
                    cur.execute(command)

                except mysql.connector.IntegrityError as e:
                    error = "Record already exists!"
                    break

                except Exception as err:
                    error = err
                    print(err)
                    break

                try:
                    for item, qty, price in zip(self.items, self.quantity, self.prices):
                        command = 'INSERT INTO co_items VALUES( "{}",{},{}, {}, {})'\
                            .format(self.co_number, item, qty, qty, price)
                        cur.execute(command)
                except Exception as err:
                    error = err
                    break
                    print(err)

            break

        if error:
            link.rollback()
        else:
            link.commit()
        cur.close()
        return error

    @staticmethod
    def create_invoice(*args,**kwargs):
        link = mysql.connector.connect(**config)
        cur = link.cursor()

        co_number = kwargs['co_number']
        items = kwargs['items']
        remaining = kwargs['remaining']
        available = kwargs['available']
        quantity = kwargs['quantity']


        error = 0
        i = 0
        print(quantity)
        while i < len(quantity):
            try:
                items[i] = int(items[i])
                remaining[i] = int(remaining[i])
                available[i] = int(available[i])
                quantity[i] = int(quantity[i])

                if quantity[i] == 0:
                    del items[i]
                    del remaining[i]
                    del available[i]
                    del quantity[i]
                    i = i - 1
                i = i + 1
            except Exception as e:
                print(e)
                error = 'Invalid entry at row ' + str(i + 1)
                return error

        i = 1
        for rem, av, qty in zip(remaining,available,quantity):
            if (qty > rem):
                error = 'Quantity exceeds remaining at row ' + str(i)
                return error
            if (qty > av):
                error = 'Insufficient stock at row ' + str(i)
                return error
            i = i+1

        while 1:

            try:
                #Create invoice
                name = CustomerOrderBackend.get_name(ID=co_number)
                prices = []
                for item in items:
                    prices.append(CustomerOrderBackend.get_prices(Item=item, ID=co_number))

                invoice = InvoiceBackend(co_name=name, co_number=co_number, items=items,
                                         quantities=quantity, prices=prices)
                error = invoice.insert(cur=cur)


                # Update Stock
                it_qty = [(item, qty) for item,qty in zip(items, quantity)]
                StockBackend.update(cur=cur,items=it_qty, type='customer_order')

                # Update remaining qty and status
                new_remaining = [rem-qty for qty, rem in zip(quantity, remaining)]
                status = 'Delivered'
                if (any(new_remaining)):
                    status = 'Pending'
                it_qty = [(item, qty) for item, qty in zip(items, new_remaining)]
                CustomerOrderBackend.update(cur=cur,co_number=co_number, items=it_qty, status=status)
            except:

                pass

            break

        if error:
            link.rollback()

        else:
            link.commit()

        return error

    @staticmethod
    def update(*args, **kwargs):

        cur = kwargs['cur']

        co_number = kwargs['co_number']
        items = kwargs['items']
        status = kwargs['status']

        command = 'Update CustomerOrder set Status = "{}" WHERE CustomerOrderNumber = "{}" '.format(status, co_number)
        cur.execute(command)

        for item, qty in items:
            command = 'Update co_items set Remaining_Qty = {} WHERE Item_Code = {} ' \
                      'and CustomerOrderNumber = "{}" '.format(qty, item, co_number)
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
                condition = '"' + condition + '%"'
                operator = 'like'
            except:
                condition = 'CustomerOrderNumber'
                operator = '='

            command = 'SELECT CustomerOrderNumber,CustomerName, Amount, CODate,Status FROM CustomerOrder WHERE CustomerOrderNumber {} {} '.format(operator,condition)

            try:
                command += 'and CustomerName like "{}%" '.format(conditions['CustomerName'])
            except:
                pass

            try:
                command += 'and Status = "{}" '.format(conditions['Status'])
            except:
                pass


            try:
                date_after = conditions['CODateAfter']
                try:
                    date_after = datetime.datetime(year=int(date_after[0]), month=int(date_after[1]), day=int(date_after[2]))
                except:
                    error = 'Invalid date (after)'
                    break
                else:
                    CODateAfter = str(date_after.year) + '-' + str(date_after.month) + '-' + str(date_after.day)
            except:
                pass
            try:
                command += " and CODate >= '{}' ".format(CODateAfter)
            except:
                pass

            try:
                date_before = conditions['CODateBefore']

                try:
                    date_before = datetime.datetime(year=int(date_before[0]), month=int(date_before[1]), day=int(date_before[2]))
                except:
                    error = 'Invalid date (before)'
                    break
                else:
                    CODateBefore = str(date_before.year) + '-' + str(date_before.month) + '-' + str(date_before.day)
            except:
                pass
            try:
                command += " and CODate <= '{}' ".format(CODateBefore)
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
    def get_prices(*args, **kwargs):
        link1 = mysql.connector.connect(**config)
        cur1 = link1.cursor()
        command = 'SELECT Price FROM co_items WHERE CustomerOrderNumber = "{}" and  Item_Code = {}' \
                  ''.format(kwargs['ID'],kwargs['Item'])
        cur1.execute(command)
        data = cur1.fetchall()[0][0]
        cur1.close()
        return data

    @staticmethod
    def get_name(*args, **kwargs):
        link1 = mysql.connector.connect(**config)
        cur1 = link1.cursor()
        command = 'SELECT CustomerName FROM CustomerOrder WHERE CustomerOrderNumber = "{}"'\
            .format(kwargs['ID'])
        cur1.execute(command)
        data = cur1.fetchone()[0]
        cur1.close()
        return data

    @staticmethod
    def get_status(*args, **kwargs):
        link1 = mysql.connector.connect(**config)
        cur1 = link1.cursor()
        command = 'SELECT Status FROM CustomerOrder WHERE CustomerOrderNumber = "{}"'\
            .format(kwargs['ID'])
        cur1.execute(command)
        data = cur1.fetchone()[0]
        cur1.close()
        return data

    @staticmethod
    def select_items(*args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()
        command = 'SELECT Item_Code, Quantity,Remaining_Qty,  Price FROM co_items WHERE CustomerOrderNumber = "{}" '.format(kwargs['ID'])
        cur.execute(command)
        data = cur.fetchall()
        cur.close()

        try:
            stock_needed =  kwargs['StockAvailable']
        except:
            stock_needed = 0

        error = 0
        if stock_needed:
            availability = []
            for item in data:
                available, error = StockBackend.get_quantity(ID=item[0])
                availability.append(available)
                if error:
                    return (0,0, error)
            return data, availability, error
        else:
            return data


    # @staticmethod
    # def delete(*args, **kwargs):
    #     try:
    #         value = '"' + kwargs['value'] + '"'
    #     except:
    #         print('error')
    #         return
    #     link = mysql.connector.connect(**config)
    #     cur = link.cursor()
    #     command = 'DELETE FROM co_items WHERE CustomerOrderNumber = '
    #     command = command + value
    #     cur.execute(command)
    #
    #     command = 'DELETE FROM CustomerOrder WHERE CustomerOrderNumber = '
    #     command = command + value
    #     cur.execute(command)
    #
    #     link.commit()
    #     cur.close()
