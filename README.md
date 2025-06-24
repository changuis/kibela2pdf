# Kibela to PDF Converter

This tool extracts content from Kibela pages and generates PDF files with specific formatting requirements.

## Features

- Extracts content from Kibela pages using the Kibela API
- Generates clean PDF files without metadata, dates, or unwanted elements
- Preserves table formatting with borders and bold headers
- Maintains proper heading hierarchy (H1, H2, H3, H4)
- Excludes folder information, table of contents, and comments
- No page count or temp file paths in footer
- Supports Japanese fonts for proper rendering

## Available Versions

### 1. WeasyPrint Version (`kibela_to_pdf.py`)
Uses WeasyPrint for HTML-to-PDF conversion with advanced CSS support.

### 2. ReportLab Version (`kibela_to_pdf_alternative.py`) - **Recommended for macOS**
Uses ReportLab for PDF generation, more reliable on macOS systems.

## Quick Setup

Run the setup script for automatic installation:
```bash
./setup.sh
```

This will:
- Install Python dependencies
- Make scripts executable
- Check environment variables

## Manual Prerequisites

1. **Environment Variables**: Make sure you have the following environment variables set in your `.zshrc`:
   ```bash
   export KIBELA_TOKEN=your_kibela_api_token
   export KIBELA_TEAM=your_team_name
   ```

2. **Python Dependencies**: 
   
   **For WeasyPrint version:**
   ```bash
   pip3 install -r requirements.txt
   # May require additional system libraries on macOS:
   brew install pango gdk-pixbuf libffi gobject-introspection
   ```
   
   **For ReportLab version (recommended):**
   ```bash
   pip3 install -r requirements_alternative.txt
   ```

## Usage

### Simple Wrapper Script (Easiest)
```bash
# Basic usage
./kibela2pdf "https://your-team.kibe.la/notes/12345"

# Specify output file
./kibela2pdf "https://your-team.kibe.la/notes/12345" -o "my-document.pdf"
```

### ReportLab Version (Recommended)
```bash
# Basic usage
python3 kibela_to_pdf_alternative.py "https://your-team.kibe.la/notes/12345"

# Specify output file
python3 kibela_to_pdf_alternative.py "https://your-team.kibe.la/notes/12345" -o "my-document.pdf"
```

### WeasyPrint Version
```bash
# Basic usage
python3 kibela_to_pdf.py "https://your-team.kibe.la/notes/12345"

# Specify output file
python3 kibela_to_pdf.py "https://your-team.kibe.la/notes/12345" -o "my-document.pdf"
```

### Make Scripts Executable (Optional)
```bash
chmod +x kibela_to_pdf_alternative.py
./kibela_to_pdf_alternative.py "https://your-team.kibe.la/notes/12345"
```

## Command Line Options

- `url`: Kibela page URL (required)
- `-o, --output`: Output PDF file path (optional, defaults to sanitized page title)

## Examples

```bash
# Convert a Kibela page to PDF with auto-generated filename (ReportLab)
python3 kibela_to_pdf_alternative.py "https://spikestudio.kibe.la/notes/12345"

# Convert with custom output filename (ReportLab)
python3 kibela_to_pdf_alternative.py "https://spikestudio.kibe.la/notes/12345" -o "project-documentation.pdf"

# Using WeasyPrint version
python3 kibela_to_pdf.py "https://spikestudio.kibe.la/notes/12345" -o "project-documentation.pdf"
```

## Output Format

The generated PDF will include:
- ✅ Page title as H1 heading
- ✅ Proper heading hierarchy (H1, H2, H3, H4)
- ✅ Tables with borders and bold headers
- ✅ Clean content without metadata
- ✅ Japanese font support
- ❌ No dates or timestamps
- ❌ No folder information
- ❌ No table of contents
- ❌ No comments
- ❌ No page numbers in footer
- ❌ No temp file paths

## Troubleshooting

1. **API Authentication Error**: Ensure your `KIBELA_TOKEN` and `KIBELA_TEAM` environment variables are correctly set.

2. **Note Not Found**: Verify the Kibela URL is correct and you have access to the note.

3. **PDF Generation Error**: Make sure all dependencies are installed correctly, especially WeasyPrint.

4. **Font Issues**: The script uses Japanese-compatible fonts. If you encounter font rendering issues, ensure your system has the required fonts installed.

## Dependencies

- `requests`: For API calls to Kibela
- `beautifulsoup4`: For HTML parsing and cleaning
- `weasyprint`: For PDF generation
- `html2text`: For text processing
- `lxml`: For XML/HTML parsing
