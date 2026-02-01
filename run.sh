#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Home Assistant User Profile Add-on..."

# Check if SUPERVISOR_TOKEN is present
if [ -z "$SUPERVISOR_TOKEN" ]; then
    bashio::log.warning "SUPERVISOR_TOKEN not found. API calls will fail."
else
    bashio::log.info "SUPERVISOR_TOKEN found."
fi

bashio::log.info "Starting Flask server on port 8099..."

# Start the Python application
exec python3 /app/app.py
