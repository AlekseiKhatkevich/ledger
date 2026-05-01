FROM caddy:builder AS builder

RUN xcaddy build --with github.com/ss098/certmagic-s3 --with github.com/ggicci/caddy-jwt

COPY . /etc/caddy


FROM caddy

RUN addgroup -S appgroup && adduser -S appuser -G appgroup \  && \
    mkdir -p /etc/caddy /srv /data \ && \
    chown -R appuser:appgroup /etc/caddy /srv /data

COPY --from=builder --chown=appuser:appgroup /usr/bin/caddy /usr/bin/caddy
COPY --from=builder --chown=appuser:appgroup /etc/caddy /etc/caddy

USER appuser

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
