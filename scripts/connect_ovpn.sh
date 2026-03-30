#!/usr/bin/env bash

CONFIG="/root/.ssh/ovpn-kskb-ix.conf"
LOG="/tmp/openvpn.log"
STATUS="/tmp/openvpn.status"
TIMEOUT=10   # seconds to wait for connection
# Start OpenVPN in background (daemon mode)
openvpn --config "$CONFIG" \
        --daemon \
        --log "$LOG" \
        --status "$STATUS" 1

# Wait for connection or failure
elapsed=0
while [ $elapsed -lt $TIMEOUT ]; do
    if grep -q "Initialization Sequence Completed" "$LOG" 2>/dev/null; then
        echo "VPN connected successfully."
        exit 0
    fi

    if grep -q "AUTH_FAILED\|ERROR" "$LOG" 2>/dev/null; then
        echo "VPN connection failed."
        exit 1
    fi

    sleep 1
    elapsed=$((elapsed + 1))
done

echo "VPN connection timeout."
exit 1