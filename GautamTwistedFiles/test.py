import sqlite3

dbName = "testUserDB"
tableName = "users"

connection = sqlite3.connect(dbName)
cursor = connection.cursor()
userName = "raj"
execute = "DELETE FROM %s where userName = \'%s\'" % (tableName, userName)
cursor.execute(execute)
connection.commit()
var = "does2"
cursor.execute("select * from " + tableName + " where userName is \'" + var + "\';")
rows = cursor.fetchall()
for row in rows:
	print row
#execute = "INSERT INTO %s (userName, password) VALUES(\'%s\', \'%s\');" % (tableName, "does2", "work")
#print execute
#cursor.execute(execute)
#cursor.execute("insert into users (userName, password) values(?, ?)", ("does2", "work"))
#connection.commit()