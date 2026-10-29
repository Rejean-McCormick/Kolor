import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageDraw
from kolor_palette import (CHANNELS,TECHNICAL_COLORS,load_palettes,
                           get_style_colors, recolor, style_info)
from kolor_studio_core import (process_sheet,export_kontexte,get_role_style,
                               set_role_style,load_state,choose_variant)


class PaletteTests(unittest.TestCase):
    def test_catalogue_contains_skin_tones_and_presets(self):
        doc=load_palettes()
        self.assertGreaterEqual(len(doc['palettes']),8)
        self.assertGreaterEqual(len(doc['carnations']),10)
        self.assertEqual('#FFFF00',get_style_colors()['peau'])
        self.assertEqual('#A66B41',get_style_colors('classique','caramel')['peau'])
        self.assertEqual('#000000',get_style_colors('pastel','brun')['contours'])

    def test_exact_technical_codes_change_to_exact_palette_codes(self):
        colors=[TECHNICAL_COLORS[k] for k in CHANNELS]+['#000000','#FFFFFF']
        original=Image.new('RGB',(8,1),'white')
        for i,hexcode in enumerate(colors):
            original.putpixel((i,0),tuple(bytes.fromhex(hexcode[1:])))
        ref=original.copy()
        result=recolor(original,'classique','caramel')
        mapping=get_style_colors('classique','caramel')
        expected=[tuple(bytes.fromhex(mapping[k][1:])) for k in CHANNELS]+[(0,0,0),(255,255,255)]
        self.assertEqual(expected,[result.getpixel((i,0)) for i in range(8)])
        self.assertEqual(list(ref.get_flattened_data()),list(original.get_flattened_data()))

    def test_noop_technical_preserves_all_pixels(self):
        original=Image.new('RGB',(2,2))
        original.putdata([(4,18,31),(255,255,0),(0,0,0),(255,255,255)])
        result=recolor(original)
        self.assertEqual(list(original.get_flattened_data()),list(result.get_flattened_data()))
        self.assertIsNot(result,original)

    def test_invalid_palette_cannot_be_selected(self):
        with self.assertRaisesRegex(ValueError,'inconnue'):
            style_info('not-a-palette','technique')
        with self.assertRaisesRegex(ValueError,'inconnu'):
            get_style_colors('technique','not-a-skin-tone')

    def test_style_before_import_and_after_validation(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            set_role_style(folder,'pecheur','foret','bronze')
            self.assertNotIn('pecheur',load_state(folder)['roles'])
            im=Image.new('RGB',(200,200),'white')
            p=folder/'sheet.png';im.save(p)
            rec=process_sheet(folder,'pecheur',p)
            self.assertEqual('foret',rec['palette_id'])
            self.assertEqual('bronze',rec['skin_tone_id'])
            choose_variant(folder,'pecheur',0,validate=True)
            set_role_style(folder,'pecheur','pastel','ivoire')
            rec=load_state(folder)['roles']['pecheur']
            self.assertFalse(rec['valide'])
            self.assertEqual('pastel',get_role_style(folder,'pecheur')['palette_id'])

    def test_export_recolors_not_sources_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d); src=folder/'synthetic.png'
            sheet=Image.new('RGB',(400,400),'white')
            draw=ImageDraw.Draw(sheet)
            for y in (0,200):
                for x in (0,200):
                    draw.rectangle((x+65,y+45,x+135,y+155),fill='#FFFF00')
                    draw.rectangle((x+82,y+75,x+118,y+125),fill='#00FF00')
            sheet.save(src)
            process_sheet(folder,'pecheur',src)
            original=(folder/'variantes/pecheur/01.png').read_bytes()
            set_role_style(folder,'pecheur','classique','caramel')
            choose_variant(folder,'pecheur',0,validate=True)
            report=export_kontexte(folder)
            self.assertEqual(1,report['exportes'])
            self.assertEqual(original,(folder/'variantes/pecheur/01.png').read_bytes())
            files=[folder/'exports/images'/dir/'pecheur.png' for dir in ('roles','roles_natifs','roles_techniques')]
            self.assertTrue(all(f.is_file() for f in files))
            with Image.open(files[0]) as im:
                cs=im.getcolors(im.width*im.height)
                self.assertIn((166,107,65),{color for _,color in cs})
                self.assertIn((52,120,199),{color for _,color in cs})
            with Image.open(files[2]) as im:
                self.assertIn((255,255,0),{c for _,c in im.getcolors(im.width*im.height)})
            manifest=json.loads((folder/'exports/manifest.json').read_text('utf8'))['roles'][0]
            self.assertEqual('caramel',manifest['skin_tone_id'])
            self.assertEqual('#A66B41',manifest['skin_tone_hex'])
            self.assertEqual('classique',manifest['palette_id'])
            self.assertTrue(manifest['chemin_natif'].startswith('images/roles_natifs/'))
            with Image.open(files[1]) as im:
                self.assertEqual((200,200),im.size)

if __name__=='__main__':unittest.main()
