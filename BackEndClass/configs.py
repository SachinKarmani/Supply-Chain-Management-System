config = {
    'user': 'root',
    'password': 'root',
    'database': 'supplydistribution',
    'raise_on_warnings': True,
}
#
# def sql_edit(retrieve_command):
#
#     def sql_command(*args, **kwargs):
#
#         link = mysql.connector.connect(**config)
#         cur = link.cursor()
#
#         command = retrieve_command(*args, **kwargs)
#
#         cur.execute(command)
#         link.commit()
#         cur.close()
#
#     return sql_command
#
# def sql_select(retrieve_command):
#
#     def sql_command(*args, **kwargs):
#
#         link = mysql.connector.connect(**config)
#         cur = link.cursor()
#
#         command = retrieve_command(*args, **kwargs)
#         link.roll
#         cur.execute(command)
#         data = cur.fetchall()
#         cur.close()
#         return data
#
#     return sql_command
