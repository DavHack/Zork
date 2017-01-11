import pika, time, json
from flask import Flask, request
app = Flask(__name__)

@app.route('/connect/<slave_name>', methods=['POST'])
def slave_connection(slave_name):
    print('Slave {} connected.'.format(slave_name))
    slave_version = request.form['version']
    channel.basic_publish(exchange='history', routing_key='connections', 
                          body=json.dumps({'name': slave_name, 'version': slave_version,
                                           'ip_address': request.remote_addr,
                                           'user-agent': request.headers.get('User-Agent'),
                                           'timestamp': int(time.time())
                                           }))
    return json.dumps({'status': 'success', 'message': 'Connection received successfully'})
    

def rabbitmq_init():
    # Initalizing connection to the RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    global channel
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    # Declaring all exchanges
    channel.exchange_declare(exchange='outcome', type='direct')
    channel.exchange_declare(exchange='log', type='fanout')
    channel.exchange_declare(exchange='history', type='direct')
    # Declaring all queues
    channel.queue_declare('outcome', durable=True)
    channel.queue_declare('log', durable=True)
    channel.queue_declare('history', durable=True)
    # Binds all exchanges to queues
    channel.queue_bind(exchange='outcome', queue='outcome')
    channel.queue_bind(exchange='history', queue='history', routing_key='connections')
    channel.queue_bind(exchange='history', queue='history', routing_key='actions')
    channel.queue_bind(exchange='log', queue='log', routing_key='info')
    channel.queue_bind(exchange='log', queue='log', routing_key='fatal')


if __name__ == '__main__':
    rabbitmq_init()
    app.run('0.0.0.0')
