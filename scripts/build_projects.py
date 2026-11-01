"""Render approved project illustrations and cards as local vector assets."""
from html import escape
from pathlib import Path
from build_assets import svg

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'


def illustration(kind):
    prefix = '<rect x=".5" y=".5" width="179" height="109" rx="6" fill="#0d1117" stroke="#3c627b"/>'
    if kind == 'architecture':
        grid = ''.join(f'<path d="M{x} 1v108"/>' for x in range(12,180,14))
        grid += ''.join(f'<path d="M1 {y}h178"/>' for y in range(12,110,14))
        return prefix + f'<g stroke="#233b4b" stroke-width=".65">{grid}</g>' + '''<g fill="none" stroke="#7ab7d9" stroke-width="1.5" stroke-linejoin="round"><path d="m24 42 72-24 55 21-72 22zM28 45v44l51 15 68-23V41M79 61v43M28 68l51 16 68-24M28 88l51 16 68-23M40 49v20m19-14v20m34-18v20m20-27v21m20-28v22M40 76v16m19-10v16m34-18v19m20-26v19m20-26v19"/><path d="m132 96 35-35v35zm10-7h17V72z" fill="#0d1117"/><path d="M17 96h9m-4-2V78m0 0c-13-1-12-16-3-17-1-9 12-11 14-3 12 0 13 16 1 19"/></g>'''
    if kind == 'calculator':
        return prefix + '''<g stroke="#7ab7d9" fill="none" stroke-width="1.6"><rect x="10" y="12" width="107" height="84" rx="4"/><path d="M10 29h107M139 22v14m-7-7h14M132 47l13 13m0-13-13 13M132 76h15"/></g><g fill="#7ab7d9"><circle cx="19" cy="21" r="2"/><circle cx="27" cy="21" r="2"/><circle cx="35" cy="21" r="2"/><circle cx="139" cy="71" r="1.5"/><circle cx="139" cy="81" r="1.5"/><path d="m151 76 18 10v20l-18 10-18-10V86z" transform="translate(0 -7)"/></g><text x="22" y="53" fill="#e6edf3" font-family="Consolas,monospace" font-size="16">2 + 2 = 4</text><text x="22" y="79" fill="#7ab7d9" font-family="Consolas,monospace" font-size="18">&gt;_</text><text x="151" y="96" text-anchor="middle" fill="#0d1117" font-family="Segoe UI,Arial,sans-serif" font-size="16" font-weight="700">C#</text>'''
    return prefix + '''<g fill="none" stroke="#7ab7d9" stroke-width="1.6" stroke-linejoin="round"><path d="M13 24q32-13 55 4v66Q43 78 13 90zM68 28q23-17 50-7v66q-27-8-50 7M8 29v67q34-11 60 5 26-15 55-8V26M21 35q20-7 37 4M21 46q20-7 37 4M21 57q20-7 37 4M21 68q20-7 37 4"/><rect x="87" y="21" width="83" height="67" rx="4" fill="#0d1117"/><path d="M87 34h83m-58 15-12 11 12 11m32-22 12 11-12 11m-12-26-9 31"/></g><g fill="#7ab7d9"><circle cx="95" cy="28" r="1.5"/><circle cx="101" cy="28" r="1.5"/><circle cx="107" cy="28" r="1.5"/></g>'''


PROJECTS = [
    ('landing-karina-ramai','architecture','Site institucional e portfólio de arquitetura.','HTML · CSS · JavaScript · Vite · Tailwind CSS', ['Site institucional e portfólio','de arquitetura.']),
    ('calculadora-csharp','calculator','Calculadora de console para praticar C# e .NET.','C# · .NET',['Calculadora de console para','praticar C# e .NET.']),
    ('clone-tabnews','course','Estudo do curso.dev, inspirado no TabNews.','React · Next.js',['Estudo do curso.dev,','inspirado no TabNews.']),
]


def card(name, kind, description, tech, mobile=False, lines=None):
    w,h = (480,248) if mobile else (900,156)
    body = f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="9" fill="#0d1117" stroke="#2b4556" stroke-width="1.5"/>'
    if mobile:
        body += f'<g transform="translate(16 18) scale(.62)">{illustration(kind)}</g>'
        body += f'<g font-family="Segoe UI,Arial,sans-serif"><text x="144" y="46" fill="#e6edf3" font-size="21" font-weight="600">{escape(name)}</text>'
        for i,line in enumerate(lines):
            body += f'<text x="20" y="{122+i*24}" fill="#b7c6d1" font-size="17">{escape(line)}</text>'
        tech_lines = ['HTML · CSS · JavaScript','Vite · Tailwind CSS'] if kind == 'architecture' else [tech]
        for i,line in enumerate(tech_lines):
            body += f'<text x="20" y="{184+i*21}" fill="#7ab7d9" font-size="14">{escape(line)}</text>'
        body += '<text x="460" y="230" text-anchor="end" fill="#7ab7d9" font-size="14">Ver código ↗</text></g>'
    else:
        body += f'<g transform="translate(18 23)">{illustration(kind)}</g>'
        body += f'<g font-family="Segoe UI,Arial,sans-serif"><text x="224" y="43" fill="#e6edf3" font-size="23" font-weight="600">{escape(name)}</text><text x="224" y="76" fill="#b7c6d1" font-size="16">{escape(description)}</text><text x="224" y="109" fill="#7ab7d9" font-size="14">{escape(tech)}</text><text x="878" y="135" text-anchor="end" fill="#7ab7d9" font-size="14">Ver código ↗</text></g>'
    return svg(w,h,name+' — '+description+' '+tech,body)


def build():
    for name,kind,description,tech,lines in PROJECTS:
        for mobile in [False,True]:
            filename = f'project-{name}'+('-mobile' if mobile else '')+'.svg'
            (ASSETS/filename).write_text(card(name,kind,description,tech,mobile,lines),encoding='utf-8')


if __name__ == '__main__':
    build()
