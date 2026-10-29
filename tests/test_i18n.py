"""Internationalization regression tests; no real network or image generation."""
import json
import tempfile
import unittest
from pathlib import Path
from kolor_studio_core import roles
from kolor_palette import load_palettes
from kolor_i18n import (get_language,set_language,translate,role_name,
                        detail_name,preset_name,ROLE_EN,ACTION_EN,OBJECT_EN,
                        PALETTE_EN,SKIN_EN)

class I18nTests(unittest.TestCase):
    def test_french_default_and_persisted_english(self):
        with tempfile.TemporaryDirectory() as d:
            project=Path(d)/'projet'
            self.assertEqual(get_language(project),'fr')
            set_language(project,'en')
            self.assertEqual(get_language(project),'en')
            data=json.loads((project/'preferences.json').read_text('utf-8'))
            self.assertEqual(data,{'language':'en'})
            set_language(project,'fr')
            self.assertEqual(get_language(project),'fr')
            with self.assertRaises(ValueError):set_language(project,'es')

    def test_all_roles_have_english_names(self):
        dataset=roles()
        self.assertEqual(len(dataset),38)
        self.assertEqual(set(ROLE_EN),{r['id'] for r in dataset})
        for r in dataset:
            self.assertTrue(role_name(r,'en'))
            self.assertEqual(role_name(r,'fr'),r['nom'])

    def test_all_role_details_are_localized(self):
        dataset=roles()
        self.assertEqual(set(ACTION_EN),{a for r in dataset for a in r['actions']})
        self.assertEqual(set(OBJECT_EN),{o for r in dataset for o in r['objets']})
        self.assertEqual(detail_name('mesurer','action','en'),'measure')
        self.assertEqual(detail_name('carte','object','en'),'map')

    def test_preset_display_names_without_touching_ids(self):
        palette=load_palettes()
        self.assertEqual(set(PALETTE_EN),{p['id'] for p in palette['palettes']})
        self.assertEqual(set(SKIN_EN),{p['id'] for p in palette['carnations']})
        for item in palette['palettes']:
            self.assertEqual(preset_name(item,'palette','fr'),item['nom'])
            self.assertTrue(preset_name(item,'palette','en'))

    def test_ui_translation_and_formatting(self):
        self.assertEqual(translate('Copier le prompt du rôle','en'),'Copy role prompt')
        self.assertEqual(translate('Copier le prompt du rôle','fr'),'Copier le prompt du rôle')
        self.assertEqual(translate('Couleur — {region}','en',region='Top'),'Color — Top')
        self.assertEqual(translate('Personnage possiblement absent','en'),'Character may be missing')

if __name__=='__main__':unittest.main()
