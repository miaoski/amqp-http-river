amqp-http-river
===============
I need to consume AMQP and put it in a queue for StreamSets to poll via HTTP.
A colleague recommended [rabbitmq-http] (https://github.com/smallfish/rabbitmq-http), but it doesn't close old channel when an HTTP connection is closed.

BTW, this amqp-http-river is in POLL model, not STREAMING model.  Remember to poll it often, otherwise the Python script will run out of memory.



LICENSE
=======
MIT License.  See LICENSE file.
