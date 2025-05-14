#!/usr/bin/env bash

include .env
export $(shell sed 's/=.*//' .env)

DOCKER_COMPOSE = docker compose -p $(ROOT_PROJECT_NAME)

CONTAINER_SE := $(shell docker container ls -f "name=$(ROOT_PROJECT_NAME)-sound-extractor" -q)

SE := docker exec -ti $(CONTAINER_SE)

fix:
	$(SE) ruff check --fix --exclude src/Protobuf --unsafe-fixes
	$(SE) black src --exclude "src/Protobuf"
