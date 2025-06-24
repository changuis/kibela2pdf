#!/usr/bin/env python3
"""
Kibela to PDF Converter

This script extracts content from Kibela pages and generates PDF files
with specific formatting requirements.
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
import weasyprint
from bs4 import BeautifulSoup
import html2text


class KibelaToPDFConverter:
    def __init__(self):
        self.kibela_token = os.getenv('KIBELA_TOKEN')
        self.kibela_team = os.getenv('KIBELA_TEAM')
        
        if not self.kibela_token or not self.kibela_team:
            raise ValueError("KIBELA_TOKEN and KIBELA_TEAM environment variables must be set")
        
        self.api_base_url = f"https://{self.kibela_team}.kibe.la/api/v1"
        self.headers = {
            'Authorization': f'Bearer {self.kibela_token}',
            'Content-Type': 'application/json'
        }

    def extract_note_id_from_url(self, url):
        """Extract note ID from Kibela URL"""
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            # Handle different URL formats
            if 'notes' in path_parts:
                note_index = path_parts.index('notes')
                if note_index + 1 < len(path_parts):
                    return path_parts[note_index + 1]
            
            # Try to extract from query parameters
            query_params = parse_qs(parsed_url.query)
            if 'id' in query_params:
                return query_params['id'][0]
                
            raise ValueError("Could not extract note ID from URL")
        except Exception as e:
            raise ValueError(f"Invalid Kibela URL format: {e}")

    def fetch_note_content(self, note_id):
        """Fetch note content from Kibela API"""
        query = """
        query($id: ID!) {
          note(id: $id) {
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
            groups {
              name
            }
            folders {
              fullName
            }
            comments {
              id
            }
          }
        }
        """
        
        variables = {"id": note_id}
        
        response = requests.post(
            f"{self.api_base_url}/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        data = response.json()
        
        if 'errors' in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        if not data.get('data', {}).get('note'):
            raise Exception("Note not found")
        
        return data['data']['note']

    def clean_html_content(self, html_content):
        """Clean and process HTML content according to requirements"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements (comments, metadata, etc.)
        for element in soup.find_all(['script', 'style', 'meta']):
            element.decompose()
        
        # Process tables - ensure they have borders and bold headers
        for table in soup.find_all('table'):
            table['style'] = 'border-collapse: collapse; width: 100%; margin: 1em 0;'
            
            # Add borders to all cells
            for cell in table.find_all(['td', 'th']):
                cell['style'] = 'border: 1px solid #333; padding: 8px; text-align: left;'
            
            # Make headers bold
            for header in table.find_all('th'):
                if 'style' in header:
                    header['style'] += ' font-weight: bold;'
                else:
                    header['style'] = 'font-weight: bold;'
            
            # If first row contains headers but uses td instead of th
            first_row = table.find('tr')
            if first_row:
                cells = first_row.find_all('td')
                if cells and not table.find('th'):
                    for cell in cells:
                        if 'style' in cell:
                            cell['style'] += ' font-weight: bold;'
                        else:
                            cell['style'] = 'font-weight: bold;'
        
        # Ensure proper heading hierarchy
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                heading['style'] = f'margin-top: 1.5em; margin-bottom: 0.5em;'
        
        return str(soup)

    def generate_html_template(self, title, content):
        """Generate HTML template for PDF conversion"""
        html_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-center {{
                content: "";
            }}
        }}
        
        body {{
            font-family: 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Noto Sans CJK JP', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
            margin: 0;
            padding: 0;
        }}
        
        h1 {{
            font-size: 2em;
            margin-bottom: 0.5em;
            margin-top: 0;
            border-bottom: 2px solid #333;
            padding-bottom: 0.3em;
        }}
        
        h2 {{
            font-size: 1.5em;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            border-bottom: 1px solid #666;
            padding-bottom: 0.2em;
        }}
        
        h3 {{
            font-size: 1.3em;
            margin-top: 1.3em;
            margin-bottom: 0.5em;
        }}
        
        h4 {{
            font-size: 1.1em;
            margin-top: 1.1em;
            margin-bottom: 0.5em;
        }}
        
        h5, h6 {{
            font-size: 1em;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }}
        
        p {{
            margin-bottom: 1em;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        
        th, td {{
            border: 1px solid #333;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            font-weight: bold;
            background-color: #f5f5f5;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
        }}
        
        ul, ol {{
            margin-bottom: 1em;
            padding-left: 2em;
        }}
        
        li {{
            margin-bottom: 0.5em;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {content}
</body>
</html>
"""
        return html_template

    def convert_to_pdf(self, note_data, output_path):
        """Convert note data to PDF"""
        title = note_data['title']
        content_html = note_data['contentHtml']
        
        # Clean and process the HTML content
        cleaned_content = self.clean_html_content(content_html)
        
        # Generate complete HTML
        html_content = self.generate_html_template(title, cleaned_content)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name
        
        try:
            # Convert HTML to PDF using WeasyPrint
            weasyprint.HTML(filename=temp_html_path).write_pdf(output_path)
            print(f"PDF generated successfully: {output_path}")
        finally:
            # Clean up temporary file
            os.unlink(temp_html_path)

    def process_kibela_url(self, url, output_path=None):
        """Main method to process Kibela URL and generate PDF"""
        try:
            # Extract note ID from URL
            note_id = self.extract_note_id_from_url(url)
            print(f"Extracted note ID: {note_id}")
            
            # Fetch note content
            print("Fetching note content from Kibela...")
            note_data = self.fetch_note_content(note_id)
            
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
    parser = argparse.ArgumentParser(description='Convert Kibela page to PDF')
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
