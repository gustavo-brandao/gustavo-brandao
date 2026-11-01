"""Fetch only language aggregates; render a quiet animated panel without dependencies."""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
CACHE = ASSETS / 'wakatime-data.json'
IGNORED = {'Binary', 'Other'}


def format_time(seconds):
    minutes = int(seconds // 60)
    return f'{minutes // 60} h {minutes % 60:02d} min' if minutes >= 60 else f'{minutes} min'


def normalize(payload):
    data = payload.get('data', {})
    languages = []
    for item in data.get('languages', []):
        name = str(item.get('name', 'Outros'))[:50]
        seconds = float(item.get('total_seconds', 0))
        percent = float(item.get('percent', 0))
        if name in IGNORED or seconds < 60:
            continue
        languages.append({'name': name, 'seconds': max(0, seconds), 'percent': max(0, min(100, percent))})
    languages.sort(key=lambda x: x['seconds'], reverse=True)
    return {'languages': languages[:5], 'total_seconds': float(data.get('total_seconds', 0)),
            'start': str(data.get('start', ''))[:10], 'end': str(data.get('end', ''))[:10],
            'updated': datetime.now(timezone.utc).isoformat(timespec='seconds')}


def render(data, status=None, animated=True):
    rows = data.get('languages', [])
    h = 112 + max(1, len(rows)) * 36
    title = 'Tempo de código · WakaTime'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" viewBox="0 0 900 {h}" role="img" aria-label="{title}">', f'<title>{title}</title>',
             '<defs><linearGradient id="edge"><stop stop-color="#30363d"/><stop offset=".5" stop-color="#7ab7d9"/><stop offset="1" stop-color="#30363d"/></linearGradient><linearGradient id="sheen"><stop stop-color="#d5f3ff" stop-opacity="0"/><stop offset=".5" stop-color="#d5f3ff" stop-opacity=".35"/><stop offset="1" stop-color="#d5f3ff" stop-opacity="0"/></linearGradient><pattern id="segments" width="12" height="14" patternUnits="userSpaceOnUse"><rect width="10" height="14" fill="#7ab7d9"/></pattern></defs>',
             f'<rect x="1" y="1" width="898" height="{h-2}" rx="9" fill="#0d1117" stroke="url(#edge)"/>',
             '<g font-family="Segoe UI,Arial,sans-serif">',
             f'<text x="24" y="32" fill="#e6edf3" font-size="18" font-weight="600">{title}</text>',
             '<text x="876" y="32" text-anchor="end" fill="#8b949e" font-size="12">Últimos 7 dias</text>']
    for i, row in enumerate(rows):
        y = 60 + i * 36
        filled = round(440 * row['percent'] / 100, 2)
        parts += [f'<text x="24" y="{y+12}" fill="#c9d1d9" font-size="14">{escape(row["name"])}</text>',
                  f'<rect x="180" y="{y}" width="440" height="14" rx="2" fill="#212a34"/>',
                  f'<rect x="180" y="{y}" width="{filled}" height="14" fill="url(#segments)"/>',
                  f'<text x="770" y="{y+12}" text-anchor="end" fill="#c9d1d9" font-size="13">{format_time(row["seconds"])}</text>',
                  f'<text x="876" y="{y+12}" text-anchor="end" fill="#7ab7d9" font-size="13">{row["percent"]:.1f}%</text>']
        if animated and filled:
            parts += [f'<clipPath id="bar{i}"><rect x="180" y="{y}" width="{filled}" height="14"/></clipPath>',
                      f'<g clip-path="url(#bar{i})"><rect x="100" y="{y}" width="65" height="14" fill="url(#sheen)"><animate attributeName="x" values="100;660;660" keyTimes="0;.55;1" dur="12s" begin="{i*.3}s" repeatCount="indefinite"/></rect></g>']
    if not rows:
        msg = status or 'Nenhuma atividade registrada neste período.'
        parts.append(f'<text x="24" y="76" fill="#8b949e" font-size="14">{escape(msg)}</text>')
    if data.get('updated'):
        stamp = data['updated'][:10]
        footer = f'Total registrado: {format_time(data.get("total_seconds",0))} · Atualizado em {stamp} (UTC)'
    else:
        footer = 'Aguardando a primeira atualização · sem valores simulados'
    parts.append(f'<text x="24" y="{h-22}" fill="#8b949e" font-size="11">{escape(footer)}</text>')
    if status and rows:
        parts.append(f'<text x="24" y="{h-42}" fill="#c9a86a" font-size="11">{escape(status)}</text>')
    parts += ['</g></svg>\n']
    return ''.join(parts)


def update_readme(data, status):
    rows = data.get('languages', [])
    lines = ['```text', 'Últimos 7 dias']
    if data.get('updated'):
        lines.append(f'Atualizado em {data["updated"][:10]} (UTC)')
    if rows:
        lines += [f'{r["name"]:<16} {format_time(r["seconds"]):>12} {r["percent"]:>6.1f}%' for r in rows]
        lines.append(f'Total registrado: {format_time(data.get("total_seconds",0))}')
    else:
        lines.append(status or 'Nenhuma atividade registrada neste período.')
    if status and rows:
        lines.append(status)
    lines.append('```')
    path = ROOT / 'README.md'
    old = path.read_text(encoding='utf-8')
    new = re.sub(r'(?<=<!--START_SECTION:waka-->)\s*.*?\s*(?=<!--END_SECTION:waka-->)', '\n\n'+'\n'.join(lines)+'\n\n', old, flags=re.S)
    path.write_text(new, encoding='utf-8')


def main():
    token = os.getenv('WAKATIME_API_KEY', '').strip()
    status = None
    data = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    ok = True
    if '--placeholder' in sys.argv:
        status = 'Aguardando a primeira atualização automática.'
    elif not token:
        status = 'WakaTime precisa ser conectado para atualizar os tempos.'
        ok = False
    else:
        request = urllib.request.Request('https://wakatime.com/api/v1/users/current/stats/last_7_days',
            headers={'Authorization': 'Basic '+base64.b64encode(token.encode()).decode(), 'User-Agent': 'gustavo-brandao-profile'})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise ValueError('Estatísticas ainda não disponíveis')
                data = normalize(json.load(response))
            CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        except (urllib.error.URLError, ValueError, KeyError, TypeError) as exc:
            status = 'Não foi possível atualizar agora; consulte a data da última coleta.' if data else 'WakaTime indisponível; verifique a conexão nas configurações do repositório.'
            # Do not print HTTP request URLs, headers, response bodies or credentials.
            print('WakaTime: atualização indisponível; dados anteriores preservados.')
            ok = False
    for animated, name in [(True,'wakatime.svg'), (False,'wakatime-still.svg')]:
        (ASSETS / name).write_text(render(data,status,animated), encoding='utf-8')
    update_readme(data, status)
    if not ok:
        print('::warning::WakaTime não atualizou. Confira a mensagem do painel e a credencial WAKATIME_API_KEY.')


if __name__ == '__main__':
    main()
