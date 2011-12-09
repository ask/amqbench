#!/usr/bin/env python
# shortcut for librabbitmq both publish and consume
from amqbench import librabbitmq

librabbitmq().publish()
librabbitmq().consume()
