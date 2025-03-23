#!/bin/bash

# Create a directory for the certificates
mkdir -p containers/vault/config

# Auto-detect values
IP_ADDRESS=$(hostname -I | awk '{print $1}')   # Get primary IP address
HOSTNAME=$(hostname)                           # Get system hostname

# Fetch location details using ipinfo.io
IPINFO=$(curl -s --max-time 5 ipinfo.io)  # Timeout set to 5 seconds

# Check if curl was successful
if [[ -z "$IPINFO" || "$IPINFO" == *"Rate limit exceeded"* ]]; then
    echo "⚠️  Warning: Failed to fetch location data from ipinfo.io. Using default values."
    COUNTRY="IN"
    STATE="Maharashtra"
    LOCALITY="$HOSTNAME"
else
    # Extract values using grep and sed (no jq required)
    COUNTRY=$(echo "$IPINFO" | grep -o '"country": *"[^"]*"' | cut -d'"' -f4)
    STATE=$(echo "$IPINFO" | grep -o '"region": *"[^"]*"' | cut -d'"' -f4)
    LOCALITY=$(echo "$IPINFO" | grep -o '"city": *"[^"]*"' | cut -d'"' -f4)

    # Validate extracted values and set defaults if empty
    COUNTRY=${COUNTRY:-"IN"}
    STATE=${STATE:-"Maharashtra"}
    LOCALITY=${LOCALITY:-"$HOSTNAME"}
fi

ORG_UNIT="IT"        # Default organizational unit
CN=$HOSTNAME         # Use hostname as common name
DNS_NAME=$IP_ADDRESS # Default DNS to the IP address

# Define configuration filename
CNF_FILE="${PWD}/containers/vault/config/vault-san.cnf"

# Generate the CNF file
cat <<EOF > $CNF_FILE
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C = $COUNTRY
ST = $STATE
L = $LOCALITY
OU = $ORG_UNIT
CN = $CN

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DNS_NAME
IP.1 = $IP_ADDRESS
EOF

# Final confirmation
if [[ -f "$CNF_FILE" ]]; then
    echo -e "\n✅ Successfully generated $CNF_FILE with location-based auto-filled values!\n"
else
    echo -e "\n❌ Error: Failed to create $CNF_FILE. Check file permissions.\n"
fi
