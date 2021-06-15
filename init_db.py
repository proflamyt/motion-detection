import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO sms (name, phone) VALUES (?, ?)",
            ('ola', +2348025729256 )
            )

cur.execute("INSERT INTO email (name, email) VALUES (?, ?)",
            ('ola', 'proflamyt@gmail.com')
            )

connection.commit()
connection.close()