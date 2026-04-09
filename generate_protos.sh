#!/bin/bash

PROTO_SRC="./proto"

if ! python3 -c "import grpc_tools" &>/dev/null; then
    echo "grpcio-tools is not installed in this python environment. Please install it with:"
    echo "pip3 install grpcio-tools"
    exit 1
fi
# Usage: generate_proto <proto_file_name> <destination_directory>
generate_proto() {
    FILE_NAME=$1
    DEST_DIR=$2

    echo "Generating $FILE_NAME for $DEST_DIR..."

    mkdir -p $DEST_DIR

    # A. Generate the Python gRPC code
    python3 -m grpc_tools.protoc \
        -I$PROTO_SRC \
        --python_out=$DEST_DIR \
        --pyi_out=$DEST_DIR \
        --grpc_python_out=$DEST_DIR \
        $PROTO_SRC/$FILE_NAME.proto

    # B. Fix imports: absolute -> relative to avoid ModuleNotFoundError
    sed -i.bak 's/^import \(.*_pb2\)/from . import \1/' $DEST_DIR/*_pb2_grpc.py
    rm -f $DEST_DIR/*_pb2_grpc.py.bak


    # C. Ensure directory is a Python package
    touch $DEST_DIR/__init__.py
}
generate_go_proto() {
    FILE_NAME=$1
    DEST_DIR=$2

    echo "Generating Go proto for $FILE_NAME in $DEST_DIR..."

    mkdir -p "$DEST_DIR"

    protoc \
        -I"$PROTO_SRC" \
        --go_out="$DEST_DIR" --go_opt=paths=source_relative \
        --go-grpc_out="$DEST_DIR" --go-grpc_opt=paths=source_relative \
        "$PROTO_SRC/$FILE_NAME.proto"
}

# --- Services and their proto dependencies ---

# user.proto -> user-service (server) + api-gateway (client) + post-service (client)
generate_proto "user" "./services/user-service/generated"
generate_proto "user" "./services/api-gateway/generated"
generate_proto "user" "./services/post-service/generated"

# post.proto -> post-service (server) + api-gateway (client) + feed-service (client)
generate_proto "post" "./services/post-service/generated"
generate_proto "post" "./services/api-gateway/generated"
generate_proto "post" "./services/feed-service/generated"

# vote.proto -> vote-service (server) + api-gateway (client) + feed-service (client) + post-service (client)
generate_proto "vote" "./services/vote-service/generated"
generate_proto "vote" "./services/api-gateway/generated"
generate_proto "vote" "./services/feed-service/generated"
generate_proto "vote" "./services/post-service/generated"

# feed.proto -> feed-service (server) + api-gateway (client)
generate_proto "feed" "./services/feed-service/generated"
generate_proto "feed" "./services/api-gateway/generated"

# subreddit.proto -> subreddit-service (server) + api-gateway (client) + post-service (client)
generate_proto "subreddit" "./services/subreddit-service/generated"
generate_proto "subreddit" "./services/api-gateway/generated"
generate_proto "subreddit" "./services/post-service/generated"

# health-check.proto -> api-gateway (server) + health-check-service (client)
generate_proto "health-check" "./services/api-gateway/generated"

# health-check.proto -> health-check-service (server)
generate_go_proto "health-check" "./services/load-balancer/generated"

echo "Done! Protos generated and imports fixed."