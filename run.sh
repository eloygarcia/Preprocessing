#!/bin/bash

set -e

docker build \
  -f docker/Dockerfile.services \
  -t preprocessing:notebook .

for plugin in $(find plugin_framework/plugins -name plugin.yaml); do

    IMAGE=$(yq '.docker.image' "$plugin")
    DOCKERFILE=$(yq '.docker.dockerfile' "$plugin")

    docker build \
        -t "$IMAGE" \
        -f "$DOCKERFILE" \
        .
done

docker compose up -d