from kafka import KafkaConsumer

consumer = KafkaConsumer('sample', bootstrap_servers = 'localhost:32768')
for message in consumer:
    print (message)
