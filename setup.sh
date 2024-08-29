#!/bin/bash


show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Choose the system you would like to install on your device for thr: TxUUT, RxMeas, ControlPC"
    echo "Options:"
    echo "  --systen <system_name>   Specify the username."
    echo "  --help              Display this help message."
    exit 0
}

if [[ $# -eq 0 ]]; then
    echo "No parameters provided."
    show_help
    exit 1
fi

SYSTEM=""

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --system) SYSTEM="$2"; shift ;;  # Assign the value of the user parameter
        --help) show_help;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Check if the user parameter is set
if [[ -z "$USER" ]]; then
    echo "Missing required parameter:  --system <system_name>"
    show_help
    exit 1
fi

if [[ "$SYSTEM" != "RxMeas" && "$SYSTEM" != "TxUUT" && "$SYSTEM" != "ControlPC" ]]; then
    echo "Wrong system name"
    exit 1
fi

UTILS_DIR="$(pwd)/utils"
PROTO_FILE="$UTILS_DIR/Messages.proto"  # Example .proto file
echo "Compiling proto file"
PROTO_DIR=$(dirname "$PROTO_FILE")
PROTO_BASENAME=$(basename "$PROTO_FILE")

if [[ "$SYSTEM" != "RxMeas" ]]; then
    protoc --proto_path="$PROTO_DIR" --python_out="$UTILS_DIR" "$PROTO_BASENAME"
fi

if [[ "$SYSTEM" == "ControlPC" ]]; then
    exit 1
fi

if [ "$SYSTEM" = "TxUUT" ]; then
    EXEC_START="/usr/bin/python3 $(pwd)/TxUUT/main.py"  #
    DESCRIPTION="TxUUT service"
else
    protoc --proto_path="$PROTO_DIR" --cpp_out="$UTILS_DIR" "$PROTO_BASENAME"
    BUILD_DIR="$(pwd)/RxMeas/build"
    echo "Creating build directory..."
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR" || exit
    cmake ..  # Assuming CMakeLists.txt is located in RxMeas/main/
    make
    cd ../..
    EXEC_START="$(pwd)/RxMeas/build/main"  #
    DESCRIPTION="RxMeas service"
fi

# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/${SYSTEM}.service"

echo "Creating systemd service file at ${SERVICE_FILE}..."

sudo bash -c "cat > ${SERVICE_FILE} <<EOL
[Unit]
Description=${DESCRIPTION}

[Service]
ExecStart=${EXEC_START}
Restart=always
User=$(whoami)
Group=$(whoami)

[Install]
WantedBy=multi-user.target
EOL"

# Reload systemd to recognize the new service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling ${SYSTEM} service..."
sudo systemctl enable ${SYSTEM}.service

# Start the service immediately (optional)
echo "Starting ${SYSTEM} service..."
sudo systemctl start ${SYSTEM}.service

echo "Service setup complete!"

