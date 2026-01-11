#!/bin/bash
# HubSign Landing - Development Server Start Script
# Auto-reloads on file changes

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting HubSign Landing Development Server...${NC}"

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Virtual environment not found. Run ./setup.sh first.${NC}"
    exit 1
fi

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Django not installed. Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

echo -e "${GREEN}✅ Starting Django server with auto-reload...${NC}"
echo -e "${BLUE}📍 URL: http://127.0.0.1:8000${NC}"
echo -e "${YELLOW}💡 Press CTRL+C to stop${NC}"
echo ""

# Start Django development server with auto-reload (default behavior)
python manage.py runserver
