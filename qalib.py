#!/usr/bin/env python
# shortcut for librabbitmq both publish and consume
from amqbench import amqplib

amqplib().publish()
amqplib().consume()
