import pika
import socket
import time
from retrying import retry
from fastapi import FastAPI
import uvicorn
import sys
import mysql.connector
from fastapi import Request
import json

def check_rabbitmq_server_active(server_ip):
    server_port = 5672  # Porta padrão do RabbitMQ
    timeout = 3  # Tempo limite de conexão em segundos

    # Tentar estabelecer uma conexão TCP/IP com o servidor
    try:
        sock = socket.create_connection(
            (
                server_ip,
                server_port),
                timeout=timeout
            )
        sock.close()
        return True  # O servidor RabbitMQ está ativo e acessível
    except (socket.timeout, ConnectionRefusedError):
        return False  # O servidor RabbitMQ não está ativo ou não pode ser alcançado

def send_message(message: str):
    channel.basic_publish(
        exchange='',
        routing_key='hello',
        body=message
    )
    print(f"[>] SENT '{message}'")

@retry(stop_max_attempt_number=10, wait_fixed=5000)  # Tentar 10 vezes com um intervalo de 5 segundos
def wait_for_rabbitmq():
    if not check_rabbitmq_server_active(rabbitmq_ip):
        raise Exception("O servidor RabbitMQ não está ativo ou não pode ser alcançado")

def send_message(message: str, ip_address_sender: str):
    data = {
        'message': message,
        'ip_address_sender': ip_address_sender
    }
    body = json.dumps(data)  # Serializa os dados em formato JSON

    channel.basic_publish(
        exchange='',
        routing_key='hello',
        body=body.encode('utf-8')  # Codifica a string como bytes
    )

    print(f" [x] Sent '{body}'")

def get_mysql_records():
    try:
        connection = mysql.connector.connect(
            host='db-mysql',
            port=3306,
            user='root',
            password='myroot',
            database='mydb'
        )
        cursor = connection.cursor(dictionary=True)  # Retorna os resultados como dicionários
        cursor.execute('SELECT * FROM coin')
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        return records
    except mysql.connector.Error as error:
        print("Erro ao conectar ao MySQL:", error)
        return []

if __name__ == "__main__":
    print("Iniciando...")
    rabbitmq_ip = socket.gethostbyname( 'rabbitmq' )
    ip_address = socket.gethostbyname(socket.gethostname())
    wait_for_rabbitmq()

    try:
        print("[*][*][*] PRODUCER [*][*][*]")
        print(f"IP = {ip_address}\n\n")
        # Cria uma conexão com o RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq_ip,
                heartbeat=300
            )
        )
        channel = connection.channel()
        # Declara a fila
        channel.queue_declare(queue='hello')

    except pika.exceptions.AMQPConnectionError as e:
        print("\n\n\n[!][!][!] Erro de conexão com o RabbitMQ:", str(e))

    print("Iniciando FAST API")
    app = FastAPI()

    @app.get("/")
    def send_message_once(BRL: str, request: Request):
        #send_message(BRL) # send
        ip_address_sender = request.client.host

        send_message(BRL, ip_address_sender) # send

        sys.stdout.flush()
        return {
            "message": "Mensagem enviada para a fila",
            "BRL" : BRL
        }

    @app.get("/ip_address")
    def get_producer_ip():
        ip_address = socket.gethostbyname(socket.gethostname())
        return {"ip_address": ip_address}

    @app.get("/rabbitmq_status")
    def get_rabbitmq_status():
        if check_rabbitmq_server_active(rabbitmq_ip):
            return {"status": "O servidor RabbitMQ está ativo e acessível"}
        else:
            return {"status": "O servidor RabbitMQ não está ativo ou não pode ser alcançado"}

    @app.get("/infos")
    def get_rabbitmq_status():
        return {
            'address_ip_rabbitmq' : rabbitmq_ip,
            'address_ip_rabbitmq2' : rabbitmq_ip
        }
    
    @app.get("/coins")
    def get_coins():
        records = get_mysql_records()
        return {"coins": records}

    sys.stdout.flush()
    
    # iniciando o servidor
    uvicorn.run(app, host="0.0.0.0", port=80)


    #uvicorn.run(produce:app, host="0.0.0.0", port=80)
    #uvicorn produce:app --host 0.0.0.0 --port 80
