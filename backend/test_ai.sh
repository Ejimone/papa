#!/bin/bash

# AI API Testing Script
# This script starts the server and runs the AI endpoints tests

echo "🚀 AI-Powered Past Questions App - Testing Setup"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Please run this script from the backend directory"
    echo "cd backend && ./test_ai.sh"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Install requests if not available
echo "📦 Checking dependencies..."
python3 -c "import requests" 2>/dev/null || {
    echo "Installing requests library..."
    pip install requests
}

# Function to start server in background
start_server() {
    echo "🌐 Starting FastAPI server..."
    python3 run.py &
    SERVER_PID=$!
    echo "Server started with PID: $SERVER_PID"
    
    # Wait for server to start
    echo "⏳ Waiting for server to start..."
    sleep 5
    
    # Check if server is responsive
    for i in {1..10}; do
        if curl -s http://localhost:4321/ > /dev/null 2>&1; then
            echo "✅ Server is running and responsive!"
            return 0
        fi
        echo "   Waiting... ($i/10)"
        sleep 2
    done
    
    echo "❌ Server failed to start or is not responsive"
    return 1
}

# Function to stop server
stop_server() {
    if [ ! -z "$SERVER_PID" ]; then
        echo "🛑 Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null
        sleep 2
        # Force kill if still running
        kill -9 $SERVER_PID 2>/dev/null
    fi
}

# Function to run tests
run_tests() {
    echo "🧪 Running AI endpoints tests..."
    python3 test_ai_simple.py
    return $?
}

# Trap to ensure server is stopped on exit
trap stop_server EXIT

# Main execution
main() {
    # Start the server
    if start_server; then
        echo ""
        echo "🔗 Server is running at: http://localhost:4321"
        echo "📖 API Documentation: http://localhost:4321/api/v1/docs"
        echo ""
        
        # Run the tests
        if run_tests; then
            echo ""
            echo "🎉 All tests completed successfully!"
            echo ""
            echo "💡 Next steps:"
            echo "   1. Check the FastAPI docs at http://localhost:4321/api/v1/docs"
            echo "   2. Test individual endpoints manually"
            echo "   3. Add authentication for protected endpoints"
            echo "   4. Add more test data and edge cases"
        else
            echo ""
            echo "⚠️  Some tests failed - check the output above"
            echo ""
            echo "🔧 Troubleshooting:"
            echo "   1. Check environment variables in .env file"
            echo "   2. Verify database connection"
            echo "   3. Ensure all AI service dependencies are configured"
        fi
        
        # Keep server running for manual testing
        echo ""
        echo "🖥️  Server is still running for manual testing..."
        echo "   Press Ctrl+C to stop the server and exit"
        echo ""
        
        # Wait for user interrupt
        wait $SERVER_PID
    else
        echo "❌ Failed to start server. Check the logs above."
        exit 1
    fi
}

# Check if running in interactive mode
if [ "$1" = "--test-only" ]; then
    echo "Running tests only (assuming server is already running)..."
    run_tests
    exit $?
fi

# Run main function
main
