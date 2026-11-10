"""Draft asset proposal is additive and cannot claim UCKK rights/acceptance."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

from kolor_studio_core import process_sheet, choose_variant, export_kontexte, creative_asset_candidates


class CreativeCandidateTests(unittest.TestCase):
    def test_proposed_index_hashes_exact_exported_files(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            sheet = Image.new('RGB', (400, 400), 'white')
            draw = ImageDraw.Draw(sheet)
            for x in (0, 200):
                for y in (0, 200):
                    draw.rectangle((x + 50, y + 50, x + 150, y + 150), fill='#FFFF00')
            source = project / 'source.png'
            sheet.save(source)
            process_sheet(project, 'pecheur', source)
            choose_variant(project, 'pecheur', 0, validate=True)
            export_kontexte(project)
            root = project / 'exports'
            old = json.loads((root / 'manifest.json').read_text('utf8'))
            self.assertEqual('kolor.studio.export/1', old['format'])
            index = json.loads((root / 'creative-candidates.json').read_text('utf8'))
            self.assertEqual('koa.creative-asset-candidates/draft-1', index['format'])
            self.assertEqual('Kolor', index['producer'])
            self.assertEqual('candidate', index['status'])
            self.assertEqual(1, len(index['items']))
            item = index['items'][0]
            self.assertEqual('kolor:role-pecheur', item['source_id'])
            self.assertEqual('reviewed', item['studio_review'])
            self.assertEqual('pending', item['uckk_review'])
            self.assertEqual({'status': 'unverified', 'license': None, 'attribution': None}, item['rights'])
            for file in item['files']:
                content = (root / file['path']).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), file['sha256'])
            self.assertEqual(2, len(item['files']))

    def test_unreviewed_role_never_becomes_uckk_approved(self):
        with tempfile.TemporaryDirectory() as directory:
            exports = Path(directory)
            relative = Path('images/roles/pecheur.png')
            (exports / relative).parent.mkdir(parents=True)
            (exports / relative).write_bytes(b'candidate png')
            native = Path('images/roles_natifs/pecheur.png')
            (exports / native).parent.mkdir(parents=True)
            (exports / native).write_bytes(b'native png')
            records = [{'visual_id': 'role-pecheur', 'chemin': str(relative),
                        'chemin_natif': str(native), 'statut': 'a_verifier',
                        'variante': 1, 'palette_id': 'pastel', 'skin_tone_id': 'bronze'}]
            catalogue = [{'id': 'pecheur', 'nom': 'Pêcheur', 'visual_id': 'role-pecheur'}]
            result = creative_asset_candidates(exports, records, catalogue)
            self.assertEqual('not_reviewed', result['items'][0]['studio_review'])
            self.assertEqual('pending', result['items'][0]['uckk_review'])
            self.assertIsNone(result['items'][0]['rights']['license'])
            bad = [dict(records[0], chemin='../outside.png')]
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                creative_asset_candidates(exports, bad, catalogue)
            missing = [dict(records[0], chemin='images/roles/missing.png')]
            with self.assertRaisesRegex(ValueError, 'Missing'):
                creative_asset_candidates(exports, missing, catalogue)

if __name__ == '__main__':
    unittest.main()
