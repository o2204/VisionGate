#!/bin/bash

# Function to display messages in color
print_message() {
    local color=$1
    local message=$2
    case $color in
        "green") echo -e "\e[32m$message\e[0m" ;;
        "cyan") echo -e "\e[36m$message\e[0m" ;;
        "yellow") echo -e "\e[33m$message\e[0m" ;;
        "red") echo -e "\e[31m$message\e[0m" ;;
        *) echo "$message" ;;
    esac
}

# Kill existing processes on port 8000
print_message "yellow" "Cleaning up existing processes on port 8000..."
fuser -k 8000/tcp 2>/dev/null

# Root directory
ROOT_DIR=$(pwd)

# Backend
print_message "cyan" "Starting Backend API..."
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
    print_message "yellow" "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# Check if dependencies are installed (simple check)
if ! pip show fastapi > /dev/null 2>&1; then
    print_message "yellow" "Installing backend dependencies..."
    pip install -r requirements.txt
fi

print_message "green" "Starting FastAPI Backend..."
python -m uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
print_message "cyan" "Starting Flutter Frontend..."
cd "$ROOT_DIR/ui/visiongate"

# Check if flutter is available
if ! command -v flutter &> /dev/null; then
    print_message "red" "Flutter command not found. Please ensure Flutter is installed and in your PATH."
    kill $BACKEND_PID
    exit 1
fi

print_message "yellow" "Getting Flutter packages..."
flutter pub get > /dev/null

print_message "green" "Starting Flutter app on Chrome..."
flutter run -d chrome &
FRONTEND_PID=$!

echo ""
print_message "green" "====================================="
print_message "green" "All services are starting!"
print_message "cyan" "Backend: http://localhost:8000"
print_message "cyan" "Frontend: Flutter Web (Chrome)"
print_message "yellow" "Press Ctrl+C to stop everything."
print_message "green" "====================================="

# Handle shutdown
cleanup() {
    print_message "red" "\nStopping all services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

trap cleanup SIGINT

# Keep script running
wait
