"""
Helper utilities
"""
from datetime import datetime
from flask import url_for


def generate_sitemap():
    """Generate dynamic sitemap.xml"""
    urls = [
        {'loc': '/', 'priority': '1.0'},
        {'loc': '/prices', 'priority': '0.9'},
        {'loc': '/about', 'priority': '0.7'},
        {'loc': '/contact', 'priority': '0.6'},
    ]
    
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>https://cloutscape.org{url["loc"]}</loc>\n'
        sitemap_xml += f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_xml += f'    <priority>{url["priority"]}</priority>\n'
        sitemap_xml += '  </url>\n'
    
    sitemap_xml += '</urlset>'
    
    return sitemap_xml


def format_gp(amount):
    """Format GP amount with commas"""
    return f"{amount:,}"


def format_usd(amount):
    """Format USD amount"""
    return f"${amount:.2f}"
