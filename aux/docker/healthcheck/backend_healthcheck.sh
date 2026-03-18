#!/bin/sh

if [ "$DEBUG" -ne "1" ]; then
    curl -f http://localhost:8000/aux/health || exit 1
else
    exit 0  # Если DEBUG=1, просто возвращаем успех, а то заебывает вывод в логах...
fi