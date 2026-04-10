#!/bin/bash
ZONE="us-west3-a"
MACHINE="e2-micro"
IMAGE_FAMILY="debian-12"
IMAGE_PROJECT="debian-cloud"
PROJECT="distributed-systems-487323"

# Create 2 Load Balancers (with external IP)
gcloud compute instances create load-balancer-go \
  --zone=$ZONE \
  --machine-type=$MACHINE \
  --image-family=$IMAGE_FAMILY \
  --image-project=$IMAGE_PROJECT \
  --boot-disk-size=10GB \
  --tags=load-balancer,frontend

gcloud compute instances create load-balancer-nginx \
  --zone=$ZONE \
  --machine-type=$MACHINE \
  --image-family=$IMAGE_FAMILY \
  --image-project=$IMAGE_PROJECT \
  --boot-disk-size=10GB \
  --tags=load-balancer,frontend

# Create 3 API Gateways (Internal only)
for i in 0 1 2; do
  gcloud compute instances create api-gateway-$i \
    --zone=$ZONE \
    --machine-type=$MACHINE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=10GB \
    --no-address \
    --tags=api-gateway
done

# Create 1 of each API Server (Internal only)
SERVICES=("user-service" "post-service" "subreddit-service" "vote-service" "feed-service")
for service in "${SERVICES[@]}"; do
  gcloud compute instances create $service \
    --zone=$ZONE \
    --machine-type=$MACHINE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=10GB \
    --no-address \
    --tags=backend-service
done

# Create 1 Redis Cache server (Internal only)
gcloud compute instances create gateway-cache \
  --zone=$ZONE \
  --machine-type=$MACHINE \
  --image-family=$IMAGE_FAMILY \
  --image-project=$IMAGE_PROJECT \
  --boot-disk-size=10GB \
  --no-address \
  --tags=cache

# Ensure NAT is set up for internal instances to reach the internet (for updates/builds)
gcloud compute routers create nat-router \
  --project=$PROJECT \
  --network=default \
  --region=us-west3 || true

gcloud compute routers nats create nat-gateway \
  --project=$PROJECT \
  --router=nat-router \
  --region=us-west3 \
  --auto-allocate-nat-external-ips \
  --nat-all-subnet-ip-ranges || true
