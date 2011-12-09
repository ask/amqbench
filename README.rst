==========
 amqbench
==========

This is the code I use to benchmark different Python AMQP clients.

Current winner is `librabbitmq`_:

    * transient (durable=False, delivery-mode=1, no_ack=True)
        * publishing 52000 messages: 1.6s
        * consuming 52000 messages: 1.06s

    * persistent (durable=True, delivery-mode=1, no_ack=True)
        * publishing 52000 messages: 1.80s
        * consuming 52000 messages: 2.08s

which after comes `librabbitmq`_ under Kombu:

    * transient (durable=False, delivery-mode=1, no_ack=True)
        * publishing 52000 messages: 1.94s
        * consuming 52000 messages: 1.55s

    * persistent (durable=True, delivery-mode=1, no_ack=True)
        * publishing 52000 messages: 2.16s
        * consuming 52000 messages: 2.22s

numbers for amqplib:

    * transient (durable=false, delivery-mode=1, no_ack=true)
        * publishing 52000 messages: 4.4s
        * consuming 52000 messages: 5.2s

    * persistent (durable=true, delivery-mode=1, no_ack=true)
        * publishing 52000 messages: 4.7s
        * consuming 52000 messages: 5.33s

numbers for amqplib under kombu:

    * transient (durable=false, delivery-mode=1, no_ack=true)
        * publishing 52000 messages: 5.09
        * consuming 52000 messages: 7.19s

    * persistent (durable=true, delivery-mode=1, no_ack=true)
        * publishing 52000 messages: 5.19s
        * consuming 52000 messages: 7.33s

.. _`librabbitmq`: http://github.com/celery/pylibrabbitmq/
