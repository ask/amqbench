#!/usr/bin/env python
# shortcut for librabbitmq both publish and consume
from amqbench import kamqplib

kamqplib().publish()
kamqplib().consume()
