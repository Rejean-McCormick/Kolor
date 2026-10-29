import io
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageDraw
from kolor_studio_core import (
    roles,prompt_role,normalize_sheet,extract_four,process_sheet,
    load_state,choose_variant,export_kontexte,quality_report,PLAN_DIR
)

class CoreTests(unittest.TestCase):
    def sheet(self):
        p=Image.new('RGB',(1024,1024),'white')
        d=ImageDraw.Draw(p)
        cols=['#FFFF00','#FF0000','#00FF00','#0000FF']
        for k,color in enumerate(cols):
            x=(k%2)*512;y=(k//2)*512
            d.ellipse((x+150,y+80,x+365,y+390),fill=color,outline='black',width=10)
        return p
    def test_roles_plans_match(self):
        r=roles(); self.assertEqual(38,len(r))
        all_plan=[]
        for path in PLAN_DIR.glob('roles-*.json'):
            p=json.loads(path.read_text(encoding='utf8'))
            self.assertEqual((2048,1024),(p['largeur'],p['hauteur']))
            all_plan.extend(x['visual_id'] for x in p['images'])
        self.assertEqual({x['visual_id'] for x in r},set(all_plan))
        self.assertEqual(38,len(all_plan))
    def test_prompt_palette_new(self):
        r=next(x for x in roles() if x['id']=='sorciere')
        p=prompt_role(r)
        for text in ['Sorcière','2 colonnes × 2 rangées','1:1','6,25 %','#FFFF00','#FF0000','#00FF00','#0000FF','#FF00FF','#00FFFF','MÊME PERSONNAGE']:
            self.assertIn(text,p)
        self.assertNotIn('1024 × 1024',p)
        self.assertNotIn('512 × 512',p)
        self.assertNotIn('32 pixels',p)
    def test_crop_order(self):
        crops=extract_four(self.sheet(),reposition=False)
        self.assertEqual([p.getpixel((256,235)) for p in crops],[(255,255,0),(255,0,0),(0,255,0),(0,0,255)])
    def test_import_export_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            temp=Path(temp)
            src=temp/'source.png';self.sheet().save(src)
            rec=process_sheet(temp,'sorciere',src)
            self.assertEqual(4,len(rec['rapport']))
            self.assertFalse(rec['valide'])
            choose_variant(temp,'sorciere',2,validate=True)
            out=export_kontexte(temp)
            self.assertEqual(1,out['exportes']);self.assertEqual(0,out['a_verifier'])
            file=temp/'exports/images/roles/sorciere.png'
            self.assertTrue(file.is_file())
            with Image.open(file) as image:self.assertEqual((512,512),image.size)
            manifest=json.loads((temp/'exports/manifest.json').read_text(encoding='utf8'))
            self.assertEqual('role-sorciere',manifest['roles'][0]['visual_id'])
            self.assertEqual(3,manifest['roles'][0]['variante'])
            self.assertTrue(any(x['planche']=='roles-05.png' for x in manifest['planches_ekole']))
            choose_variant(temp,'sorciere',0)
            self.assertFalse(load_state(temp)['roles']['sorciere']['valide'])
    def test_any_square_resolution_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'une_planche.png'
            Image.new('RGB',(1254,1254),'white').save(src)
            pic,warning=normalize_sheet(src)
            self.assertEqual((1254,1254),pic.size)
            self.assertIsNone(warning)
            crops=extract_four(pic,reposition=False)
            self.assertEqual([(627,627)]*4,[im.size for im in crops])
    def test_nonstandard_square_import_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)
            src=project/'source.png'
            Image.new('RGB',(600,600),'white').save(src)
            rec=process_sheet(project,'sorciere',src)
            self.assertIsNone(rec['avertissement'])
            with Image.open(project/'planches'/'sorciere.png') as im:
                self.assertEqual((600,600),im.size)
            with Image.open(project/'variantes'/'sorciere'/'01.png') as im:
                self.assertEqual((300,300),im.size)
            choose_variant(project,'sorciere',0,validate=True)
            export_kontexte(project)
            with Image.open(project/'exports'/'images'/'roles'/'sorciere.png') as im:
                self.assertEqual((512,512),im.size)  # contrat du catalogue ancien
    def test_odd_square_adds_white_padding(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'impair.png'
            Image.new('RGB',(601,601),'red').save(src)
            pic,warning=normalize_sheet(src)
            self.assertEqual((602,602),pic.size)
            self.assertIn('pixel blanc',warning)
            self.assertEqual((255,255,255),pic.getpixel((601,601)))
            self.assertEqual([(301,301)]*4,[p.size for p in extract_four(pic,reposition=False)])
    def test_rectangular_image_is_rejected_without_stretching(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'rectangle.png'
            Image.new('RGB',(1000,800),'white').save(src)
            with self.assertRaisesRegex(ValueError,'carrée'):
                normalize_sheet(src)

    def test_quality_alert(self):
        self.assertTrue(quality_report(Image.new('RGB',(512,512),'white'))['a_verifier'])

if __name__=='__main__': unittest.main()
