# Kibela to PDF Converter

This tool extracts content from Kibela pages and generates PDF files with specific formatting requirements.

## Features

- Extracts content from Kibela pages using the Kibela API
- Generates clean PDF files without metadata, dates, or unwanted elements
- Preserves table formatting with borders and bold headers
- Maintains proper heading hierarchy (H1, H2, H3, H4)
- **✅ Clickable links** - Links appear as blue underlined text and open URLs when clicked
- **✅ Image support** - Automatically uses local PNG files (1.png, 2.png, 3.png) when available
- **✅ Code blocks** - Monospace formatting with grey background and borders
- **✅ Numbered lists** - Proper sequential numbering (1., 2., 3., etc.)
- Excludes folder information, table of contents, and comments
- No page count or temp file paths in footer
- Supports Japanese fonts for proper rendering

## Available Versions

### 1. WeasyPrint Version (`kibela_to_pdf.py`)
Uses WeasyPrint for HTML-to-PDF conversion with advanced CSS support.

### 2. ReportLab Version (`kibela_to_pdf_alternative.py`) - **Recommended for macOS**
Uses ReportLab for PDF generation, more reliable on macOS systems with enhanced features:
- **Clickable links** in tables and paragraphs
- **Local image embedding** (automatically uses 1.png, 2.png, 3.png files)
- **Enhanced code block formatting**
- **Better Japanese font support**

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

## Image Support

The ReportLab version automatically embeds local PNG files when available:

1. **Place your images** in the same directory as the script
2. **Name them sequentially**: `1.png`, `2.png`, `3.png`, etc.
3. **Run the converter** - it will automatically use these images in order

```bash
# Example directory structure:
kibela2pdf/
├── 1.png          # First image in the document
├── 2.png          # Second image in the document
├── 3.png          # Third image in the document
└── kibela_to_pdf_alternative.py

# Run the converter
./kibela2pdf "https://your-team.kibe.la/notes/12345"
```

The script will:
- ✅ Use `1.png` for the first image found in the HTML
- ✅ Use `2.png` for the second image found in the HTML
- ✅ Scale images to fit PDF page width (max 400 points)
- ✅ Embed high-quality images in the PDF

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

# With local images (ReportLab version)
# 1. Place 1.png, 2.png, 3.png in the directory
# 2. Run the converter
./kibela2pdf "https://spikestudio.kibe.la/notes/12345" -o "document-with-images.pdf"
```

## Output Format

The generated PDF will include:
- ✅ Page title as H1 heading
- ✅ Proper heading hierarchy (H1, H2, H3, H4)
- ✅ Tables with borders and bold headers
- ✅ **Clickable links** (blue underlined text that opens URLs)
- ✅ **Real images** (from local PNG files when available)
- ✅ **Code blocks** with monospace formatting and grey backgrounds
- ✅ **Numbered lists** with proper sequential numbering
- ✅ Clean content without metadata
- ✅ Japanese font support
- ❌ No dates or timestamps
- ❌ No folder information
- ❌ No table of contents
- ❌ No comments
- ❌ No page numbers in footer
- ❌ No temp file paths

## Link Functionality

The ReportLab version provides full clickable link support:

- **Blue underlined text** - Links appear like traditional web links
- **Clickable functionality** - Click to open URLs in your browser
- **Table support** - Links in table cells are fully functional
- **Clean appearance** - No visible URLs cluttering the document
- **Cross-platform** - Works in all PDF viewers

## Troubleshooting

1. **API Authentication Error**: Ensure your `KIBELA_TOKEN` and `KIBELA_TEAM` environment variables are correctly set.

2. **Note Not Found**: Verify the Kibela URL is correct and you have access to the note.

3. **PDF Generation Error**: Make sure all dependencies are installed correctly, especially WeasyPrint.

4. **Font Issues**: The script uses Japanese-compatible fonts. If you encounter font rendering issues, ensure your system has the required fonts installed.

5. **Image Issues**: 
   - Ensure PNG files are named correctly (1.png, 2.png, 3.png)
   - Place images in the same directory as the script
   - Check that images are in PNG format

6. **Link Issues**: 
   - Links are only clickable in the ReportLab version
   - Ensure you're using a PDF viewer that supports link annotations

## Dependencies

### ReportLab Version (Recommended)
- `requests`: For API calls to Kibela
- `beautifulsoup4`: For HTML parsing and cleaning
- `reportlab`: For PDF generation with advanced features
- `pillow`: For image processing
- `html2text`: For text processing

### WeasyPrint Version
- `requests`: For API calls to Kibela
- `beautifulsoup4`: For HTML parsing and cleaning
- `weasyprint`: For PDF generation
- `html2text`: For text processing
- `lxml`: For XML/HTML parsing

## Version History

### Latest Version (ReportLab)
- ✅ Added clickable link support
- ✅ Added local image embedding (1.png, 2.png, 3.png)
- ✅ Enhanced code block formatting
- ✅ Improved table styling
- ✅ Better Japanese font support
- ✅ Professional PDF output with full interactivity

### Previous Version (WeasyPrint)
- Basic PDF generation
- Table and heading support
- Japanese font compatibility
