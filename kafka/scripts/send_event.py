import argparse
import json
from kafka import KafkaProducer

parser = argparse.ArgumentParser(
    description='Push events to a Kafka server', add_help=False)
parser.add_argument('topics', type=str, nargs="+",
                    help="name of the topics that will receive the messages")
parser.add_argument('-k', '--key', type=str, default=None,
                    help='the message key')
parser.add_argument('-p', '--partition', type=int, default=None,
                    help='the partition which will receive the messages')
parser.add_argument('-h', '--host', type=str, default="localhost:9094",
                    help='host of Kafka server')
parser.add_argument('-f', '--file', type=str, default="events.json",
                    help='file with the events to be sent')
parser.add_argument('-s', '--server', type=str, default="fake-live.mconf.com",
                    help='name of the server which will sign the events in the header')
parser.add_argument('--help', action="help")

args = parser.parse_args()

p = KafkaProducer(bootstrap_servers=[args.host])


def delivery_report(metadata):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    print(f'Sucessfull sent message to {metadata.topic_partition.topic}')


with open(args.file, 'r') as file:
    events = json.load(file)
    for topic in args.topics:
        for data in events:
            try:
                response = p.send(topic, value=json.dumps(data).encode(
                    'utf-8'), key=str(args.key).encode('utf-8'), partition=args.partition, headers=[('server', str(args.server).encode('utf-8'))])
                response.add_callback(delivery_report)
            except Exception as err:
                print(f'Error sending the message: {err}')
        p.flush()
