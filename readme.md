Setting up Kafka
https://www.digitalocean.com/community/tutorials/how-to-install-apache-kafka-on-ubuntu-20-04

sudo systemctl start kafka
sudo systemctl status kafka

./kafka-topics.sh --create --topic whatsapp-messages --bootstrap-server localhost:9092 --replication-factor 1 --partitions 4

./kafka-topics.sh --create --topic ad-manager --bootstrap-server localhost:9092 --replication-factor 1 --partitions 4

echo "Hello, World" | ~/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic whatsapp-messages > /dev/null

./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic whatsapp-messages --from-beginning
