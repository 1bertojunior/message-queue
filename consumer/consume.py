import pika
import socket
from retrying import retry
import time
import sys
import requests
import mysql.connector
import threading
import json


def check_rabbitmq_server_active(server_ip):
    server_port = 5672  # Porta padrão do RabbitMQ
    timeout = 3  # Tempo limite de conexão em segundos

    # Tentar estabelecer uma conexão TCP/IP com o servidor
    try:
        sock = socket.create_connection((server_ip, server_port), timeout=timeout)
        sock.close()
        return True  # O servidor RabbitMQ está ativo e acessível
    except (socket.timeout, ConnectionRefusedError):
        return False  # O servidor RabbitMQ não está ativo ou não pode ser alcançado

def wait_for_rabbitmq():
    while not check_rabbitmq_server_active(rabbitmq_ip):
        print("Servidor RabbitMQ não está ativo. Tentando novamente em 5 segundos...")
        time.sleep(5)

    print("Servidor RabbitMQ conectado com sucesso!")

def convert_to_major_currencies(amount):
    try:
        value = float(amount)
    except ValueError:
        print("Invalid value. Please enter a valid number.")
        return None

    
    url = f"https://api.exchangerate-api.com/v4/latest/BRL"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rates = data["rates"]

        usd = round(value * rates["USD"], 2)
        eur = round(value * rates["EUR"], 2)
        jpy = round(value * rates["JPY"], 2)
        gbp = round(value * rates["GBP"], 2)
        cad = round(value * rates["CAD"], 2)

        return {
            "USD": usd,
            "EUR": eur,
            "JPY": jpy,
            "GBP": gbp,
            "CAD": cad
        }
    else:
        print("Failed to retrieve exchange rates.")
        return None


def check_mysql_server_active(host, port, user, password):
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        conn.close()
        return True  # O servidor MySQL está ativo e acessível
    except mysql.connector.Error:
        return False  # O servidor MySQL não está ativo ou não pode ser alcançado

def wait_for_mysql(host, port, user, password):
    while not check_mysql_server_active(host, port, user, password):
        sys.stdout.flush()
        print("Servidor MySQL não está ativo. Tentando novamente em 5 segundos...")
        time.sleep(5)
    sys.stdout.flush()
    print("Servidor MySQL conectado com sucesso!")

def store_in_database(host, port, user, password, result):
    try:
        # Estabelece conexão com o banco de dados
        connection = mysql.connector.connect(
            host=host,
            user="root",
            password="myroot",
            database="mydb"
        )

        if connection.is_connected():
            print("Conexão bem-sucedida!")

            cursor = connection.cursor()

            # Insere os valores no banco de dados
            query = "INSERT INTO coin (BRL, USD, EUR, JPY, GBP, CAD, ip_address_sender) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (result['BRL'], result['USD'], result['EUR'], result['JPY'], result['GBP'], result['CAD'], result['ip_address_sender'])
            cursor.execute(query, values)

            # Commit das alterações e encerramento da conexão
            connection.commit()
            cursor.close()
            connection.close()
            print("Valores inseridos no banco de dados.")

        else:
            print("Falha na conexão.")

    except mysql.connector.Error as error:
        print("Erro ao conectar ao servidor MySQL:", error)

def callback(ch, method, properties, body):
    sys.stdout.flush()
    print("\n[x] Received %r" % body)

    decoded_body = body.decode('utf-8')
    data = json.loads(decoded_body)  # Decodifica o JSON para obter os dados

    message = data.get('message')
    ip_address_sender = data.get('ip_address_sender')

    print(f"[*] Mensagem recebida: {message}")
    print(f"[*] IP do remetente: {ip_address_sender}")
    result = convert_to_major_currencies(message)
    #result = convert_to_major_currencies(decoded_body)

    #print(result)
    result["BRL"] = float(message)
    result["ip_address_sender"] = ip_address_sender
    print(result)

    ## salvar dados no db
    host_db = socket.gethostbyname( 'db-mysql' )  # Endereço IP do servidor MySQL
    port_db = 3306  # Porta padrão do MySQL
    user_db = 'root'  # Usuário do MySQL
    password_db = 'myroot'  # Senha do MySQL

    sys.stdout.flush()
    print("Start DB\nTentando conexão com o MySQL")
    wait_for_mysql(host_db, port_db, user_db, password_db)
    print("\n[*][*][*] DB [*][*][*]")
    store_in_database(host_db, port_db, user_db, password_db, result)
    sys.stdout.flush()


if __name__ == "__main__":

    rabbitmq_ip = socket.gethostbyname( 'rabbitmq' )
    print("Iniciando...")
    wait_for_rabbitmq()

    try:
        print("[*][*][*] CONSUMER [*][*][*]")
        print("IP: ", socket.gethostbyname(socket.gethostname()))

        # Criar a conexão
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq_ip,
                heartbeat=300
            )
        )

        channel = connection.channel()

        channel.queue_declare(queue='hello') # Fila

        channel.basic_consume('hello', callback, auto_ack=True) # Executar o callback todas as vezes que for enviado algo do produtor

        print('\n[*] Waiting for messages. To exit press CTRL+C')

        channel.start_consuming() # Consumir o que vem do produtor

    except pika.exceptions.AMQPConnectionError as e:
        print("\n\n\n[!][!][!] Erro de conexão com o RabbitMQ:", str(e))
