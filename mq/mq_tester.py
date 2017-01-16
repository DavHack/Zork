import pika, sys, time

def mycallback(ch, method, properties, body):
	print('Message received on channel {}, on method {}, with those properties: {} and with the body: {}'.format(ch, method, properties, body))
	time.sleep(3)
	ch.basic_ack(delivery_tag = method.delivery_tag)
	print('Done')


def publish(connection, channel, message):
	channel.queue_declare(queue='tasks', durable=True)
	channel.basic_publish(exchange='',
                      routing_key='tasks',
                      body=message,
					  properties=pika.BasicProperties(delivery_mode=2))
	print(" [x] Sent {}'".format(message))
	connection.close()

def receiver(connection, channel):
	channel.queue_declare(queue='history', durable=True)
	channel.basic_consume(mycallback, queue='history')
	channel.start_consuming()
	
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.basic_qos(prefetch_count=1)
# TODO switch to relative script name
if len(sys.argv) < 2:
    print('Usage: mq_tester.py <receive/send> [what to send]')
    sys.exit(1)
elif sys.argv[1] == 'send':
	publish(connection, channel, sys.argv[2])
elif sys.argv[1] == 'receive':
	receiver(connection, channel)
else:
	print('Unknown command')
