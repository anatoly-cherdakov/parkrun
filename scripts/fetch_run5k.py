#!/usr/bin/env python3
"""Refresh the public run5k snapshot used by the GitHub Pages button."""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = 'https://run5k.run/api/users/293/profile/runs'
results = []
offset = 0
while True:
    request = urllib.request.Request(
        f'{URL}?limit=200&offset={offset}',
        headers={'User-Agent': 'Mozilla/5.0 (compatible; results-refresh/1.0)'},
    )
    with urllib.request.urlopen(request, timeout=35) as response:
        batch = json.load(response)
    if not isinstance(batch, list):
        raise ValueError('run5k вернул неожиданный формат')
    for r in batch:
        if not isinstance(r, dict) or not r.get('event_date') or not r.get('finish_time_display'):
            raise ValueError('run5k вернул неполный результат')
        results.append({
            k: r.get(k) for k in
            ('event_date', 'location_name', 'location_city',
             'location_country', 'platform_code', 'finish_time_display')
        })
    if len(batch) < 200:
        break
    offset += len(batch)
    if offset > 10000:
        raise ValueError('Слишком много страниц результатов')

if not results:
    raise ValueError('Пустой ответ run5k: существующий файл не изменён')
destination = ROOT / 'run5k-results.json'
temporary = destination.with_suffix('.json.tmp')
temporary.write_text(
    json.dumps({'runs': results}, ensure_ascii=False, separators=(',', ':')) + '\n',
    encoding='utf-8',
)
temporary.replace(destination)
print(f'Сохранено результатов: {len(results)}')
