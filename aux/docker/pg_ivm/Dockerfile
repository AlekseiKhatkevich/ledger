# Custom PostgreSQL 18 image with pg_ivm extension
FROM postgres:18 AS builder

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        build-essential \
        git \
        libpq-dev \
        postgresql-server-dev-18; \
    rm -rf /var/lib/apt/lists/*

# Clone pg_ivm from the branch supporting PG 18
# Use GIT_SSL_NO_VERIFY=0 to ensure SSL works (ca-certificates is installed above)
RUN git clone --branch 133-support-postgresql-18 --depth 1 https://github.com/sraoss/pg_ivm.git /tmp/pg_ivm

# Build and install the extension
WORKDIR /tmp/pg_ivm
RUN make USE_PGXS=1 -j"$(nproc)" && \
    make USE_PGXS=1 install

# --- Final slim image ---
FROM postgres:18

COPY --from=builder /usr/lib/postgresql/18/lib/bitcode/pg_ivm /usr/lib/postgresql/18/lib/bitcode/pg_ivm
COPY --from=builder /usr/lib/postgresql/18/lib/pg_ivm.so /usr/lib/postgresql/18/lib/pg_ivm.so
COPY --from=builder /usr/share/postgresql/18/extension/pg_ivm* /usr/share/postgresql/18/extension/