import pika
import socket
import time

rabbitmq_ip = '172.20.0.2'

# Criar uma conexão
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_ip))
channel = connection.channel()

# A fila
channel.queue_declare(queue='hello')

i=1
while True:
    # Enviar Mensagem
    channel.basic_publish(
        exchange='',
        routing_key='hello',
        body= f'Hello World {i}!'
    )
    
    print(" [x] Sent 'Hello World!'")
    i+=1
    #time.sleep(1)
# Fechar a conexão
connection.close()