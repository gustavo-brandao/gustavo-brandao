"""Check generated images, links and data handling before publication."""
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import update_wakatime as waka


class ProfileChecks(unittest.TestCase):
    def test_readme_local_assets_exist(self):
        readme = (waka.ROOT / 'README.md').read_text(encoding='utf-8')
        for path in re.findall(r'(?:src|srcset)="(assets/[^\"]+)"', readme):
            self.assertTrue((waka.ROOT / path).is_file(), path)

    def test_svg_assets_are_self_contained(self):
        for path in (waka.ROOT / 'assets').glob('*.svg'):
            root = ET.parse(path).getroot()
            self.assertTrue(root.tag.endswith('svg'), path)
            for el in root.iter():
                self.assertFalse(el.tag.endswith('script'), path)
                for attr, value in el.attrib.items():
                    if attr.endswith('href'):
                        self.assertFalse(value.startswith(('http:', 'https:')), path)

    def test_no_fake_data_in_empty_state(self):
        panel = waka.render({}, 'Aguardando a primeira atualização.', True)
        self.assertNotIn('0.0%', panel)
        self.assertNotIn('0 h', panel)
        self.assertIn('Aguardando', panel)
        ET.fromstring(panel)

    def test_language_aggregates_and_escaping(self):
        payload = {'data': {'languages': [
            {'name': 'C#', 'total_seconds': 7200, 'percent': 80},
            {'name': 'Binary', 'total_seconds': 1000, 'percent': 10},
            {'name': '<HTML>', 'total_seconds': 600, 'percent': 8},
            {'name': 'CSS', 'total_seconds': 5, 'percent': 2}],
            'total_seconds': 8805}}
        data = waka.normalize(payload)
        self.assertEqual([x['name'] for x in data['languages']], ['C#','<HTML>'])
        self.assertEqual(data['languages'][0]['percent'], 80)
        animated = waka.render(data)
        ET.fromstring(animated)
        self.assertIn('&lt;HTML&gt;', animated)
        self.assertIn('2 h 00 min', animated)
        self.assertIn('<animate ', animated)
        self.assertNotIn('<animate ', waka.render(data, animated=False))

    def test_missing_credential_preserves_previous_data(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'assets').mkdir()
            original = 'prefix\n<!--START_SECTION:waka-->old<!--END_SECTION:waka-->\nsuffix'
            (root/'README.md').write_text(original, encoding='utf-8')
            cached = {'languages':[{'name':'C#','seconds':3600,'percent':100}], 'total_seconds':3600,'updated':'2026-10-31T00:00:00+00:00'}
            import json
            cache = root/'assets'/'wakatime-data.json'
            cache.write_text(json.dumps(cached), encoding='utf-8')
            with patch.object(waka,'ROOT',root), patch.object(waka,'ASSETS',root/'assets'), patch.object(waka,'CACHE',cache), patch.dict('os.environ', {'WAKATIME_API_KEY':''}), patch('sys.argv',['update_wakatime.py']):
                waka.main()
            text = (root/'README.md').read_text(encoding='utf-8')
            self.assertTrue(text.startswith('prefix'))
            self.assertTrue(text.endswith('suffix'))
            self.assertIn('C#',text)
            self.assertIn('2026-10-31',text)
            self.assertIn('precisa ser conectado',text)
            self.assertEqual(json.loads(cache.read_text()),cached)


if __name__ == '__main__':
    unittest.main()
