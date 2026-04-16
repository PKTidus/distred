#!/bin/sh
set -e

# Substitute environment variables in the template
envsubst '${BACKENDS}' < /usr/local/etc/haproxy/haproxy.cfg.template > /usr/local/etc/haproxy/haproxy.cfg

# Ensure there is a trailing newline to prevent HAProxy 'Missing LF' error
echo >> /usr/local/etc/haproxy/haproxy.cfg

# Execute the original entrypoint or the command passed to the container
exec "$@"
