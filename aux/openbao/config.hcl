# OpenBao configuration with PostgreSQL storage backend and file-based auto-unseal
#
# - Data: PostgreSQL (citus-coordinator) via BAO_PG_CONNECTION_STRING env variable
# - Unseal: file-backed seal keyring on /bao/keyring volume — auto-unseals on restart
# - Listener: plain TCP on port 8200 (TLS termination handled by HAProxy/Caddy upstream)

storage "postgresql" {
  connection_url = "postgresql://openbao_user:1q2w3e@citus-coordinator:5432/openbao?sslmode=disable"
  max_parallel=30
  max_connect_retries=2
}

# seal "file" {
#   path = "/bao/keyring"
# }

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true
}

ui = true

api_addr = "http://localhost:8200"