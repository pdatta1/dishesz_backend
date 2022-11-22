FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY dishesz.nginx.conf /etc/nginx/sites-available/dishesz.nginx.conf
RUN mkdir /etc/nginx/sites-enabled
RUN ln -s /etc/nginx/sites-available/dishesz.nginx.conf /etc/nginx/sites-enabled/

