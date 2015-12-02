# -*- coding: utf8 -*-
# Hand-made AMQP to HTTP river, like rabbitmq-http

import pika
import Queue
import thread
from flask import Flask, Response

q = Queue.Queue()

QUEUE = 'queue_name'
ROUTING_KEY = 'routing.key.#'
EXCHANGE = 'feeds'
AMQP = 'amqp://user:pass@host:5672/%2Fvhost'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_queue():
    size = q.qsize()
    print 'Getting approximately %d records.' % size
    return Response(producer(), mimetype='application/json')


def producer():
    while not q.empty():
        yield q.get() + '\n'


def link_amqp(*args):
    parameters = pika.URLParameters(AMQP)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, passive=False, durable=False, exclusive=False, auto_delete=False, arguments={"x-message-ttl": 86400*1000})
    channel.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)
    channel.basic_consume(callback, queue = QUEUE)
    channel.start_consuming()


def callback(ch, method, properties, body):
    if not q.full():
        q.put(body)
        ch.basic_ack(delivery_tag = method.delivery_tag)
    else:
        print 'Queue is full!  Re-queue the message.'
        ch.basic_nack()


if __name__ == '__main__':
    thread.start_new_thread(link_amqp, ())
    app.config['JSON_AS_ASCII'] = False     # JSON in UTF-8
    app.config['DEBUG'] = False
    app.run(host = '0.0.0.0', port = 8080, threaded=True)
