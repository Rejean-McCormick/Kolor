# -*- coding: utf-8 -*-
"""Traitement automatique en ligne de commande des planches Kolor Studio."""
import argparse
from pathlib import Path
from kolor_studio_core import roles,process_sheet,export_prompts,export_kontexte,load_state,choose_variant,ROOT,set_role_style,set_role_color,get_role_style
from kolor_palette import load_palettes, style_info


def main():
    ap=argparse.ArgumentParser(description='Kolor Studio — lot de planches')
    ap.add_argument('action',choices=['prompts','importer-dossier','exporter','etat','palettes','choisir-palette','choisir-couleur'])
    ap.add_argument('chemin',nargs='?',help='dossier contenant <identifiant_role>.png')
    ap.add_argument('--projet',default=str(ROOT/'projet'))
    ap.add_argument('--ecraser',action='store_true',help='réimporter aussi les rôles existants')
    ap.add_argument('--role',help='identifiant du personnage, exemple : pecheur')
    ap.add_argument('--palette',default='technique',help='identifiant de la palette')
    ap.add_argument('--skin-tone',default='technique',help='identifiant de carnation')
    ap.add_argument('--region',help='cheveux, haut, bas, chaussures, accessoires')
    ap.add_argument('--hex',help='couleur #RRGGBB ou RESET')
    args=ap.parse_args()
    project=Path(args.projet)
    if args.action=='prompts':print(f'{export_prompts(project)} prompts produits.')
    elif args.action=='palettes':
        catalogue=load_palettes()
        print('PALETTES :')
        for p in catalogue['palettes']:print(' ',p['id'],'—',p['nom'])
        print('SKIN TONES :')
        for c in catalogue['carnations']:print(' ',c['id'],'—',c['nom'],c['couleur'])
    elif args.action=='choisir-palette':
        if not args.role:ap.error('--role est nécessaire')
        try:
            info=style_info(args.palette,args.skin_tone)
            set_role_style(project,args.role,args.palette,args.skin_tone)
        except ValueError as exc:ap.error(str(exc))
        print(args.role,info['palette_nom'],info['skin_tone_nom'],': choix enregistré, réexporter pour appliquer.')
    elif args.action=='choisir-couleur':
        if not args.role or not args.region or not args.hex:
            ap.error('--role, --region et --hex sont nécessaires')
        try:
            set_role_color(project,args.role,args.region,None if args.hex.upper()=='RESET' else args.hex)
        except ValueError as exc:ap.error(str(exc))
        style=get_role_style(project,args.role)
        print(args.role, args.region, style['couleurs_libres'].get(args.region,'palette'),
              '— noir #000000 et blanc #FFFFFF préservés.')
    elif args.action=='importer-dossier':
        if not args.chemin:ap.error('Le dossier des planches est nécessaire')
        directory=Path(args.chemin)
        if not directory.is_dir():ap.error(f'Dossier introuvable : {directory}')
        existing=load_state(project)['roles']
        count=0
        for r in roles():
            fn=directory/f'{r["id"]}.png'
            if not fn.is_file() or (r['id'] in existing and not args.ecraser): continue
            try:process_sheet(project,r['id'],fn)
            except Exception as e:print(f'ERREUR {r["id"]}: {e}')
            else:print('✓',r['nom']);count+=1
        print(f'Importations terminées : {count} planche(s).')
    elif args.action=='exporter':print(export_kontexte(project))
    elif args.action=='etat':
        state=load_state(project)['roles']
        print(f"{len(state)}/38 rôles créés, {sum(x['valide'] for x in state.values())} approuvés.")

if __name__=='__main__':main()
