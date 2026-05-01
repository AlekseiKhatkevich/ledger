FROM caddy:builder AS builder
RUN xcaddy build --with github.com/ss098/certmagic-s3
COPY . /etc/caddy

FROM caddy
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY --from=builder /etc/caddy /etc/caddy


CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
