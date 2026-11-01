"""Build self-contained SVG assets using Python's standard library."""
import base64
import re
import struct
import xml.etree.ElementTree as ET
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


def mono_icon(name, x, y, size):
    if name == 'dotnet':
        return f'<text x="{x+size/2}" y="{y+size*.72}" text-anchor="middle" fill="#7ab7d9" font-family="Segoe UI,Arial,sans-serif" font-size="{size*.51}" font-weight="650">.NET</text>'
    root = ET.fromstring((ASSETS / 'icons' / (name+'.svg')).read_text(encoding='utf-8'))
    # Preserve negative spaces while replacing brand colors with the profile palette.
    negative = {'#fff','#ffffff','#ebebeb','#323330','#000','#000000','black','white'}
    for parent in list(root.iter()):
        for child in list(parent):
            if child.tag.endswith('defs') or (name == 'azure' and child.get('fill') == 'url(#azure-original-b)'):
                parent.remove(child)
    for el in root.iter():
        for attr in ['fill','stroke']:
            value = el.get(attr)
            if value and value != 'none':
                el.set(attr, '#0d1117' if value.lower() in negative else '#7ab7d9')
        if el.tag.endswith('path') and 'fill' not in el.attrib:
            el.set('fill', '#7ab7d9')
    if name == 'vite':
        paths = [el for el in root.iter() if el.tag.endswith('path')]
        if len(paths) > 1:
            paths[-1].set('fill','#0d1117')
    root.set('x',str(x)); root.set('y',str(y))
    root.set('width',str(size)); root.set('height',str(size))
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    return ET.tostring(root, encoding='unicode')


def tile(name, label, width, height, size, filename):
    body = f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="7" fill="#0d1117" stroke="#2b4556"/>'
    body += mono_icon(name,(width-size)/2,14,size)
    body += f'<text x="{width/2}" y="{height-15}" text-anchor="middle" fill="#e6edf3" font-family="Segoe UI,Arial,sans-serif" font-size="14">{label}</text>'
    (ASSETS / filename).write_text(svg(width,height,label,body),encoding='utf-8')


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
    secondary = {'javascript':'JavaScript','html':'HTML','css':'CSS','php':'PHP'}
    for name,label in {**primary, **secondary}.items():
        w,h,size = (148,112,52) if name in primary else (128,100,44)
        tile(name,label,w,h,size,f'tech-{name}-mono.svg')
    for name,label,w in [('mysql','MySQL',100),('git','Git',72),('tailwind','Tailwind CSS',144)]:
        tile(name,label,124,86,32,f'tool-{name}-mono.svg')


if __name__ == '__main__':
    build()
