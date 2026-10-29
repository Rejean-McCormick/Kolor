import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
from kolor_palette import (TECHNICAL_COLORS, EDITABLE_CHANNELS, recolor,
                           get_style_colors, validate_overrides, load_palettes)
from kolor_studio_core import (roles, default_role_style, get_role_style,
                               set_role_color, set_role_style, process_sheet,
                               export_kontexte, load_state)


class VariedColorsTests(unittest.TestCase):
    def test_38_default_roles_have_varied_palette_and_skin_tones(self):
        presets=[default_role_style(r['id']) for r in roles()]
        self.assertEqual(38,len(presets))
        self.assertGreaterEqual(len({p['palette_id'] for p in presets}),8)
        self.assertGreaterEqual(len({p['skin_tone_id'] for p in presets}),10)
        self.assertTrue(all(p['palette_id'] != 'technique' for p in presets))
        self.assertTrue(all(p['skin_tone_id'] != 'technique' for p in presets))
        for p in presets:
            colors=get_style_colors(p['palette_id'],p['skin_tone_id'])
            self.assertGreaterEqual(len({colors[k] for k in EDITABLE_CHANNELS}),4)

    def test_custom_colors_independent_skin_and_black_lines_locked(self):
        custom={'cheveux':'#802B41','haut':'#FF8844','bas':'#5599CC',
                'chaussures':'#EE44AA','accessoires':'#4DAB74'}
        c1=get_style_colors('classique','porcelaine',overrides=custom)
        c2=get_style_colors('classique','ebene',overrides=custom)
        self.assertNotEqual(c1['peau'],c2['peau'])
        for key in EDITABLE_CHANNELS:
            self.assertEqual(custom[key],c1[key])
            self.assertEqual(c1[key],c2[key])
        self.assertEqual('#000000',c1['contours'])
        self.assertEqual('#FFFFFF',c2['fond'])
        for k in ('contours','fond','peau'):
            with self.assertRaises(ValueError):
                validate_overrides({k:'#123456'})
        for forbidden in ('#000000','#FFFFFF'):
            with self.assertRaises(ValueError):
                validate_overrides({'haut':forbidden})

    def test_black_and_white_remain_exact_across_all_palettes_and_skin_tones(self):
        source=Image.new('RGB',(8,2),'white')
        colors=[TECHNICAL_COLORS[k] for k in ('peau','cheveux','haut','bas','chaussures','accessoires')]
        colors+=['#000000','#FFFFFF']
        for x,v in enumerate(colors):
            source.putpixel((x,0),tuple(bytes.fromhex(v[1:])))
        for x in range(8):
            source.putpixel((x,1),(0,0,0) if x%2==0 else (255,255,255))
        for palette in load_palettes()['palettes']:
            for skin in load_palettes()['carnations']:
                result=recolor(source,palette['id'],skin['id'])
                self.assertEqual((0,0,0),result.getpixel((6,0)))
                self.assertEqual((255,255,255),result.getpixel((7,0)))
                for x in range(8):
                    self.assertEqual(source.getpixel((x,1)),result.getpixel((x,1)))

    def test_selected_region_only_and_exports_preserve_sources(self):
        with tempfile.TemporaryDirectory() as d:
            project=Path(d)
            source=Image.new('RGB',(200,200),'#FFFFFF')
            draw=ImageDraw.Draw(source)
            for x in (0,100):
                for y in (0,100):
                    draw.rectangle((x+25,y+15,x+75,y+85),fill='#00FF00',outline='#000000',width=6)
                    draw.ellipse((x+32,y+22,x+65,y+50),fill='#FFFF00',outline='#000000',width=4)
            src=project/'sheet.png';source.save(src)
            process_sheet(project,'architecte',src)
            before=(project/'variantes/architecte/01.png').read_bytes()
            original=get_role_style(project,'architecte')
            set_role_color(project,'architecte','haut','#CC7744')
            updated=get_role_style(project,'architecte')
            self.assertEqual('#CC7744',updated['couleurs_libres']['haut'])
            self.assertEqual(original['skin_tone_id'],updated['skin_tone_id'])
            set_role_style(project,'architecte',updated['palette_id'],'ebene')
            self.assertEqual('#CC7744',get_role_style(project,'architecte')['couleurs_libres']['haut'])
            export_kontexte(project)
            self.assertEqual(before,(project/'variantes/architecte/01.png').read_bytes())
            manifest=json.loads((project/'exports/manifest.json').read_text('utf-8'))
            info=manifest['roles'][0]
            self.assertEqual('#CC7744',info['couleurs']['haut'])
            self.assertEqual('#3B241C',info['couleurs']['peau'])
            self.assertEqual('#000000',info['couleurs']['contours'])
            with Image.open(project/'exports/images/roles_natifs/architecte.png') as pic:
                self.assertEqual((0,0,0),pic.getpixel((25,25)))
                self.assertEqual((255,255,255),pic.getpixel((0,0)))
            set_role_color(project,'architecte','haut',None)
            self.assertEqual({},get_role_style(project,'architecte')['couleurs_libres'])

if __name__ == '__main__':
    unittest.main()
