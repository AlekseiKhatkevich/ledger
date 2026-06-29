cluster_name = "openbao-ledger"

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
  cluster_address = "0.0.0.0:8201"
  tls_disable = true
}

log_level = "info"

ui = true

api_addr = "http://localhost:8200"

path "cubbyhole/test" {
  capabilities = ["read"]
}