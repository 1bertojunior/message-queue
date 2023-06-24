import mysql.connector
import socket


db_mysql_ip = socket.gethostbyname( 'db-mysql' )
host = db_mysql_ip  # Endereço IP do servidor MySQL
# Estabelece conexão com o banco de dados
connection = mysql.connector.connect(
    host=host,
    user="root",
    password="myroot",
    database="mydb"
)

if connection.is_connected():
    print("Conexão bem-sucedida!")

    # Executa consultas, operações no banco de dados, etc.

    # Encerra a conexão
    connection.close()
    print("Conexão encerrada.")
else:
    print("Falha na conexão.")
