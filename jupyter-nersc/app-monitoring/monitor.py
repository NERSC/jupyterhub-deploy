# https://raw.githubusercontent.com/pika/pika/master/examples/asynchronous_publisher_example.py

# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import argparse
import functools
import json
import logging
import os

import pika
import requests

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class ExamplePublisher(object):
    """This is an example publisher that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    It uses delivery confirmations and illustrates one way to keep track of
    messages that have been sent and if they've been confirmed by RabbitMQ.

    """

    def __init__(self, amqp_url, publish_interval, routing_key, exchange, exchange_type):
        """Setup the example publisher object, passing in the URL we will use
        to connect to RabbitMQ.

        :param str amqp_url: The URL for connecting to RabbitMQ

        """
        self._connection = None
        self._channel = None

        self._deliveries = None
        self._acked = None
        self._nacked = None
        self._message_number = None

        self._stopping = False
        self._url = amqp_url

        self._publish_interval = publish_interval
        self._routing_key = routing_key
        self._exchange = exchange
        self._exchange_type = exchange_type

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        LOGGER.info('Connecting to %s', self._url)
        return pika.SelectConnection(
            pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param pika.SelectConnection _unused_connection: The connection

        """
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        LOGGER.error('Connection open failed, reopening in 5 seconds: %s', err)
        self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        self._channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def open_channel(self):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.

        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._exchange)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed

        """
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        LOGGER.info('Declaring exchange %s', exchange_name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self._exchange_type,
            callback=cb,
            durable=True)

    def on_exchange_declareok(self, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)

        """
        LOGGER.info('Exchange declared: %s', userdata)
        self.start_publishing()

    def start_publishing(self):
        """This method will enable delivery confirmations and schedule the
        first message to be sent to RabbitMQ

        """
        LOGGER.info('Issuing consumer related RPC commands')
        self.enable_delivery_confirmations()
        self.schedule_next_message()

    def enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.

        """
        LOGGER.info('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        LOGGER.info('Received %s for delivery tag: %i', confirmation_type,
                    method_frame.method.delivery_tag)
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        LOGGER.info(
            'Published %i messages, %i have yet to be confirmed, '
            '%i were acked and %i were nacked', self._message_number,
            len(self._deliveries), self._acked, self._nacked)

    def schedule_next_message(self):
        """If we are not closing our connection to RabbitMQ, schedule another
        message to be delivered in _publish_interval seconds.

        """
        LOGGER.info('Scheduling next message for %0.1f seconds',
                    self._publish_interval)
        self._connection.ioloop.call_later(self._publish_interval,
                                           self.publish_message)

    def publish_message(self):
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Once the message has been sent, schedule another message to be sent.
        The main reason I put scheduling in was just so you can get a good idea
        of how the process is flowing by slowing down and speeding up the
        delivery intervals by changing the _publish_interval constant in the
        class.

        """
        if self._channel is None or not self._channel.is_open:
            return
        message = self.create_message()
        self._channel.basic_publish(self._exchange, self._routing_key,
                                    json.dumps(message))
        self._message_number += 1
        self._deliveries.append(self._message_number)
        LOGGER.info('Published message # %i', self._message_number)
        self.schedule_next_message()

    def create_message(self):
        raise NotImplementedError

    def run(self):
        """Run the example code by connecting and then starting the IOLoop.

        """
        while not self._stopping:
            self._connection = None
            self._deliveries = []
            self._acked = 0
            self._nacked = 0
            self._message_number = 0

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if (self._connection is not None and
                        not self._connection.is_closed):
                    # Finish closing
                    self._connection.ioloop.start()

        LOGGER.info('Stopped')

    def stop(self):
        """Stop the example by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. The IOLoop is started because this method is
        invoked by the Try/Catch below when KeyboardInterrupt is caught.
        Starting the IOLoop again will allow the publisher to cleanly
        disconnect from RabbitMQ.

        """
        LOGGER.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.

        """
        if self._channel is not None:
            LOGGER.info('Closing the channel')
            self._channel.close()

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self._connection is not None:
            LOGGER.info('Closing connection')
            self._connection.close()


class JupyterHubPublisher(ExamplePublisher):

    def __init__(self, api_token, api_url, subcategory, *args, **kwargs):
        self._api_token = api_token
        self._api_url = api_url
        self._subcategory = subcategory
        super().__init__(*args, **kwargs)

    def create_message(self):
        import pprint

        hub_users = self.hub_users()
        iris_staff = self.iris_staff()

        users = list()
        user_servers = list()

        for user in hub_users:
            if not user["servers"]:
                continue
            servers = user["servers"]
            if "" in servers:
                servers["default"] = servers.pop("")
            name = user["name"]
            if name in iris_staff:
                continue
            users.append(name)
            for key in servers:
                user_servers.append(f"{name}:{key}")

        # Format and return message

        message = dict()
        message["category"] = "MODS"
        message["subcategory"] = self._subcategory
        message["users"] = users
        message["user_servers"] = user_servers
        return message

    def hub_users(self):
        headers = dict(Authorization="token " + self._api_token)
        r = requests.get(self._api_url + "/users", headers=headers)
        r.raise_for_status()
        return r.json()

    def iris_staff(self):
        query = """{
          systemInfo {
            projects(repoName: "nstaff"){
              users {
                name
              }
            }
          }
        }"""

        try:
            r = requests.post("https://iris.nersc.gov/graphql", data=dict(query=query))
            r.raise_for_status()
        except Exception as err:
            LOGGER.warning("Iris error, assuming there are no staff!")
            return set()
        else:
            data = r.json()
            users = data["data"]["systemInfo"]["projects"][0]["users"]
            return set(u["name"] for u in users)


def main():
    args = parse_arguments()

    logging.basicConfig(level=args.log_level, format=LOG_FORMAT)

    amqp_url = f"amqp://{args.username}:{args.password}@{args.rabbitmq_host}"

    publisher = JupyterHubPublisher(
        args.api_token,
        args.api_url,
        args.subcategory,
        amqp_url,
        args.publish_interval,
        args.routing_key,
        args.exchange,
        args.exchange_type,
    )
    publisher.run()

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", "-l",
            default=logging.INFO, type=int)
    parser.add_argument("--api-token", "-o",
            default=os.environ["MODS_JUPYTERHUB_API_TOKEN"])
    parser.add_argument("--api-url", "-a",
            default="http://web-jupyterhub:8081/hub/api")
    parser.add_argument("--subcategory", "-s",
            default="jupyterhub_v10")
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
    return parser.parse_args()


if __name__ == '__main__':
    main()
