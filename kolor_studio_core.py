# -*- coding: utf-8 -*-
"""Kolor Studio: production non destructive de planches et d'exports Kontexte.

Aucune génération n'est lancée à l'import: les appels réseau sont volontaires.
La palette est celle de Kolor « nouveau » (peau JAUNE, cheveux ROUGE).
"""
from __future__ import annotations
import base64
import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from kolor_palette import (TECHNICAL_COLORS, EDITABLE_CHANNELS, validate_overrides,
                           load_palettes, style_info, recolor)

ROOT = Path(__file__).resolve().parent
ROLES_FILE = ROOT / 'data' / 'roles.json'
PLAN_DIR = ROOT / 'plans'
SAFETY_MARGIN_RATIO = 1 / 16  # 6,25 % de chaque côté du quart
LEGACY_EXPORT_SIZE = 512  # uniquement pour les anciens plans Kontexte/Ekole
BRAND = '#1E6864'
POSES = [
    ('Principal', 'debout, de face, les pieds visibles, posture accueillante; les deux mains clairement visibles'),
    ('Bonjour', 'debout, de face, souriant et faisant un signe de la main'),
    ('Accessoire', 'debout, de face, montrant un accessoire emblématique du rôle, de façon simple et lisible'),
    ('Action', 'debout et faisant un geste caractéristique du métier, sans autre personnage ni décor'),
]
COLORS = TECHNICAL_COLORS



def roles() -> list[dict]:
    result = json.loads(ROLES_FILE.read_text(encoding='utf-8'))
    assert len(result) == 38 and len({r['id'] for r in result}) == 38
    return result


def prompt_role(role: dict) -> str:
    nom = role['nom']
    action = role['actions'][0] if role['actions'] else 'un geste simple associé à son rôle'
    objet = role['objets'][0] if role['objets'] else 'un accessoire simple'
    return f'''Crée UNE SEULE PLANCHE au FORMAT CARRÉ (rapport largeur/hauteur 1:1), sans imposer de dimensions en pixels. Divise-la mentalement en 2 colonnes × 2 rangées : QUATRE cases carrées identiques occupant chacune 25 % de la surface totale (50 % de la largeur et 50 % de la hauteur).

PERSONNAGE : « {nom} », personnage fictif sympathique dans un cahier de coloriage pour enfants. Idée du rôle : {role['intro']}.

RÈGLE ABSOLUE DE COHÉRENCE : montre EXACTEMENT LE MÊME PERSONNAGE 4 FOIS, avec un visage et une coiffure identiques, les mêmes vêtements et accessoires, les mêmes proportions, la même silhouette et le même âge. Seuls ses bras, ses gestes et sa posture changent légèrement. Ce ne sont pas quatre personnages différents.

DISPOSITION, SANS QUADRILLAGE NI TEXTE :
• Haut gauche (image principale) : {POSES[0][1]}.
• Haut droite : {POSES[1][1]}.
• Bas gauche : {POSES[2][1]}; objet suggéré : {objet}.
• Bas droite : {POSES[3][1]}; geste suggéré : {action}.

IMPORTANT POUR LE DÉCOUPAGE : chaque personnage doit être ENTIER, de la tête aux pieds. Place UN personnage au centre de CHAQUE quart d'image, jamais entre les cases. Laisse une marge blanche de sécurité d'au moins 6,25 % de la largeur de chaque case sur chacun de ses quatre côtés, quelle que soit la résolution choisie. Pas de traits de grille, pas de numéros, pas de titres. Les quatre cases doivent rester lisibles une fois la planche découpée exactement à mi-largeur et à mi-hauteur, sans dimension imposée en pixels.

STYLE : dessin 2D très net, grands aplats, contour NOIR pur (#000000) épais, uniforme et fermé autour de chaque zone, comme un cahier de coloriage pour enfants. Formes claires, peu de petits détails, pas de perspective compliquée. Fond BLANC pur (#FFFFFF), sans paysage, sol, ombre portée, texture, décor ou autre personnage.

IMPORTANT — LES COULEURS SONT UN CODE TECHNIQUE, PAS UN RENDU NATUREL. Utilise UNIQUEMENT ces SIX couleurs pour les aplats, sur les QUATRE cases, sans aucune variation :
• PEAU (visage, mains, jambes visibles) : JAUNE #FFFF00.
• CHEVEUX ou barbe : ROUGE #FF0000.
• HAUT (chemise, manteau ou robe) : VERT #00FF00.
• BAS (pantalon, jupe) : BLEU #0000FF.
• CHAUSSURES : MAGENTA #FF00FF.
• ACCESSOIRES et objets portés : CYAN #00FFFF.
Le noir #000000 est réservé aux contours et aux détails noirs; le blanc #FFFFFF au fond et aux blancs des yeux. Si le personnage n'a pas de cheveux, ne fabrique pas de cheveux pour employer le rouge. Pour un personnage non humain, utilise le jaune comme couleur de sa peau/corps visible. Pour les vêtements d'un seul tenant, vert pour la partie haute et bleu pour la partie basse, avec une ligne noire de séparation.

INTERDICTIONS : aucune septième couleur de remplissage, aucun dégradé, aucun ombrage, aucun reflet, aucun effet 3D, aucune texture, aucun mélange, aucune écriture, aucun cartouche, aucune bordure de grille, aucun décor, aucune couleur de peau naturelle à ce stade. Ne pas générer une planche de personnages différents.

PRIORITÉS : 1) même identité dans les 4 cases, 2) séparation parfaite des cases, 3) six couleurs exactes faciles à remplacer, 4) contours noirs épais, 5) personnages entiers et isolés.'''


