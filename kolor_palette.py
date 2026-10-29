# -*- coding: utf-8 -*-
"""Kolor Studio : recoloration non destructive du code technique.

Six couleurs techniques localisent les zones. La carnation est indépendante des
couleurs variées des cheveux, vêtements, chaussures et accessoires. Noir pur
(#000000) et blanc pur (#FFFFFF) ne sont jamais des couleurs à recolorer.
"""
from __future__ import annotations

import colorsys
import json
import re
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageFilter

PALETTES_FILE = Path(__file__).resolve().parent / 'data' / 'palettes.json'
TECHNICAL_COLORS = {
    'peau': '#FFFF00', 'cheveux': '#FF0000', 'haut': '#00FF00',
    'bas': '#0000FF', 'chaussures': '#FF00FF', 'accessoires': '#00FFFF',
    'contours': '#000000', 'fond': '#FFFFFF',
}
CHANNELS = ('peau','cheveux','haut','bas','chaussures','accessoires')
EDITABLE_CHANNELS = ('cheveux', 'haut', 'bas', 'chaussures', 'accessoires')
HUE_CHANNELS = ('cheveux', 'peau', 'haut', 'accessoires', 'bas', 'chaussures')
HEX_PATTERN = re.compile(r'#[0-9A-Fa-f]{6}\Z')


def _hex(value: str, label: str, *, allow_neutral: bool = False) -> str:
    if not isinstance(value, str) or not HEX_PATTERN.fullmatch(value):
        raise ValueError(f'HEX invalide pour {label} : attendu #RRGGBB')
    normalized = value.upper()
    if not allow_neutral and normalized in ('#000000', '#FFFFFF'):
        raise ValueError('Le noir pur est réservé aux traits et le blanc pur au fond.')
    return normalized


def validate_overrides(overrides: dict | None) -> dict[str, str]:
    """Accepte uniquement les cinq catégories colorables, jamais peau/traits/fond."""
    if overrides is None:
        return {}
    if not isinstance(overrides, dict):
        raise ValueError('Couleurs personnalisées : dictionnaire attendu')
    unknown = set(overrides) - set(EDITABLE_CHANNELS)
    if unknown:
        raise ValueError('Zones interdites à la modification : ' + ', '.join(sorted(unknown)))
    return {channel: _hex(value, channel) for channel, value in overrides.items()}


def load_palettes(path: Path | None = None) -> dict:
    doc = json.loads(Path(path or PALETTES_FILE).read_text(encoding='utf-8'))
    if doc.get('format') != 'kolor.palettes/1':
        raise ValueError('Fichier de palettes incompatible')
    for collection, fields in (
        ('palettes', EDITABLE_CHANNELS), ('carnations', ('couleur',)),
    ):
        items = doc.get(collection)
        if not isinstance(items, list) or not items:
            raise ValueError('Liste non vide requise : ' + collection)
        ids = set()
        for item in items:
            ident = item.get('id')
            if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9-]+', ident) or ident in ids:
                raise ValueError('Identifiant de palette ou de carnation invalide/dupliqué')
            if not item.get('nom'):
                raise ValueError('Nom manquant : ' + ident)
            ids.add(ident)
            for field in fields:
                _hex(item.get(field), f'{ident}/{field}', allow_neutral=(ident == 'technique'))
    if doc.get('palette_par_defaut') not in {x['id'] for x in doc['palettes']}:
        raise ValueError('Palette par défaut inconnue')
    if doc.get('carnation_par_defaut') not in {x['id'] for x in doc['carnations']}:
        raise ValueError('Carnation par défaut inconnue')
    return doc


def get_style_colors(palette_id: str = 'technique', skin_tone_id: str = 'technique',
                     catalog: dict | None = None, overrides: dict | None = None) -> dict[str, str]:
    catalog = catalog if catalog is not None else load_palettes()
    palette = next((p for p in catalog['palettes'] if p['id'] == palette_id), None)
    skin = next((p for p in catalog['carnations'] if p['id'] == skin_tone_id), None)
    if palette is None:
        raise ValueError('Palette inconnue : ' + str(palette_id))
    if skin is None:
        raise ValueError('Skin tone inconnu : ' + str(skin_tone_id))
    out = {k: _hex(palette[k], k, allow_neutral=(palette_id == 'technique'))
           for k in EDITABLE_CHANNELS}
    out.update(validate_overrides(overrides))
    out.update({'peau': _hex(skin['couleur'], 'carnation', allow_neutral=True),
                'contours': '#000000', 'fond': '#FFFFFF'})
    return out


def style_info(palette_id='technique', skin_tone_id='technique', catalog=None, overrides=None):
    catalog = catalog if catalog is not None else load_palettes()
    palette = next((p for p in catalog['palettes'] if p['id'] == palette_id), None)
    skin = next((s for s in catalog['carnations'] if s['id'] == skin_tone_id), None)
    if palette is None or skin is None:
        raise ValueError('Palette ou carnation inconnue')
    return {'palette_id': palette['id'], 'palette_nom': palette['nom'],
            'skin_tone_id': skin['id'], 'skin_tone_nom': skin['nom'],
            'skin_tone_hex': skin['couleur'].upper(),
            'couleurs_personnalisees': validate_overrides(overrides),
            'couleurs': get_style_colors(palette_id, skin_tone_id, catalog, overrides)}


@lru_cache(maxsize=96)
def _make_filter(colors_key: tuple[str, ...]):
    """LUT Pillow native, conserve le noir/blanc et les bords antialiasés.

    Les aplats techniques exacts deviennent les codes HEX demandés. Les gris
    (contours noirs, fond blanc, antialiasing neutre) restent inchangés.
    """
    target = {name: tuple(int(v[i:i+2], 16)/255 for i in (1,3,5))
              for name, v in zip(CHANNELS, colors_key)}

    def converter(r, g, b):
        hi = max(r,g,b); lo = min(r,g,b); chroma = hi - lo
        # Ne jamais recolorer les traits sombres ni les tons de gris.
        if hi < 0.10 or chroma < 0.09:
            return (r,g,b)
        hue = colorsys.rgb_to_hsv(r,g,b)[0] * 6.0
        nearest = round(hue) % 6
        distance = abs((hue-nearest+3)%6 - 3)
        if distance > 0.40:
            return (r,g,b)
        replacement = target[HUE_CHANNELS[nearest]]
        return tuple(min(1.0, lo + chroma * c) for c in replacement)

    return ImageFilter.Color3DLUT.generate(33, converter)


def recolor(image: Image.Image, palette_id='technique', skin_tone_id='technique',
            catalog=None, overrides=None) -> Image.Image:
    """Retourne une copie, jamais une modification de l'image source.

    Tous les noirs purs restent #000000, tous les blancs purs #FFFFFF.
    Les six couleurs techniques d'origine ne sont pas modifiées sur disque.
    """
    rgb = image.convert('RGB')
    mapping = get_style_colors(palette_id, skin_tone_id, catalog, overrides)
    if all(mapping[k] == TECHNICAL_COLORS[k] for k in CHANNELS):
        return rgb.copy()
    return rgb.filter(_make_filter(tuple(mapping[k] for k in CHANNELS)))
