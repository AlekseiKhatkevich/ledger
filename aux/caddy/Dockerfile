FROM caddy:builder AS builder
RUN xcaddy build \
    --with github.com/ggicci/caddy-jwt \
    --with github.com/mholt/caddy-ratelimit
COPY . /etc/caddy

FROM caddy

# создаём пользователя и директории как root, выставляем права
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && \
    mkdir -p /etc/caddy /srv /data /config && \
    chown -R appuser:appgroup /etc/caddy /srv /data /config

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY --from=builder /etc/caddy /etc/caddy
USER appuser

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]