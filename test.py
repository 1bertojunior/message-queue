import mysql.connector

# Estabelece conexão com o banco de dados
connection = mysql.connector.connect(
    host="127.20.0.5",
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
