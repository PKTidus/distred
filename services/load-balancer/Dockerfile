FROM golang:1.25-alpine
WORKDIR /app
COPY . .
RUN apk add --no-cache git
RUN go mod tidy
RUN go build -o load-balancer .
EXPOSE 80
CMD ["./load-balancer"]