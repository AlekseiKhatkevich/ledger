#!/usr/bin/env just --justfile

default: up-dev

alias up := up-dev
alias down := down-dev

profile := ""

up-dev:
    docker compose  up --watch --remove-orphans

down-dev:
    docker compose down