def slug_file(role_id: str) -> str:
    if role_id not in {r['id'] for r in roles()}:
        raise ValueError('Identifiant de rôle inconnu')
    return role_id


def atomic_save_image(im: Image.Image, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.kolor-', suffix='.png', dir=str(out.parent))
    try:
        os.close(fd)
        im.save(name, 'PNG')
        os.replace(name, out)
    finally:
        if os.path.exists(name): os.remove(name)


def atomic_save_json(data, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.kolor-', suffix='.json', dir=str(out.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(name, out)
    finally:
        if os.path.exists(name): os.remove(name)


def normalize_sheet(source: str | Path) -> tuple[Image.Image, str | None]:
    """Accepte toute résolution carrée; ne réduit jamais une image importée.

    Si la longueur du côté est impaire, ajoute 1 pixel blanc à droite et en
    bas pour obtenir quatre quarts rigoureusement identiques.
    """
    with Image.open(source) as f:
        im = ImageOps.exif_transpose(f).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        rgb = bg.convert('RGB')
    width, height = rgb.size
    if width != height:
        raise ValueError(
            f'La planche doit être carrée (rapport 1:1). Image reçue : {width} × {height}. '
            'Aucun étirement ni rognage automatique ne sera effectué.'
        )
    if width < 16:
        raise ValueError('Planche trop petite pour un découpage en quatre cases.')
    if width % 2:
        even = Image.new('RGB', (width + 1, height + 1), 'white')
        even.paste(rgb, (0, 0))
        return even, ('Côté impair : un pixel blanc a été ajouté à droite et en bas '
                      'pour obtenir quatre cases égales, sans réduire ni rogner l’image.')
    return rgb, None


def clean_cell(cell: Image.Image, reposition=True) -> Image.Image:
    """Recentre la silhouette avec une marge de 6,25 % par bord.

    Conserve la résolution de la case. Ne convertit pas les six couleurs afin
    de ne pas dissimuler les erreurs éventuelles du modèle de génération.
    """
    im = cell.convert('RGB')
    size = im.width
    if size != im.height:
        raise ValueError('La case doit être carrée.')
    pixels = im.load()
    for y in range(size):
        for x in range(size):
            r, g, b = pixels[x, y]
            if min(r, g, b) >= 248:
                pixels[x, y] = (255, 255, 255)
    if not reposition:
        return im

    sample_size = min(128, size)
    small = im.resize((sample_size, sample_size), Image.Resampling.BOX)
    ink = Image.new('L', (sample_size, sample_size), 0)
    pix = small.load(); mask = ink.load()
    for y in range(sample_size):
        for x in range(sample_size):
            if min(pix[x, y]) < 232:
                mask[x, y] = 255
    bounds = ink.getbbox()
    if not bounds:
        return im
    x0, y0, x1, y1 = [min(size, max(0, round(c * size / sample_size))) for c in bounds]
    minimum_extent = max(4, round(size * 36 / 512))
    if x1 - x0 < minimum_extent or y1 - y0 < minimum_extent:
        return im
    crop = im.crop((x0, y0, x1, y1))
    from math import ceil
    margin = ceil(size * SAFETY_MARGIN_RATIO)
    usable = max(1, size - 2 * margin)
    crop.thumbnail((usable, usable), Image.Resampling.LANCZOS)
    result = Image.new('RGB', (size, size), 'white')
    result.paste(crop, ((size - crop.width) // 2, (size - crop.height) // 2))
    return result


def extract_four(sheet: Image.Image, reposition=True) -> list[Image.Image]:
    """Coupe en quatre zones carrées, sans résolution prédéterminée."""
    if sheet.width != sheet.height:
        raise ValueError('Planche requise : format carré (1:1).')
    if sheet.width % 2:
        padded = Image.new('RGB', (sheet.width + 1, sheet.height + 1), 'white')
        padded.paste(sheet.convert('RGB'), (0, 0))
        sheet = padded
    half = sheet.width // 2
    return [clean_cell(sheet.crop((col * half, row * half,
                                   (col + 1) * half, (row + 1) * half)), reposition)
            for row in range(2) for col in range(2)]


def quality_report(img: Image.Image) -> dict:
    """Heuristique de contrôle, jamais certification que les couleurs sont exactes."""
    import colorsys
    sm = img.convert('RGB').resize((128,128),Image.Resampling.BOX)
    high_sat = off_palette = white = dark = 0
    edge_ink = 0
    data = sm.get_flattened_data() if hasattr(sm,'get_flattened_data') else sm.getdata()
    for i,(r,g,b) in enumerate(data):
        high = max(r,g,b); low = min(r,g,b)
        if low >= 245: white += 1
        if high <= 60: dark += 1
        x=i%128; y=i//128
        if (x<2 or x>125 or y<2 or y>125) and low<100: edge_ink += 1
        if high<90: continue
        s=(high-low)/max(high,1)
        if s<0.6: continue
        high_sat+=1
        hue=colorsys.rgb_to_hsv(r/255,g/255,b/255)[0]*360
        distance=abs((hue+30)%60-30)
        if distance>22: off_palette+=1
    frac=off_palette/max(1,high_sat)
    issues=[]
    if white > 16384*0.96: issues.append('Personnage possiblement absent')
    if edge_ink>35: issues.append('Un personnage ou un trait touche le bord')
    if high_sat>100 and frac>0.12: issues.append('Teintes techniques approximatives')
    return {'a_verifier':issues,'pixels_forts':high_sat,'ecart_palette_pct':round(frac*100,1), 'fond_blanc_pct':round(white/16384*100,1)}


def load_state(project: Path) -> dict:
    f=project/'etat.json'
    if not f.exists(): return {'format':'kolor.studio/1','roles':{}}
    j=json.loads(f.read_text(encoding='utf8'))
    if j.get('format')!='kolor.studio/1': raise ValueError('Projet inconnu')
    return j


def save_state(project: Path, state: dict) -> None:
    atomic_save_json(state,project/'etat.json')


def default_role_style(role_id: str, catalog: dict | None = None) -> dict:
    """Combinaisons MULTICOLORES variées pour les 38 rôles, déterministes.

    Les choix enregistrés précédemment ont toujours priorité sur ces valeurs.
    Les fonds et contours ne font jamais partie de ces palettes.
    """
    catalog = catalog if catalog is not None else load_palettes()
    index = next((i for i, r in enumerate(roles()) if r['id'] == role_id), None)
    if index is None:
        raise ValueError('Identifiant de rôle inconnu')
    colorful = [p['id'] for p in catalog['palettes'] if p['id'] != 'technique']
    natural = [p['id'] for p in catalog['carnations'] if p['id'] != 'technique']
    if not colorful or not natural:
        raise ValueError('Il faut au moins une palette colorée et un skin tone naturel')
    return {'palette_id': colorful[index % len(colorful)],
            'skin_tone_id': natural[index % len(natural)],
            'couleurs_libres': {}}


def get_role_style(project: Path, role_id: str, state: dict | None = None) -> dict:
    """Palette, carnation et couleurs par élément, enregistrées PAR rôle."""
    slug_file(role_id)
    state = state if state is not None else load_state(project)
    values = state.get('styles', {}).get(role_id, {})
    previous = state.get('roles', {}).get(role_id, {})
    defaults = default_role_style(role_id)
    return {
        'palette_id': values.get('palette_id', previous.get('palette_id', defaults['palette_id'])),
        'skin_tone_id': values.get('skin_tone_id', previous.get('skin_tone_id', defaults['skin_tone_id'])),
        'couleurs_libres': validate_overrides(
            values.get('couleurs_libres', previous.get('couleurs_libres', {}))),
    }


def set_role_style(project: Path, role_id: str, palette_id: str, skin_tone_id: str,
                   overrides: dict | None = None) -> None:
    """La peau n'affecte pas les vêtements; aucune image source n'est modifiée.

    overrides=None conserve les couleurs personnelles actuelles, {} les efface.
    """
    slug_file(role_id)
    state = load_state(project)
    old = get_role_style(project, role_id, state)
    colors = old['couleurs_libres'] if overrides is None else validate_overrides(overrides)
    style_info(palette_id, skin_tone_id, overrides=colors)
    new = {'palette_id':palette_id,'skin_tone_id':skin_tone_id,'couleurs_libres':colors}
    if old == new:
        return
    state.setdefault('styles', {})[role_id] = new
    if role_id in state['roles']:
        record = state['roles'][role_id]
        record.update(new)
        # Une autre combinaison doit être vérifiée avant publication.
        record['valide'] = False
    save_state(project,state)


def set_role_color(project: Path, role_id: str, region: str,
                   color: str | None) -> None:
    """Change une seule catégorie, tout en verrouillant peau/traits/fond."""
    if region not in EDITABLE_CHANNELS:
        raise ValueError('La peau se règle par skin tone; traits noirs et fond blanc sont fixes.')
    current = get_role_style(project,role_id)
    extras = dict(current['couleurs_libres'])
    if color is None:
        extras.pop(region, None)
    else:
        extras.update(validate_overrides({region:color}))
    set_role_style(project,role_id,current['palette_id'],current['skin_tone_id'],extras)


def process_sheet(project: Path, role_id: str, original: str | Path) -> dict:
    slug_file(role_id)
    project.mkdir(parents=True,exist_ok=True)
    sheet,warning=normalize_sheet(original)
    out=project/'planches'/f'{role_id}.png'
    atomic_save_image(sheet,out)
    parts=extract_four(sheet)
    qual=[]
    for i,im in enumerate(parts):
        atomic_save_image(im,project/'variantes'/role_id/f'{i+1:02}.png')
        qual.append(quality_report(im))
    state=load_state(project)
    old=state['roles'].get(role_id,{})
    style=get_role_style(project,role_id,state)
    state['roles'][role_id]={
        'planche':f'planches/{role_id}.png','selection':old.get('selection',0),
        'valide':False,'rapport':qual,'avertissement':warning,
        'palette_id':style['palette_id'],'skin_tone_id':style['skin_tone_id'],
        'couleurs_libres':style['couleurs_libres'],
        'importe_le':datetime.now(timezone.utc).isoformat(timespec='seconds')}
    save_state(project,state)
    return state['roles'][role_id]


def choose_variant(project:Path, role_id:str,selection:int,validate:bool|None=None)->None:
    if selection not in range(4):raise ValueError('Choisir une variante de 1 à 4')
    state=load_state(project); record=state['roles'][role_id]
    record['selection']=selection
    if validate is not None:record['valide']=bool(validate)
    else:record['valide']=False
    save_state(project,state)


def export_kontexte(project:Path)->dict:
    """Exports colorés + copies techniques ; les 38 planches natives restent intactes."""
    state=load_state(project)
    catalog=load_palettes()
    exports=project/'exports'; img_root=exports/'images'
    records=[]; selected_count=0
    for role in roles():
        id_=role['id']; rec=state['roles'].get(id_)
        if not rec:continue
        chosen=rec['selection']
        source=project/'variantes'/id_/f'{chosen+1:02}.png'
        if not source.is_file(): continue
        style=get_role_style(project,id_,state)
        meta=style_info(style['palette_id'],style['skin_tone_id'],catalog,style['couleurs_libres'])
        with Image.open(source) as im:
            original=im.convert('RGB')
            colored=recolor(original,style['palette_id'],style['skin_tone_id'],catalog,style['couleurs_libres'])
            # Pose native recolorisée : jamais redimensionnée.
            atomic_save_image(colored,img_root/'roles_natifs'/f'{id_}.png')
            # Copie non recolorisée pour revenir aux six codes techniques.
            technique=original
            if technique.size != (LEGACY_EXPORT_SIZE, LEGACY_EXPORT_SIZE):
                technique=technique.resize((LEGACY_EXPORT_SIZE, LEGACY_EXPORT_SIZE),Image.Resampling.LANCZOS)
            atomic_save_image(technique,img_root/'roles_techniques'/f'{id_}.png')
            # Chemin historique conservé pour Ekole / Kontexte.
            if colored.size != (LEGACY_EXPORT_SIZE, LEGACY_EXPORT_SIZE):
                colored=colored.resize((LEGACY_EXPORT_SIZE, LEGACY_EXPORT_SIZE),Image.Resampling.LANCZOS)
            atomic_save_image(colored,img_root/'roles'/f'{id_}.png')
        selected_count+=1
        records.append({'visual_id':role['visual_id'],'chemin':f'images/roles/{id_}.png',
            'chemin_natif':f'images/roles_natifs/{id_}.png',
            'chemin_technique':f'images/roles_techniques/{id_}.png',
            'statut':'pret' if rec.get('valide') else 'a_verifier',
            'variante':chosen+1,'palette_id':meta['palette_id'],
            'palette_nom':meta['palette_nom'],'skin_tone_id':meta['skin_tone_id'],
            'skin_tone_nom':meta['skin_tone_nom'], 'skin_tone_hex':meta['skin_tone_hex'],
            'couleurs':meta['couleurs'],
            'couleurs_personnalisees':meta['couleurs_personnalisees'],
            'alerte_qualite':rec.get('rapport',[{}]*4)[chosen].get('a_verifier',[])})
    # Rassembler sur les planches originales, sans rendre les rôles absents fictivement.
    present_visuals={r['visual_id'] for r in records}
    sheets=[]
    for plpath in sorted(PLAN_DIR.glob('roles-*.json')):
        pl=json.loads(plpath.read_text(encoding='utf8'))
        surface=Image.new('RGB',(pl['largeur'],pl['hauteur']),'white')
        present=0
        for imrec in pl['images']:
            img_path=exports/imrec['fichier']
            if img_path.is_file() and imrec['visual_id'] in present_visuals:
                with Image.open(img_path) as p:
                    cell=p.convert('RGBA')
                surface.paste(cell,(imrec['zone'][0],imrec['zone'][1]),cell)
                present+=1
        if present:
            dest=exports/'planches_ekole'/f'{plpath.stem}.png'
            atomic_save_image(surface,dest)
            sheets.append({'planche':dest.name,'present':present,'attendu':len(pl['images'])})
    generate_contact_sheet(project,records,exports/'apercu_roles.jpg')
    # Embarquer les presets, sans dépendre du dossier interne Studio.
    atomic_save_json(catalog, exports/'palettes.json')
    atomic_save_json({'format':'kolor.studio.export/1','roles':records,
                      'palettes_fichier':'palettes.json',
                      'a_verifier':sum(x['statut']!='pret' for x in records),
                      'attendus':38,'exportes':selected_count,'planches_ekole':sheets},exports/'manifest.json')
    return {'exportes':selected_count,'a_verifier':sum(x['statut']!='pret' for x in records),
            'planches':len(sheets),'dossier':str(exports)}



def generate_contact_sheet(project: Path, records: list[dict], destination: Path)->None:
    """Vue d'ensemble 38 rôles : statut visible, sans modifier les sources."""
    from PIL import ImageFont
    cols=6; cw=188; ch=222
    total=38; rows=(total+cols-1)//cols
    out=Image.new('RGB',(cols*cw,rows*ch),(244,249,247))
    draw=ImageDraw.Draw(out)
    fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:
        font=ImageFont.truetype(fontpath,13)
    except OSError:
        font=ImageFont.load_default()
    lookup={r['visual_id']:r for r in records}
    for i,r in enumerate(roles()):
        x=(i%cols)*cw; y=(i//cols)*ch
        rect=(x+6,y+6,x+cw-7,y+ch-7)
        draw.rounded_rectangle(rect,radius=8,fill='white',outline=(210,227,222),width=2)
        rec=lookup.get(r['visual_id'])
        if rec:
            src=project/'exports'/rec['chemin']
            with Image.open(src) as im:
                pic=im.convert('RGBA')
                pic.thumbnail((cw-20,ch-49),Image.Resampling.LANCZOS)
            px=x+(cw-pic.width)//2;py=y+8+(ch-49-pic.height)//2
            out.paste(pic,(px,py),pic)
        else:
            draw.text((x+24,y+80),'À produire',fill=(123,151,145),font=font)
        draw.text((x+12,y+ch-35),r['nom'][:23],fill=(24,65,61),font=font)
        symbol='✓' if rec and rec['statut']=='pret' else ('!' if rec else '–')
        draw.text((x+cw-28,y+ch-35),symbol,fill=(30,104,100),font=font)
    destination.parent.mkdir(parents=True,exist_ok=True)
    out.save(destination,'JPEG',quality=91)


def export_prompts(project:Path)->int:
    dest=project/'prompts';dest.mkdir(parents=True,exist_ok=True)
    for r in roles(): (dest/f'{r["id"]}.txt').write_text(prompt_role(r)+'\n',encoding='utf8')
    return len(roles())


def generate_api(role:dict, api_key:str, model:str='gpt-image-2.5-flare',quality:str='medium',timeout:int=240)->bytes:
    """Appel intentionnel à l'API Images; jamais déclenché sans action utilisateur.

    Bibliothèques standard seulement. N'enregistre ni n'affiche la clé API.
    """
    if not api_key.strip():raise ValueError('Clé API requise')
    supported=['gpt-image-2.5-flare','gpt-image-2.5-sunburst','gpt-image-2']
    if model not in supported:raise ValueError('Modèle non pris en charge')
    if quality not in ['low','medium','high']:raise ValueError('Qualité invalide')
    payload={'model':model,'prompt':prompt_role(role),'size':'auto',
             'quality':quality,'n':1,'output_format':'png','background':'opaque'}
    req=urllib.request.Request('https://api.openai.com/v1/images/generations',
        data=json.dumps(payload).encode('utf8'),headers={
            'Authorization':'Bearer '+api_key.strip(),
            'Content-Type':'application/json'},method='POST')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=timeout) as response:
                data=json.loads(response.read().decode('utf8'))
            raw=data['data'][0].get('b64_json')
            if not raw:raise ValueError('Image absente dans la réponse API')
            decoded=base64.b64decode(raw,validate=True)
            with Image.open(__import__('io').BytesIO(decoded)) as im:
                im.verify()
            return decoded
        except urllib.error.HTTPError as exc:
            body=exc.read(2048).decode('utf8',errors='replace')
            try:msg=json.loads(body).get('error',{}).get('message','Erreur API')
            except (ValueError,AttributeError):msg='Erreur API'
            if exc.code in [429,500,502,503,504] and attempt<2:
                time.sleep(min(10,2**attempt*3));continue
            raise RuntimeError(f'API HTTP {exc.code}: {msg}') from None
        except urllib.error.URLError as exc:
            if attempt<2: time.sleep(2**attempt*3);continue
            raise RuntimeError('Connexion API impossible : '+str(exc.reason)) from None
    raise RuntimeError('Génération impossible')
