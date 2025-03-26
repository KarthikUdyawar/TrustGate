#!/bin/bash

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--file)
      DOCKER_COMPOSE_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Check if docker-compose.yml exists
if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
  echo "Error: Docker Compose file not found at $DOCKER_COMPOSE_FILE"
  exit 1
fi

# Create a directory for the certificates
mkdir -p containers/vault/certs

# Generate private key
openssl genrsa -out containers/vault/certs/vault-key.pem 2048

# Generate certificate signing request (CSR)
openssl req -new -key containers/vault/certs/vault-key.pem -out containers/vault/certs/vault.csr -config containers/vault/config/vault-san.cnf

# Generate self-signed certificate
openssl x509 -req -in containers/vault/certs/vault.csr -signkey containers/vault/certs/vault-key.pem -out containers/vault/certs/vault-cert.pem -days 365 -extensions req_ext -extfile containers/vault/config/vault-san.cnf

# Start Vault with Docker Compose
docker compose -f "$DOCKER_COMPOSE_FILE" --profile vault up -d

echo "Vault is up and running. You can access it at https://localhost:8200 and sleep for 10 seconds before running the next command."
sleep 5

docker exec -it vault vault operator init

echo "Copy the Unseal Keys and Token to a safe place."

read -p "Enter Unseal Key 1 : " key1
read -p "Enter Unseal Key 2 : " key2
read -p "Enter Unseal Key 3 : " key3
read -p "Enter Token : " token

docker exec -it vault vault operator unseal $key1
docker exec -it vault vault operator unseal $key2
docker exec -it vault vault operator unseal $key3

docker exec -it vault vault login $token

docker exec -it vault vault secrets enable -path=user_auth kv-v2

docker exec -it vault vault auth enable approle

cat ./containers/vault/policies/portal-policy.hcl | docker exec -i vault vault policy write portal -

docker exec -it vault vault write auth/approle/role/SecretPortal token_policies='portal' secret_id_ttl=0 token_ttl=0 token_max_ttl=0

ROLE_ID=$(docker exec -it vault vault read -field=role_id auth/approle/role/SecretPortal/role-id)
SECRET_ID=$(docker exec -it vault vault write -f -field=secret_id auth/approle/role/SecretPortal/secret-id)

# Echo the role-id and secret-id for portal
echo -e "\nUpdate VAULT_ROLE_ID and VAULT_SECRET_ID in .env"
echo -e "VAULT_ROLE_ID=$ROLE_ID"
echo -e "VAULT_SECRET_ID=$SECRET_ID"
