FROM nginx:latest

COPY nginx.conf.template /etc/nginx/templates/default.conf.template

ENV BACKENDS="server api-gateway-1:8000; server api-gateway-2:8000;"

CMD ["nginx", "-g", "daemon off;"]
