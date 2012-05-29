#!/usr/bin/env python
# shortcut for librabbitmq both publish and consume
from amqbench import librabbitmq

librabbitmq().publish(100000)
librabbitmq().consume(100000)
