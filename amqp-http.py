# -*- coding: utf8 -*-
# Hand-made AMQP to HTTP river, like rabbitmq-http

import pika
from flask import Flask, Response

QUEUE = 'queue_name'
ROUTING_KEY = 'routing.key.#'
EXCHANGE = 'feeds'
AMQP = 'amqp://user:pass@host:5672/%2Fvhost'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_queue():
    return Response(link_amqp(), mimetype='application/json')

def link_amqp():
    parameters = pika.URLParameters(AMQP)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, passive=False, durable=False, exclusive=False, auto_delete=False, arguments={"x-message-ttl": 86400*1000})
    channel.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)
    i = 0
    while True:
        method_frame, header_frame, body = channel.basic_get(QUEUE)
        if method_frame:
            channel.basic_ack(method_frame.delivery_tag)
            i += 1
            yield body + '\n'
        else:
            break
    print 'Returned %d records.' % i
    connection.close()

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False     # JSON in UTF-8
    app.config['DEBUG'] = False
    app.run(host = '0.0.0.0', port = 8080, threaded=True)
