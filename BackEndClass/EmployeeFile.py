import mysql.connector

config = {
    'user': 'root',
    'password': 'root',
    'database': 'testdb',
    'raise_on_warnings': True,
}

def sql_exec(retrieve_command):

    def sql_command(*args, **kwargs):

        link = mysql.connector.connect(**config)
        cur = link.cursor()
        command = retrieve_command(*args, **kwargs)
        cur.execute(command)

        if 'DELETE' in command or 'UPDATE' in command:
            link.commit()
            cur.close()

        elif 'INSERT'in command:
            link.commit()
            cur.execute('SELECT LAST_INSERT_ID();')
            data = cur.fetchall()
            cur.close()
            return data

        elif 'SELECT' in command:
            data = cur.fetchall()
            cur.close()
            return data


    return sql_command

class Employee:
    def __init__(self, id, name, loc):
        self.id = id
        self.name = name
        self.loc = loc

    @staticmethod
    @sql_exec
    def get_key(*args, **kwargs):
        command = 'SELECT LAST_INSERT_ID();'
        return command

    @sql_exec
    def insert(self, *args, **kwargs):
        command = 'INSERT INTO DEPT(deptno, dname, loc) VALUES({}, "{}", "{}");'.format(self.id, self.name, self.loc)
        print(command)
        return command

    @sql_exec
    def update(self, *args, **kwargs):
        command = 'UPDATE DEPT SET dname="{}", loc="{}" where deptno={}'.format(self.name, self.loc, self.id)
        return command

    @staticmethod
    @sql_exec
    def select(*args, **kwargs):
        command = 'SELECT deptno, dname, loc FROM DEPT '
        try:
            condition = kwargs['condition']
        except:
            condition = ''
        command = command + condition
        return command

    @staticmethod
    @sql_exec
    def delete(*args, **kwargs):
        command = 'DELETE FROM DEPT WHERE deptno = '
        try:
            value = kwargs['value']
        except:
            print('error')
            return
        command = command + value
        return command
