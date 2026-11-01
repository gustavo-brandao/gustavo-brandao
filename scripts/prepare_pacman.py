"""Apply the profile's blue palette and create a reduced-motion alternative."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = '{http://www.w3.org/2000/svg}'


def prepare():
    source = ROOT / 'dist' / 'pacman-contribution-graph-dark.svg'
    text = source.read_text(encoding='utf-8')
    for old,new in {'#161b22':'#212a34','#0e4429':'#1b3a50','#006d32':'#285f7d','#26a641':'#4e93b8','#39d353':'#7ab7d9'}.items():
        text = text.replace(old,new).replace(old.upper(),new)
    (ROOT / 'assets' / 'pacman.svg').write_text(text, encoding='utf-8')
    root = ET.fromstring(text)
    for parent in list(root.iter()):
        for child in list(parent):
            if child.tag in {SVG+'animate',SVG+'animateTransform',SVG+'animateMotion', SVG+'set'}:
                parent.remove(child)
            elif child.tag == SVG+'style':
                parent.remove(child)
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.ElementTree(root).write(ROOT / 'assets' / 'pacman-still.svg', encoding='utf-8', xml_declaration=False)


if __name__ == '__main__':
    prepare()
