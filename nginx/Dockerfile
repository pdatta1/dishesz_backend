FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY backend.nginx.conf /etc/nginx/sites-available/backend.nginx.conf
RUN mkdir /etc/nginx/sites-enabled
RUN ln -s /etc/nginx/sites-available/backend.nginx.conf /etc/nginx/sites-enabled/

