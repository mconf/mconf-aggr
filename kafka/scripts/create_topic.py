from kafka import KafkaAdminClient
from kafka.admin.new_topic import NewTopic
import argparse

parser = argparse.ArgumentParser(
    description='Create topic in a Kafka server', add_help=False)
parser.add_argument('topics', type=str, nargs="+",
                    help="name of the topics to be created")
parser.add_argument('-p', '--partitions', type=int, nargs=1, default=1,
                    help='number of partitions')
parser.add_argument('-r', '--replicas', type=int, nargs=1, default=1,
                    help='number of replicas')
parser.add_argument('-h', '--host', type=str, nargs=1, default="localhost:9094",
                    help='host of Kafka server')
parser.add_argument('--help', action="help")

args = parser.parse_args()
args.host = args.host[0]

admin_client = KafkaAdminClient(**{'bootstrap_servers': args.host})

new_topics = [NewTopic(
    topic, num_partitions=args.partitions, replication_factor=args.replicas) for topic in args.topics]

try:
    admin_client.create_topics(new_topics)
    print('Topic created!')
except Exception as err:
    print(f'Error creating the topic: {err}')
