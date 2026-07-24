#!/bin/bash

set -e

echo "=== Building base image ==="
# docker build \
#   -f docker/Dockerfile.services \
#   -t preprocessing:notebook .

echo "=== Building plugins ==="

for plugin in plugin_framework/plugins/*; do
    if [ -f "$plugin/plugin.yaml" ]; then
        echo "Found plugin: $plugin"
        IMAGE=$(yq -r '.docker.image' "$plugin/plugin.yaml")
        echo "Building $IMAGE"
        docker build \
            -t "$IMAGE" \
            "$plugin"
    fi
done

echo "=== Starting compose ==="
COMPOSE_FILES="-f docker-compose.yml"

for plugin in plugin_framework/plugins/*; do
    if [ -f "$plugin/docker-compose.yml" ]; then
        COMPOSE_FILES="$COMPOSE_FILES -f $plugin/docker-compose.yml"
    fi
done

echo "=== Starting up ==="
docker compose $COMPOSE_FILES up -d

