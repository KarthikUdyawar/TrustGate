#!/bin/bash

# Auto-detect values
IP_ADDRESS=$(hostname -I | awk '{print $1}')   # Get primary IP address

# Define configuration filename
HCL_FILE="${PWD}/containers/vault/config/hcl.config"

# Generate the CNF file
cat <<EOF > $HCL_FILE
storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/vault/certs/vault-cert.pem"
  tls_key_file  = "/vault/certs/vault-key.pem"
}

api_addr = "https://$IP_ADDRESS:8200"
cluster_addr = "https://$IP_ADDRESS:8201"
ui = true
EOF

# Final confirmation
if [[ -f "$HCL_FILE" ]]; then
    echo -e "\n✅ Successfully generated $HCL_FILE.\n"
else
    echo -e "\n❌ Error: Failed to create $HCL_FILE. Check file permissions.\n"
fi
