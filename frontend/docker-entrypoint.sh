#!/usr/bin/env sh
set -e
# Render and other hosts inject PORT; default to 80 for Docker Compose + Traefik.
PORT="${PORT:-80}"
sed -i.bak "s/listen 80;/listen ${PORT};/" /etc/nginx/conf.d/default.conf
exec nginx -g "daemon off;"
