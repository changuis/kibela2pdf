#!/bin/bash
# Setup script for Kibela to PDF Converter

echo "🚀 Setting up Kibela to PDF Converter..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ Python 3 and pip3 found"

# Install Python dependencies for ReportLab version (recommended)
echo "📦 Installing Python dependencies..."
pip3 install -r requirements_alternative.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x kibela_to_pdf_alternative.py
chmod +x kibela2pdf

echo "✅ Scripts are now executable"

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$KIBELA_TOKEN" ] || [ -z "$KIBELA_TEAM" ]; then
    echo "⚠️  Environment variables not set"
    echo "Please add the following to your .zshrc:"
    echo ""
    echo "export KIBELA_TOKEN=your_kibela_api_token"
    echo "export KIBELA_TEAM=your_team_name"
    echo ""
    echo "Then run: source ~/.zshrc"
else
    echo "✅ Environment variables are set"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Usage examples:"
echo "  ./kibela2pdf \"https://your-team.kibe.la/notes/12345\""
echo "  ./kibela2pdf \"https://your-team.kibe.la/notes/12345\" -o \"my-document.pdf\""
echo ""
echo "For more information, see README.md"
