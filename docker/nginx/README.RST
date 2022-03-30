From this directory:
docker build -t nginxmax:v0 -f Dockerfile.nginx.txt .

-- with --rm when we close it the docker is deleted
docker run --rm -p 80:80 --add-host max.local:127.0.0.1 --add-host oauth.local:127.0.0.1 --add-host hub.local:127.0.0.1 --name nginxtmp -it --add-host host.docker.internal:host-gateway nginxmax:v0 bash

-- if we do not want the docker to be deleted
docker run -p 80:80 --add-host max.local:127.0.0.1 --add-host oauth.local:127.0.0.1 --add-host hub.local:127.0.0.1 --name nginxtmp -it --add-host host.docker.internal:host-gateway nginxmax:v0 bash

-- in the container's shell:
nginx -t -c /etc/nginx/nginx.conf

-- if everythins is fine:
service nginx start

-- if you want to see the logs:
tail -f /var/log/nginx/*.log