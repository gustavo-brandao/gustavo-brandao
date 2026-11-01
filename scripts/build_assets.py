"""Build self-contained SVG assets using Python's standard library."""
import base64
import re
import struct
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'


def icon(name, x, y, size, color=None):
    source = (ASSETS / 'icons' / (name + '.svg')).read_text(encoding='utf-8')
    box = re.search(r'viewBox=[\"\']([^\"\']+)', source).group(1)
    body = re.sub(r'^.*?<svg\b[^>]*>', '', source, count=1, flags=re.S)
    body = re.sub(r'</svg>\s*$', '', body)
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{box}" fill="{color or "#7ab7d9"}">{body}</svg>'


def svg(width, height, label, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>{body}</svg>\n'


def build():
    # Embedded raster: no external SVG image requests, preserving GitHub compatibility.
    png = (ASSETS / 'banner.png').read_bytes()
    width, height = struct.unpack('>II', png[16:24])
    image = base64.b64encode(png).decode('ascii')
    body = f'<image width="{width}" height="{height}" xlink:href="data:image/png;base64,{image}"/>'
    body += f'''<defs><linearGradient id="light"><stop stop-color="#7ab7d9" stop-opacity="0"/><stop offset=".5" stop-color="#a6e2ff" stop-opacity=".3"/><stop offset="1" stop-color="#7ab7d9" stop-opacity="0"/></linearGradient><clipPath id="keyboard"><rect x="{width*.345}" y="{height*.755}" width="{width*.23}" height="{height*.12}"/></clipPath></defs>
<g clip-path="url(#keyboard)"><rect x="{width*.2}" y="{height*.755}" width="{width*.09}" height="{height*.12}" fill="url(#light)"><animate attributeName="x" values="{width*.2};{width*.62};{width*.62}" keyTimes="0;.6;1" dur="9s" repeatCount="indefinite"/></rect></g>
<rect x="{width*.505}" y="{height*.617}" width="{width*.004}" height="{height*.01}" fill="#9bd8ef"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.45;.5;1" dur="1.6s" repeatCount="indefinite"/></rect>'''
    (ASSETS / 'banner.svg').write_text(svg(width, height, 'Mesa de programação em pixel art com luz azul suave e cursor animado', body), encoding='utf-8')
    for name, label in [('linkedin','LinkedIn'), ('envelope','E-mail'), ('twitch','Twitch'), ('instagram','Instagram'), ('youtube','YouTube')]:
        body = '<rect x=".5" y=".5" width="117" height="35" rx="6" fill="#161b22" stroke="#3d5668"/>'
        body += icon(name, 12, 9, 18)
        body += f'<text x="39" y="23" fill="#e6edf3" font-family="Segoe UI,Arial,sans-serif" font-size="12">{label}</text>'
        (ASSETS / f'social-{name}.svg').write_text(svg(118,36,label,body), encoding='utf-8')
    primary = {'csharp':'C#', 'dotnet':'.NET', 'sqlserver':'SQL Server', 'azure':'Azure'}
    secondary = {'javascript':'JavaScript','html':'HTML','css':'CSS'}
    for name,label in {**primary, **secondary}.items():
        w,h,size = (112,84,40) if name in primary else (96,76,32)
        body = '<rect width="100%" height="100%" rx="6" fill="#0d1117"/>'
        body += icon(name, (w-size)/2, 8, size)
        body += f'<text x="{w/2}" y="{h-12}" text-anchor="middle" fill="#e6edf3" font-family="Segoe UI,Arial,sans-serif" font-size="13">{label}</text>'
        (ASSETS / f'tech-{name}.svg').write_text(svg(w,h,label,body), encoding='utf-8')
    for name,label,w in [('mysql','MySQL',100),('git','Git',72),('vite','Vite',76),('tailwind','Tailwind CSS',144)]:
        body = '<rect width="100%" height="100%" rx="5" fill="#161b22"/>' + icon(name,8,6,20)
        body += f'<text x="36" y="21" fill="#b7c6d1" font-family="Segoe UI,Arial,sans-serif" font-size="12">{label}</text>'
        (ASSETS / f'tool-{name}.svg').write_text(svg(w,32,label,body), encoding='utf-8')


if __name__ == '__main__':
    build()
