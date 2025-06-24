#!/usr/bin/env python3
"""
Kibela to PDF Converter (Alternative Implementation)

This script extracts content from Kibela pages and generates PDF files
using reportlab instead of WeasyPrint for better macOS compatibility.
"""

import os
import sys
import json
import requests
import argparse
from urllib.parse import urlparse, parse_qs
import re
from datetime import datetime
import tempfile
from bs4 import BeautifulSoup
import html2text
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
import html
import urllib.request
import urllib.parse
from PIL import Image as PILImage
import io


class LinkFlowable(Flowable):
    """Custom flowable for creating clickable links"""
    def __init__(self, text, url, style):
        Flowable.__init__(self)
        self.text = text
        self.url = url
        self.style = style
        # Calculate dimensions
        from reportlab.pdfbase.pdfmetrics import stringWidth
        self.width = stringWidth(text, style.fontName, style.fontSize)
        self.height = style.fontSize

    def draw(self):
        # Draw the text in blue
        self.canv.setFillColor(colors.blue)
        self.canv.setFont(self.style.fontName, self.style.fontSize)
        self.canv.drawString(0, 0, self.text)
        
        # Add link annotation
        self.canv.linkURL(self.url, (0, 0, self.width, self.height))


class KibelaToPDFConverter:
    def __init__(self):
        self.kibela_token = os.getenv('KIBELA_TOKEN')
        self.kibela_team = os.getenv('KIBELA_TEAM')
        
        if not self.kibela_token or not self.kibela_team:
            raise ValueError("KIBELA_TOKEN and KIBELA_TEAM environment variables must be set")
        
        self.api_base_url = f"https://{self.kibela_team}.kibe.la/api/v1"
        self.headers = {
            'Authorization': f'Bearer {self.kibela_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'KibelaToPDFConverter/1.0'
        }
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom paragraph styles with Japanese font support"""
        # Register Japanese fonts
        try:
            # Try to register HeiseiMin-W3 (built-in Japanese font in ReportLab)
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
            japanese_font = 'HeiseiMin-W3'
            japanese_font_bold = 'HeiseiMin-W3'
        except:
            try:
                # Fallback to HeiseiKakuGo-W5 (another built-in Japanese font)
                pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
                japanese_font = 'HeiseiKakuGo-W5'
                japanese_font_bold = 'HeiseiKakuGo-W5'
            except:
                # Final fallback to Helvetica (will show garbled text but won't crash)
                japanese_font = 'Helvetica'
                japanese_font_bold = 'Helvetica-Bold'
                print("Warning: Japanese fonts not available, text may appear garbled")
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            spaceBefore=0,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName=japanese_font_bold
        ))
        
        # Heading styles
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=18,
            textColor=colors.black,
            fontName=japanese_font_bold
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.black,
            fontName=japanese_font_bold
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.black,
            fontName=japanese_font_bold
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading4',
            parent=self.styles['Heading4'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=10,
            textColor=colors.black,
            fontName=japanese_font_bold
        ))
        
        # Update Normal style for Japanese text
        self.styles['Normal'].fontName = japanese_font
        
        # Add custom code style
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Courier',
            backgroundColor=colors.lightgrey,
            leftIndent=12,
            rightIndent=12,
            spaceAfter=6,
            spaceBefore=6,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=6
        ))
        
        # Store font names for table use
        self.japanese_font = japanese_font
        self.japanese_font_bold = japanese_font_bold

    def extract_note_id_from_url(self, url):
        """Extract note ID from Kibela URL"""
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            # Handle different URL formats
            if 'notes' in path_parts:
                note_index = path_parts.index('notes')
                if note_index + 1 < len(path_parts):
                    note_id = path_parts[note_index + 1]
                    return note_id
            
            # Try to extract from query parameters
            query_params = parse_qs(parsed_url.query)
            if 'id' in query_params:
                note_id = query_params['id'][0]
                return note_id
            
            # Handle URLs like https://team.kibe.la/12345
            if len(path_parts) >= 1 and path_parts[0] and path_parts[0].isdigit():
                note_id = path_parts[0]
                return note_id
                
            raise ValueError("Could not extract note ID from URL")
        except Exception as e:
            raise ValueError(f"Invalid Kibela URL format: {e}")

    def fetch_note_content(self, note_url):
        """Fetch note content from Kibela API"""
        # First, get the proper note ID using noteFromPath
        query = """
        query($path: String!) {
          noteFromPath(path: $path) {
            id
            title
            content
            contentHtml
            publishedAt
            updatedAt
            author {
              account
              realName
            }
          }
        }
        """
        
        variables = {"path": note_url}
        
        
        response = requests.post(
            self.api_base_url,
            headers=self.headers,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
        
        if 'errors' in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        if not data.get('data', {}).get('noteFromPath'):
            raise Exception("Note not found in response")
        
        return data['data']['noteFromPath']

    def clean_text(self, text):
        """Clean text for PDF generation"""
        if not text:
            return ""
        # Unescape HTML entities
        text = html.unescape(text)
        # Remove zero-width characters and other problematic Unicode characters
        text = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f\ufeff]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def process_element_with_links(self, element):
        """Process element content while preserving links as separate flowables"""
        elements = []
        
        # Check if this element contains links
        links = element.find_all('a')
        if not links:
            # No links, just return regular text
            text = self.clean_text(element.get_text())
            if text:
                return [Paragraph(text, self.styles['Normal'])]
            return []
        
        # Process mixed content with links
        current_text = ""
        
        for child in element.children:
            if hasattr(child, 'name'):
                if child.name == 'a':
                    # Add any accumulated text before the link
                    if current_text.strip():
                        elements.append(Paragraph(self.clean_text(current_text), self.styles['Normal']))
                        current_text = ""
                    
                    # Create link flowable
                    link_text = self.clean_text(child.get_text())
                    link_url = child.get('href', '')
                    if link_text and link_url:
                        elements.append(LinkFlowable(link_text, link_url, self.styles['Normal']))
                    elif link_text:
                        elements.append(Paragraph(link_text, self.styles['Normal']))
                else:
                    # Other HTML elements, accumulate text
                    current_text += self.clean_text(child.get_text())
            else:
                # Text node, accumulate
                current_text += self.clean_text(str(child))
        
        # Add any remaining text
        if current_text.strip():
            elements.append(Paragraph(self.clean_text(current_text), self.styles['Normal']))
        
        return elements

    def process_text_with_links(self, element):
        """Process text content while preserving links (for table cells)"""
        result = []
        
        # Process all child nodes
        for child in element.children:
            if hasattr(child, 'name'):
                if child.name == 'a':
                    # This is a link
                    link_text = self.clean_text(child.get_text())
                    link_url = child.get('href', '')
                    if link_text and link_url:
                        # Create a Paragraph with clickable link for table cells
                        return Paragraph(f'<a href="{link_url}" color="blue"><u>{link_text}</u></a>', self.styles['Normal'])
                    elif link_text:
                        result.append(link_text)
                else:
                    # Other HTML elements, just get text
                    result.append(self.clean_text(child.get_text()))
            else:
                # Text node
                result.append(self.clean_text(str(child)))
        
        return ''.join(result)

    def download_image(self, img_url, image_counter=None):
        """Download image and return ReportLab Image object"""
        try:
            # Check if we should use local PNG files instead of processing the URL
            if image_counter is not None:
                local_png_path = f"{image_counter}.png"
                if os.path.exists(local_png_path):
                    print(f"Using local PNG file: {local_png_path}")
                    
                    # Load the local PNG file
                    pil_img = PILImage.open(local_png_path)
                    
                    # Convert to RGB if necessary (for RGBA, P mode images)
                    if pil_img.mode in ('RGBA', 'P'):
                        pil_img = pil_img.convert('RGB')
                    
                    # Save to bytes as JPEG
                    img_buffer = io.BytesIO()
                    pil_img.save(img_buffer, format='JPEG', quality=85)
                    img_buffer.seek(0)
                    
                    # Create ReportLab Image from the buffer
                    img = Image(img_buffer)
                    
                    # Scale image to fit page width (max 400 points)
                    max_width = 400
                    max_height = 300
                    
                    # Get original dimensions
                    orig_width, orig_height = pil_img.size
                    
                    # Calculate scaling factor
                    scale_w = max_width / orig_width if orig_width > max_width else 1
                    scale_h = max_height / orig_height if orig_height > max_height else 1
                    scale = min(scale_w, scale_h)
                    
                    img.drawWidth = orig_width * scale
                    img.drawHeight = orig_height * scale
                    
                    print(f"Successfully processed local image: {orig_width}x{orig_height} -> {img.drawWidth:.0f}x{img.drawHeight:.0f}")
                    return img
            
            # Fallback to original logic if no local file found
            is_svg = False
            
            # Handle data URLs (base64 encoded images)
            if img_url.startswith('data:'):
                import base64
                # Extract the base64 data
                if ';base64,' in img_url:
                    header, data = img_url.split(';base64,')
                    # Check if it's an SVG
                    if 'svg' in header.lower():
                        is_svg = True
                    img_data = base64.b64decode(data)
                else:
                    print(f"Warning: Unsupported data URL format: {img_url[:50]}...")
                    return Paragraph(f"[Image: data URL]", self.styles['Normal'])
            else:
                # Handle relative URLs
                if img_url.startswith('/'):
                    img_url = f"https://{self.kibela_team}.kibe.la{img_url}"
                elif not img_url.startswith('http'):
                    img_url = f"https://{self.kibela_team}.kibe.la/{img_url}"
                
                # Check if it's an SVG file
                if img_url.lower().endswith('.svg'):
                    is_svg = True
                
                # Add authorization headers for Kibela images
                req = urllib.request.Request(img_url)
                req.add_header('Authorization', f'Bearer {self.kibela_token}')
                req.add_header('User-Agent', 'KibelaToPDFConverter/1.0')
                
                # Create SSL context that doesn't verify certificates (for development)
                import ssl
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    img_data = response.read()
            
            # Handle SVG files
            if is_svg:
                try:
                    import cairosvg
                    # Convert SVG to PNG with white background to handle transparency
                    png_data = cairosvg.svg2png(bytestring=img_data, background_color='white')
                    img_data = png_data
                    print(f"Successfully converted SVG to PNG: {img_url[:50]}...")
                except ImportError:
                    print(f"Warning: cairosvg not available, skipping SVG: {img_url[:50]}...")
                    return Paragraph("📷 [SVG Image - cairosvg not installed]", self.styles['Normal'])
                except Exception as e:
                    print(f"Warning: Could not convert SVG: {e}")
                    return Paragraph("📷 [SVG Image - conversion failed]", self.styles['Normal'])
            
            # Create PIL Image to get dimensions and convert if needed
            pil_img = PILImage.open(io.BytesIO(img_data))
            
            # Skip very small images (likely placeholders)
            if pil_img.size[0] < 10 or pil_img.size[1] < 10:
                return Paragraph("[Small placeholder image]", self.styles['Normal'])
            
            # Convert to RGB if necessary (for RGBA, P mode images)
            if pil_img.mode in ('RGBA', 'P'):
                pil_img = pil_img.convert('RGB')
            
            # Save to bytes as JPEG
            img_buffer = io.BytesIO()
            pil_img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # Create ReportLab Image from the buffer
            img = Image(img_buffer)
            
            # Scale image to fit page width (max 400 points)
            max_width = 400
            max_height = 300
            
            # Get original dimensions
            orig_width, orig_height = pil_img.size
            
            # Calculate scaling factor
            scale_w = max_width / orig_width if orig_width > max_width else 1
            scale_h = max_height / orig_height if orig_height > max_height else 1
            scale = min(scale_w, scale_h)
            
            img.drawWidth = orig_width * scale
            img.drawHeight = orig_height * scale
            
            print(f"Successfully processed image: {orig_width}x{orig_height} -> {img.drawWidth:.0f}x{img.drawHeight:.0f}")
            return img
            
        except Exception as e:
            print(f"Warning: Could not process image {img_url[:50]}...: {e}")
            # Return a placeholder text instead
            return Paragraph(f"[Image could not be loaded]", self.styles['Normal'])

    def parse_html_to_elements(self, html_content):
        """Parse HTML content and convert to ReportLab elements"""
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = []
        image_counter = 1  # Counter for local PNG files
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'meta']):
            element.decompose()
        
        for element in soup.find_all(True):
            if element.name == 'h1':
                text = self.clean_text(element.get_text())
                if text:
                    elements.append(Paragraph(text, self.styles['CustomHeading1']))
                    elements.append(Spacer(1, 6))
            
            elif element.name == 'h2':
                text = self.clean_text(element.get_text())
                if text:
                    elements.append(Paragraph(text, self.styles['CustomHeading2']))
                    elements.append(Spacer(1, 6))
            
            elif element.name == 'h3':
                text = self.clean_text(element.get_text())
                if text:
                    elements.append(Paragraph(text, self.styles['CustomHeading3']))
                    elements.append(Spacer(1, 6))
            
            elif element.name == 'h4':
                text = self.clean_text(element.get_text())
                if text:
                    elements.append(Paragraph(text, self.styles['CustomHeading4']))
                    elements.append(Spacer(1, 6))
            
            elif element.name == 'p':
                # Process paragraph with potential links
                text_with_links = self.process_text_with_links(element)
                if text_with_links:
                    elements.append(Paragraph(text_with_links, self.styles['Normal']))
                    elements.append(Spacer(1, 6))
            
            elif element.name == 'img':
                img_src = element.get('src')
                if img_src:
                    img_element = self.download_image(img_src, image_counter)
                    elements.append(img_element)
                    elements.append(Spacer(1, 6))
                    image_counter += 1  # Increment for next image
            
            elif element.name in ['pre', 'code']:
                code_text = element.get_text()
                if code_text:
                    # Use Preformatted for code blocks to preserve formatting
                    elements.append(Preformatted(code_text, self.styles['CustomCode']))
                    elements.append(Spacer(1, 6))
            
            elif element.name == 'table':
                table_data = self.parse_table(element)
                if table_data:
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), self.japanese_font_bold),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), self.japanese_font),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 12))
            
            elif element.name in ['ul', 'ol']:
                counter = 1
                for li in element.find_all('li', recursive=False):
                    text = self.clean_text(li.get_text())
                    if text:
                        if element.name == 'ul':
                            bullet = "• "
                        else:
                            bullet = f"{counter}. "
                            counter += 1
                        elements.append(Paragraph(f"{bullet}{text}", self.styles['Normal']))
                        elements.append(Spacer(1, 3))
                elements.append(Spacer(1, 6))
        
        return elements

    def parse_table(self, table_element):
        """Parse HTML table to data structure for ReportLab"""
        rows = []
        
        # Get all rows
        for tr in table_element.find_all('tr'):
            row = []
            for cell in tr.find_all(['td', 'th']):
                # Process cell content with potential links
                cell_content = self.process_text_with_links(cell)
                if not cell_content:
                    cell_content = self.clean_text(cell.get_text())
                row.append(cell_content)
            if row:  # Only add non-empty rows
                rows.append(row)
        
        return rows if rows else None

    def convert_to_pdf(self, note_data, output_path):
        """Convert note data to PDF using ReportLab"""
        title = note_data['title']
        content_html = note_data['contentHtml']
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Add title
        story.append(Paragraph(self.clean_text(title), self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Parse and add content
        content_elements = self.parse_html_to_elements(content_html)
        story.extend(content_elements)
        
        # Build PDF
        doc.build(story)
        print(f"PDF generated successfully: {output_path}")

    def process_kibela_url(self, url, output_path=None):
        """Main method to process Kibela URL and generate PDF"""
        try:
            # Extract note ID from URL for logging
            note_id = self.extract_note_id_from_url(url)
            print(f"Extracted note ID: {note_id}")
            
            # Fetch note content using full URL
            print("Fetching note content from Kibela...")
            note_data = self.fetch_note_content(url)
            
            # Generate output filename if not provided
            if not output_path:
                safe_title = re.sub(r'[^\w\s-]', '', note_data['title'])
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                output_path = f"{safe_title}.pdf"
            
            # Convert to PDF
            print("Converting to PDF...")
            self.convert_to_pdf(note_data, output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Convert Kibela page to PDF (Alternative Implementation)')
    parser.add_argument('url', help='Kibela page URL')
    parser.add_argument('-o', '--output', help='Output PDF file path')
    
    args = parser.parse_args()
    
    try:
        converter = KibelaToPDFConverter()
        output_path = converter.process_kibela_url(args.url, args.output)
        print(f"Successfully converted Kibela page to PDF: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
