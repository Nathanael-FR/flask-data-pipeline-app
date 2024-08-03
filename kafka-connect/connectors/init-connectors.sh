#!/bin/bash

# Start Kafka Connect
/etc/confluent/docker/run &

# Wait for Kafka Connect to be ready
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://localhost:8083/connectors)" != "200" ]]; do
  echo "Waiting for Kafka Connect to start..."
  sleep 5
done

# Post the connector configuration
curl -X POST -H "Content-Type: application/json" --data @/etc/kafka-connect/jars/your-connector-config.json http://localhost:8083/connectors

# Keep the container running
tail -f /dev/null
