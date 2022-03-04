From this directory:
docker build -t nginxmax:v0 -f Dockerfile.nginx.txt .
docker run --rm --add-host max.local:127.0.0.1 --add-host oauth.local:127.0.0.1 --add-host hub.local:127.0.0.1 --name nginxtmp -it --add-host host.docker.internal:host-gateway nginxmax:v0 bash

-- in the container's shell:
nginx -t -c /etc/nginx/nginx.conf

-- if everythins is fine:
service nginx start
