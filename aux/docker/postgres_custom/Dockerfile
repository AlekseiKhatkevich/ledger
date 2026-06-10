# Custom PostgreSQL 18 image with pg_ivm and pg_search extensions
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

# Clone pg_ivm at the specific commit that supports PG 18
# Pin to a specific commit for reproducible builds
ARG PG_IVM_COMMIT=2949e99d7cbd59039aa20f6444bf3b6e13e0c6d8
RUN git clone https://github.com/sraoss/pg_ivm.git /tmp/pg_ivm && \
    cd /tmp/pg_ivm && \
    git checkout ${PG_IVM_COMMIT}

# Build and install the extension
WORKDIR /tmp/pg_ivm
RUN make USE_PGXS=1 -j"$(nproc)" && \
    make USE_PGXS=1 install

# --- Final slim image ---
FROM postgres:18

# Install ca-certificates and curl for downloading pg_search
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl; \
    rm -rf /var/lib/apt/lists/*

# Copy pg_ivm from builder
COPY --from=builder /usr/lib/postgresql/18/lib/bitcode/pg_ivm /usr/lib/postgresql/18/lib/bitcode/pg_ivm
COPY --from=builder /usr/lib/postgresql/18/lib/pg_ivm.so /usr/lib/postgresql/18/lib/pg_ivm.so
COPY --from=builder /usr/share/postgresql/18/extension/pg_ivm* /usr/share/postgresql/18/extension/

# Install pg_search extension (ParadeDB) v0.24.0 for PG 18 on Debian 13 Trixie amd64
RUN curl -L \
    "https://github.com/paradedb/paradedb/releases/download/v0.24.0/postgresql-18-pg-search_0.24.0-1PARADEDB-trixie_amd64.deb" \
    -o /tmp/pg_search.deb && \
    apt-get install -y --no-install-recommends /tmp/pg_search.deb && \
    rm -f /tmp/pg_search.deb && \
    rm -rf /var/lib/apt/lists/*
