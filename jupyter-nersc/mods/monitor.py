
# Based on the asynchronous publisher example in the Pika documentation.

import argparse
import logging
import json
import os

import pika
import requests

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def main():
    args = parse_arguments()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    credentials = pika.PlainCredentials(args.username, args.password)

    publisher = Publisher(args.rabbitmq_host, credentials,
            args.publish_interval, args.routing_key, args.exchange,
            args.exchange_type, args.queue, args.api_url, args.api_token,
            args.subcategory)

    try:
        publisher.run()
    except KeyboardInterrupt:
        publisher.stop()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d",
            action="store_true")
    parser.add_argument("--username", "-u",
            default=os.environ["MODS_USERNAME"])
    parser.add_argument("--password", "-p",
            default=os.environ["MODS_PASSWORD"])
    parser.add_argument("--rabbitmq-host", "-r",
            default=os.environ["MODS_RABBITMQ_HOST"])
    parser.add_argument("--publish-interval", "-i",
            default=300, type=int)
    parser.add_argument("--routing-key", "-k",
            default="ou.das")
    parser.add_argument("--exchange", "-e",
            default="ha-metric")
    parser.add_argument("--exchange-type", "-t",
            default="topic")
    parser.add_argument("--queue", "-q",
            default="text")
    parser.add_argument("--api-url", "-a",
            default="http://web:8081/hub/api")
    parser.add_argument("--api-token", "-o",
            default=os.environ["MODS_JUPYTERHUB_API_TOKEN"])
    parser.add_argument("--subcategory", "-s",
            default="jupyterhub_v1")
    return parser.parse_args()


class Publisher(object):

    def __init__(self, host, credentials, publish_interval, routing_key,
            exchange, exchange_type, queue, api_url, api_token, subcategory):

        self.connection = None
        self.channel = None
        self.deliveries = []
        self.acked = 0
        self.nacked = 0
        self.message_number = 0
        self.stopping = False
        self.host = host
        self.credentials = credentials
        self.publish_interval = publish_interval
        self.routing_key = routing_key
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue
        self.closing = False
        self.api_url = api_url
        self.api_token = api_token
        self.subcategory = subcategory

    def connect(self):
        LOGGER.info('Connecting to %s', self.host)
        parameters = pika.connection.ConnectionParameters(self.host,
            credentials = self.credentials)

        # For reconnect to work, must ensure `stop_ioloop_on_close=False`.
        return pika.SelectConnection(parameters,
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        LOGGER.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        LOGGER.info('Adding connection close callback')
        self.connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self.channel = None
        if self.closing:
            self.connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self.connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        self.deliveries = []
        self.acked = 0
        self.nacked = 0
        self.message_number = 0

        # This is the old connection IOLoop instance, stop its ioloop
        self.connection.ioloop.stop()

        # Create a new connection
        self.connection = self.connect()

        # There is now a new connection, needs a new ioloop to run
        self.connection.ioloop.start()

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.info('Channel opened')
        self.channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange)

    def add_on_channel_close_callback(self):
        LOGGER.info('Adding channel close callback')
        self.channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        LOGGER.warning('Channel was closed: (%s) %s', reply_code, reply_text)
        if not self.closing:
            self.connection.close()

    def setup_exchange(self, exchange_name):
        LOGGER.info('Declaring exchange %s', exchange_name)
        self.channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.exchange_type,
                                       durable=True)

    def on_exchange_declareok(self, unused_frame):
        LOGGER.info('Exchange declared')
        self.setup_queue(self.queue)

    def setup_queue(self, queue_name):
        LOGGER.info('Declaring queue %s', queue_name)
        self.channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        LOGGER.info('Binding %s to %s with %s',
                    self.exchange, self.queue, self.routing_key)
        self.channel.queue_bind(self.on_bindok, self.queue,
                                 self.exchange, self.routing_key)

    def on_bindok(self, unused_frame):
        LOGGER.info('Queue bound')
        self.start_publishing()

    def start_publishing(self):
        LOGGER.info('Issuing consumer related RPC commands')
        self.enable_delivery_confirmations()
        self.schedule_next_message()

    def enable_delivery_confirmations(self):
        LOGGER.info('Issuing Confirm.Select RPC command')
        self.channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        LOGGER.info('Received %s for delivery tag: %i',
                    confirmation_type,
                    method_frame.method.delivery_tag)
        if confirmation_type == 'ack':
            self.acked += 1
        elif confirmation_type == 'nack':
            self.nacked += 1
        self.deliveries.remove(method_frame.method.delivery_tag)
        LOGGER.info('Published %i messages, %i have yet to be confirmed, '
                    '%i were acked and %i were nacked',
                    self.message_number, len(self.deliveries),
                    self.acked, self.nacked)

    def schedule_next_message(self):
        if self.stopping:
            return
        LOGGER.info('Scheduling next message for %0.1f seconds',
                    self.publish_interval)
        self.connection.add_timeout(self.publish_interval,
                                     self.publish_message)

    def publish_message(self):
        if self.stopping:
            return

        headers = dict(Authorization="token " + self.api_token)
        r = requests.get(self.api_url + "/users", headers=headers)
        r.raise_for_status()
        users = r.json()

        servers = list()
        for user in users:
            for name, info in user["servers"].items():
                 servers.append(info["url"])

        message = dict()
        message["category"] = "MODS"
        message["subcategory"] = self.subcategory
        message["servers"] = sorted(servers)

        self.channel.basic_publish(self.exchange, self.routing_key,
                                    json.dumps(message))

        self.message_number += 1
        self.deliveries.append(self.message_number)
        LOGGER.info('Published message # %i', self.message_number)
        self.schedule_next_message()

    def close_channel(self):
        LOGGER.info('Closing the channel')
        if self.channel:
            self.channel.close()

    def run(self):
        self.connection = self.connect()
        self.connection.ioloop.start()

    def stop(self):
        LOGGER.info('Stopping')
        self.stopping = True
        self.close_channel()
        self.close_connection()
        self.connection.ioloop.start()
        LOGGER.info('Stopped')

    def close_connection(self):
        LOGGER.info('Closing connection')
        self.closing = True
        self.connection.close()


if __name__ == '__main__':
    main()
