#!/usr/bin/env python
from amqbench import klibrabbitmq

klibrabbitmq().publish()
klibrabbitmq().consume()
