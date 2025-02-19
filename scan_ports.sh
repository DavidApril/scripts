#!/bin/bash

# Check if IP and port range are provided
if [[ -z "$1" || -z "$2" ]]; then
  echo "Usage: $0 <IP> <start-port> <end-port>"
  echo "Example: $0 192.168.1.1 1 100"
  exit 1
fi

IP=$1
START_PORT=$2
END_PORT=${3:-65535} # Default to 65535 if end port is not provided

# Validate port range
if [[ $START_PORT -lt 1 || $END_PORT -gt 65535 || $START_PORT -gt $END_PORT ]]; then
  echo "Invalid port range. Please provide a valid range between 1 and 65535."
  exit 1
fi

# Maximum number of concurrent processes
MAX_CONCURRENT=100

# Function to scan a single port
scan_port() {
  local port=$1
  if timeout 2 bash -c "echo '' > /dev/tcp/$IP/$port" 2>/dev/null; then
    echo "[+] Port $port is OPEN"
  fi
}

# Export the function so it can be used by parallel
export -f scan_port

# Use xargs to control the number of concurrent processes
seq $START_PORT $END_PORT | xargs -I{} -P $MAX_CONCURRENT bash -c 'scan_port "$@"' _ {}

echo "Scan completed."
