#!/bin/bash

set -e

echo "=== Building base image ==="
docker build \
  -f docker/Dockerfile.services \
  -t preprocessing:notebook .

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

echo "=== Cleaning stale plugin containers ==="
docker compose $COMPOSE_FILES down --remove-orphans >/dev/null 2>&1 || true
for stale in preprocessing-notebook preprocessing-xai preprocessing-gmic preprocessing-resnet-classification preprocessing-unet-segmentation preprocessing-yolox; do
    docker rm -f "$stale" >/dev/null 2>&1 || true
done

echo "=== Starting up ==="
docker compose $COMPOSE_FILES up -d

