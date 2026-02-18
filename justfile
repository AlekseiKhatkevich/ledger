default: up-dev

up-dev:
    docker compose up --watch --remove-orphans

down-dev:
    docker compose down