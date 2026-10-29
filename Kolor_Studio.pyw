# -*- coding: utf-8 -*-
"""Kolor Studio — bilingual (French/English) manager for 38 Kontexte roles.

Windows : py -m pip install pillow ; double-clic sur Kolor_Studio.pyw
API facultative : clé personnelle OpenAI et frais API séparés de ChatGPT.
"""
from __future__ import annotations
import io
import os
import queue
import random
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageDraw, ImageTk
from kolor_studio_core import (
    ROOT,BRAND,roles,prompt_role,load_state,process_sheet,choose_variant,
    export_kontexte,export_prompts,generate_api,atomic_save_image,
    get_role_style,set_role_style,set_role_color,
)
from kolor_palette import load_palettes, get_style_colors, recolor, EDITABLE_CHANNELS
from kolor_i18n import (translate, role_name, detail_name, preset_name,
                        get_language, set_language)

BG='#F3F7F6'; WHITE='#FFFFFF'; DARK='#173D39'; MUTED='#64807C'; LINE='#D7E6E2'
PALE= '#E8F2F0'; ORANGE='#F4B650'; PROJECT=ROOT/'projet'


def launch_folder(path:Path):
    path.mkdir(parents=True,exist_ok=True)
    if sys.platform=='win32': os.startfile(path)
    elif sys.platform=='darwin': subprocess.Popen(['open',str(path)])
    else: subprocess.Popen(['xdg-open',str(path)])


class Studio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang=get_language(PROJECT)
        self.title(self.T('Kolor Studio • Personnages Kontexte'))
        try:self.iconbitmap(str(ROOT/'Kolor_Studio.ico'))
        except (OSError,tk.TclError):pass
        self.geometry('1280x850');self.minsize(1180,680)
        self.configure(bg=BG)
        self.data=roles()
        self.ids={r['id']:r for r in self.data}
        self.project=PROJECT
        self.state_data=load_state(self.project)
        self.catalog=load_palettes()
        self.lang=get_language(self.project)
        self.language_var=tk.StringVar(value='English' if self.lang=='en' else 'Français')
        self._make_preset_maps()
        self.palette_var=tk.StringVar(value=self.palette_names['technique'])
        self.skin_var=tk.StringVar(value=self.skin_names['technique'])
        self.show_technical=tk.BooleanVar(value=False)
        self.current='sorciere'
        self.preview_tk=None;self.card_images=[]
        self.messages=queue.Queue();self.worker=None
        self.stop_flag=threading.Event()
        self.search=tk.StringVar();self.search.trace_add('write',lambda *_:self._fill_roles())
        self.model=tk.StringVar(value='gpt-image-2.5-flare')
        self.quality=tk.StringVar(value='medium')
        self.api_key=tk.StringVar(value=os.environ.get('OPENAI_API_KEY',''))
        self.status=tk.StringVar(value=self.T('Prêt — sélectionne un rôle pour commencer.'))
        self._create_ui();self._fill_roles();self.select(self.current)
        self.after(100,self._poll)
        self.protocol('WM_DELETE_WINDOW',self._on_close)

    def T(self,text,**kwargs):
        return translate(text,self.lang,**kwargs)

    def msg(self,fr,en):
        return en if self.lang=='en' else fr

    def fmt(self,fr,en,**kwargs):
        return (en if self.lang=='en' else fr).format(**kwargs)

    def role_label(self,role):
        return role_name(role,self.lang)

    def _make_preset_maps(self):
        self.palette_names={p['id']:preset_name(p,'palette',self.lang) for p in self.catalog['palettes']}
        self.palette_ids={name:key for key,name in self.palette_names.items()}
        self.skin_names={p['id']:preset_name(p,'skin',self.lang) for p in self.catalog['carnations']}
        self.skin_ids={name:key for key,name in self.skin_names.items()}

    def _switch_language(self,event=None):
        selected='en' if self.language_var.get()=='English' else 'fr'
        if selected==self.lang:return
        # Project state stores stable palette IDs, not translated combo labels.
        self.lang=selected
        set_language(self.project,selected)
        self._make_preset_maps()
        self.title(self.T('Kolor Studio • Personnages Kontexte'))
        for child in self.winfo_children():child.destroy()
        self._create_ui()
        self._fill_roles()
        self.select(self.current)
        self.status.set(self.msg('Interface en français.','Interface in English.'))

    def label(self,parent,text="",fg=DARK,font=('Segoe UI',11),**kw):
        return tk.Label(parent,text=self.T(text),bg=parent.cget('bg'),fg=fg,font=font,**kw)

    def btn(self,parent,text,command,primary=False,**kwargs):
        return tk.Button(parent,text=self.T(text),command=command,font=('Segoe UI Semibold',10),
                bg=BRAND if primary else PALE,fg='white' if primary else BRAND,
                activebackground='#135450' if primary else '#D8EAE6',
                activeforeground='white' if primary else BRAND,relief='flat',cursor='hand2',
                padx=11,pady=9,borderwidth=0,**kwargs)

    def _create_ui(self):
        header=tk.Frame(self,bg=BRAND,height=84)
        header.pack(side='top',fill='x');header.pack_propagate(False)
        logo_file=ROOT/'Logo_Kolor_blanc.png'
        if logo_file.exists():
            logo=Image.open(logo_file).convert('RGBA')
            logo.thumbnail((128,52))
            self.header_logo=ImageTk.PhotoImage(logo)
            tk.Label(header,image=self.header_logo,bg=BRAND).pack(side='left',padx=(22,10),pady=8)
        else:
            tk.Label(header,text='Kolor',font=('Segoe UI',25,'bold'),bg=BRAND,fg='white').pack(side='left',padx=20)
        tk.Label(header,text=self.T('STUDIO · FABRIQUE DE PERSONNAGES'),font=('Segoe UI',12,'bold'),
                bg=BRAND,fg='white').pack(side='left',padx=8)
        self.progress_label=tk.Label(header,text=self.msg('38 rôles · 4 poses chacun',
            '38 roles · 4 poses each'),bg=BRAND,fg='white',font=('Segoe UI',10))
        self.progress_label.pack(side='right',padx=(12,20))
        self.language_picker=ttk.Combobox(header,textvariable=self.language_var,state='readonly',
                                         values=['Français','English'],width=11)
        self.language_picker.pack(side='right',padx=(3,12))
        self.language_picker.bind('<<ComboboxSelected>>',self._switch_language)
        tk.Label(header,text=self.T('Langue'),bg=BRAND,fg='white',font=('Segoe UI',10)).pack(side='right')

        body=tk.Frame(self,bg=BG)
        body.pack(side='top',fill='both',expand=True,padx=13,pady=13)
        self.left=tk.Frame(body,bg=WHITE,width=272,highlightbackground=LINE,highlightthickness=1)
        self.left.pack(side='left',fill='y',padx=(0,10));self.left.pack_propagate(False)
        middle=tk.Frame(body,bg=WHITE,highlightbackground=LINE,highlightthickness=1)
        right=tk.Frame(body,bg=WHITE,width=340,highlightbackground=LINE,highlightthickness=1)
        right.pack(side='right',fill='y');right.pack_propagate(False)
        middle.pack(side='left',fill='both',expand=True,padx=(0,10))
        self._left_panel();self._middle_panel(middle);self._right_panel(right)
        bottom=tk.Frame(self,bg=BG,height=44)
        bottom.pack(side='bottom',fill='x')
        self.label(bottom,'●',fg=BRAND).pack(side='left',padx=(18,5))
        self.label(bottom,textvariable=self.status,fg=MUTED,font=('Segoe UI',9),anchor='w').pack(side='left',fill='x',expand=True)

    def _left_panel(self):
        self.label(self.left,'Personnages de Kontexte',font=('Segoe UI',14,'bold')).pack(anchor='w',padx=12,pady=(15,5))
        entry=tk.Entry(self.left,textvariable=self.search,font=('Segoe UI',11),relief='flat',bg=BG,fg=DARK,
                    highlightbackground=LINE,highlightthickness=1)
        entry.pack(fill='x',padx=12,pady=(5,8),ipady=8)
        self.label(self.left,'Rechercher un rôle',fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=12)
        holder=tk.Frame(self.left,bg=WHITE)
        holder.pack(fill='both',expand=True,padx=6,pady=8)
        self.role_canvas=tk.Canvas(holder,bg=WHITE,highlightthickness=0)
        bar=tk.Scrollbar(holder,orient='vertical',command=self.role_canvas.yview)
        bar.pack(side='right',fill='y');self.role_canvas.pack(side='left',fill='both',expand=True)
        self.role_canvas.configure(yscrollcommand=bar.set)
        self.role_holder=tk.Frame(self.role_canvas,bg=WHITE)
        self.role_window=self.role_canvas.create_window((0,0),window=self.role_holder,anchor='nw')
        self.role_holder.bind('<Configure>',lambda e:self.role_canvas.configure(scrollregion=self.role_canvas.bbox('all')))
        self.role_canvas.bind('<Configure>',lambda e:self.role_canvas.itemconfig(self.role_window,width=e.width))
        self.role_canvas.bind('<MouseWheel>',lambda e:self.role_canvas.yview_scroll(int(-1*(e.delta/120)),'units'))
        self.count_label=self.label(self.left,'',fg=MUTED,font=('Segoe UI',10))
        self.count_label.pack(anchor='w',padx=12,pady=(0,12))

    def _middle_panel(self,middle):
        top=tk.Frame(middle,bg=WHITE);top.pack(fill='x',padx=18,pady=(18,5))
        self.main_title=self.label(top,'',font=('Segoe UI',20,'bold'))
        self.main_title.pack(anchor='w')
        self.description=self.label(top,'',fg=MUTED,font=('Segoe UI',10),wraplength=520,justify='left')
        self.description.pack(anchor='w',pady=(3,5))
        preview_box=tk.Frame(middle,bg=PALE)
        preview_box.pack(fill='both',expand=True,padx=18,pady=(8,8))
        self.preview=tk.Label(preview_box,bg=PALE,text=self.T('Aucune planche importée\n\nCrée une planche ou importe une image carrée (1:1), sans taille imposée.'),
                 fg=MUTED,font=('Segoe UI',13),justify='center')
        self.preview.pack(fill='both',expand=True,padx=7,pady=7)
        self.preview.bind('<Configure>',lambda e:self._show_preview())
        self.label(middle,'Choisis la meilleure pose pour Kolor et Kontexte',
                   font=('Segoe UI',11,'bold')).pack(anchor='w',padx=18,pady=(4,4))
        cards=tk.Frame(middle,bg=WHITE);cards.pack(fill='x',padx=15,pady=(2,10))
        self.choices=[]
        for column in range(4):cards.columnconfigure(column,weight=1,uniform='pose')
        for i,txt in enumerate(['1 · Principal','2 · Bonjour','3 · Accessoire','4 · Action']):
            f=tk.Frame(cards,bg=WHITE,highlightbackground=LINE,highlightthickness=2)
            f.grid(row=0,column=i,sticky='nsew',padx=3)
            thumb=tk.Label(f,text='?',font=('Segoe UI',15,'bold'),bg=PALE,width=12,height=5)
            thumb.pack(fill='x',padx=3,pady=3)
            self.btn(f,txt,lambda k=i:self._choose(k)).pack(fill='x',padx=3,pady=(0,3))
            self.choices.append((f,thumb))
        self.alert=self.label(middle,'',fg='#885D28',font=('Segoe UI',9),wraplength=620,justify='left')
        self.alert.pack(anchor='w',padx=18,pady=(0,14))

    def _right_panel(self,container):
        # Le panneau doit rester accessible sur un écran de portable plus petit.
        scroll=tk.Canvas(container,bg=WHITE,highlightthickness=0)
        scroll_bar=tk.Scrollbar(container,orient='vertical',command=scroll.yview)
        scroll_bar.pack(side='right',fill='y')
        scroll.pack(side='left',fill='both',expand=True)
        scroll.configure(yscrollcommand=scroll_bar.set)
        right=tk.Frame(scroll,bg=WHITE)
        window=scroll.create_window((0,0),window=right,anchor='nw')
        right.bind('<Configure>',lambda e:scroll.configure(scrollregion=scroll.bbox('all')))
        scroll.bind('<Configure>',lambda e:scroll.itemconfig(window,width=e.width))
        scroll.bind('<MouseWheel>',lambda e:scroll.yview_scroll(-int(e.delta/120),'units'))
        pad=14
        self.label(right,'1. Créer une planche',font=('Segoe UI',14,'bold')).pack(anchor='w',padx=pad,pady=(15,5))
        self.btn(right,'Copier le prompt du rôle',self._copy_prompt,primary=True).pack(fill='x',padx=pad,pady=3)
        self.btn(right,'Importer une planche PNG…',self._import_sheet).pack(fill='x',padx=pad,pady=3)
        self.btn(right,'Préparer les 38 prompts',self._export_prompts).pack(fill='x',padx=pad,pady=3)
        tk.Frame(right,bg=LINE,height=1).pack(fill='x',padx=pad,pady=15)
        self.label(right,'2. Génération automatique (API)',font=('Segoe UI',12,'bold')).pack(anchor='w',padx=pad)
        self.label(right,'Facultatif : frais API séparés de ChatGPT.',fg=MUTED,
                   font=('Segoe UI',9),wraplength=250,justify='left').pack(anchor='w',padx=pad,pady=(2,9))
        self.label(right,'Clé API (non enregistrée)',fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=pad)
        tk.Entry(right,textvariable=self.api_key,show='●',relief='flat',bg=BG,
                 highlightbackground=LINE,highlightthickness=1).pack(fill='x',padx=pad,pady=(3,9),ipady=6)
        self.label(right,'Modèle',fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=pad)
        models=ttk.Combobox(right,textvariable=self.model,state='readonly',values=[
          'gpt-image-2.5-flare','gpt-image-2','gpt-image-2.5-sunburst'])
        models.pack(fill='x',padx=pad,pady=(3,9))
        self.label(right,'Qualité',fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=pad)
        ttk.Combobox(right,textvariable=self.quality,state='readonly',values=['low','medium','high']).pack(fill='x',padx=pad,pady=(3,8))
        self.btn(right,'Générer ce rôle (1 planche)',self._generate_one,primary=True).pack(fill='x',padx=pad,pady=3)
        self.btn(right,'Générer les rôles manquants…',self._generate_missing).pack(fill='x',padx=pad,pady=3)
        self.btn(right,'Arrêter après cette planche',self._cancel).pack(fill='x',padx=pad,pady=3)
        tk.Frame(right,bg=LINE,height=1).pack(fill='x',padx=pad,pady=13)
        self.label(right,'3. Palettes et skin tones',font=('Segoe UI',12,'bold')).pack(anchor='w',padx=pad,pady=(0,4))
        self.label(right,'Palette multicolore (base)',fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=pad)
        self.palette_combo=ttk.Combobox(right,textvariable=self.palette_var,state='readonly',
                                      values=list(self.palette_ids))
        self.palette_combo.pack(fill='x',padx=pad,pady=(3,8))
        self.palette_combo.bind('<<ComboboxSelected>>',self._style_changed)
        self.label(right,'Carnation / skin tone',fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=pad)
        self.skin_combo=ttk.Combobox(right,textvariable=self.skin_var,state='readonly',
                                   values=list(self.skin_ids))
        self.skin_combo.pack(fill='x',padx=pad,pady=(3,8))
        self.skin_combo.bind('<<ComboboxSelected>>',self._style_changed)
        self.label(right,'Chaque case colorée est modifiable (sauf la peau).',
                   fg=MUTED,font=('Segoe UI',9),wraplength=290,justify='left').pack(anchor='w',padx=pad,pady=(4,3))
        swatch_area=tk.Frame(right,bg=WHITE)
        swatch_area.pack(fill='x',padx=pad,pady=(2,7))
        self.swatches={}
        for i,(k,n) in enumerate([('peau','Peau'),('cheveux','Cheveux'),('haut','Haut'),
                                  ('bas','Bas'),('chaussures','Chaussures'),('accessoires','Objets')]):
            swatch_area.columnconfigure(i%2,weight=1)
            holder=tk.Frame(swatch_area,bg=WHITE)
            holder.grid(row=i//2,column=i%2,sticky='w',pady=3)
            if k == 'peau':
                block=tk.Label(holder,width=3,height=1,relief='solid',borderwidth=1)
            else:
                block=tk.Button(holder,width=3,height=1,relief='solid',borderwidth=1,
                    cursor='hand2',command=lambda region=k:self._choose_color(region))
            block.pack(side='left',padx=(0,6))
            caption=self.label(holder,n,fg=MUTED,font=('Segoe UI',8))
            caption.pack(side='left')
            self.swatches[k]=(block,caption,n)
        self.label(right,'Traits : #000000 (fixe)  •  Fond : #FFFFFF (fixe)',
                   fg=MUTED,font=('Segoe UI',9),wraplength=295,justify='left').pack(anchor='w',padx=pad,pady=(3,7))
        self.btn(right,'Générer une combinaison multicolore',self._random_colors).pack(fill='x',padx=pad,pady=3)
        self.btn(right,'Revenir aux couleurs de la palette',self._reset_colors).pack(fill='x',padx=pad,pady=(2,5))
        tk.Checkbutton(right,text=self.T('Voir les couleurs techniques d’origine'),
            variable=self.show_technical,command=self._refresh_previews,
            anchor='w',bg=WHITE,fg=DARK,activebackground=WHITE,
            selectcolor=WHITE,font=('Segoe UI',9),wraplength=275,
            justify='left').pack(fill='x',padx=pad,pady=(2,5))
        self.style_note=self.label(right,'',fg=MUTED,font=('Segoe UI',9),
                                 wraplength=265,justify='left')
        self.style_note.pack(anchor='w',padx=pad,pady=(0,7))
        tk.Frame(right,bg=LINE,height=1).pack(fill='x',padx=pad,pady=12)
        self.label(right,'4. Valider et exporter',font=('Segoe UI',12,'bold')).pack(anchor='w',padx=pad,pady=(0,6))
        self.approve_var=tk.BooleanVar(value=False)
        tk.Checkbutton(right,text=self.T('J’ai vérifié le personnage'),variable=self.approve_var,
            command=self._approve,anchor='w',bg=WHITE,fg=DARK,activebackground=WHITE,
            selectcolor=WHITE,font=('Segoe UI',10)).pack(fill='x',padx=pad,pady=3)
        self.btn(right,'Exporter pour Kolor / Kontexte',self._export,primary=True).pack(fill='x',padx=pad,pady=3)
        self.btn(right,'Ouvrir le dossier du projet',lambda:launch_folder(self.project)).pack(fill='x',padx=pad,pady=(3,9))

    def _fill_roles(self):
        for c in self.role_holder.winfo_children():c.destroy()
        phrase=self.search.get().casefold().strip()
        filtered=[r for r in self.data if phrase in r['nom'].casefold() or phrase in self.role_label(r).casefold() or phrase in r['id']]
        for r in filtered:
            rec=self.state_data['roles'].get(r['id'])
            sym='✓' if rec and rec.get('valide') else ('◉' if rec else '○')
            selected=r['id']==self.current
            bg=PALE if selected else WHITE
            button=tk.Button(self.role_holder,text=f' {sym}  {self.role_label(r)}',anchor='w',
                 font=('Segoe UI Semibold' if selected else 'Segoe UI',10),
                 bg=bg,fg=BRAND if selected else DARK,activebackground=PALE,
                 relief='flat',padx=8,pady=7,command=lambda k=r['id']:self.select(k))
            button.pack(fill='x',padx=5,pady=1)
        completed=len(self.state_data['roles'])
        approved=sum(bool(v.get('valide')) for v in self.state_data['roles'].values())
        self.count_label.config(text=self.fmt('{done}/38 créés · {ok}/38 vérifiés',
            '{done}/38 created · {ok}/38 reviewed',done=completed,ok=approved))
        self.progress_label.config(text=self.fmt('{done}/38 planches · {ok} vérifiées',
            '{done}/38 sheets · {ok} reviewed',done=completed,ok=approved))

    def select(self,role_id):
        self.current=role_id
        r=self.ids[role_id]
        self.main_title.config(text=self.role_label(r))
        actions=', '.join(detail_name(x,'action',self.lang) for x in r['actions'][:3])
        objects=', '.join(detail_name(x,'object',self.lang) for x in r['objets'][:2])
        self.description.config(text=self.fmt('Actions : {actions}.  Accessoires : {items}.',
                              'Actions: {actions}.  Items: {items}.',actions=actions,items=objects))
        rec=self.state_data['roles'].get(role_id)
        self.approve_var.set(bool(rec and rec.get('valide')))
        style=get_role_style(self.project,role_id,self.state_data)
        self.palette_var.set(self.palette_names.get(style['palette_id'],self.palette_names['technique']))
        self.skin_var.set(self.skin_names.get(style['skin_tone_id'],self.skin_names['technique']))
        self._show_swatches()
        self._fill_roles();self._show_preview();self._show_cards()

    def _show_preview(self):
        rec=self.state_data['roles'].get(self.current)
        if not rec:
            self.preview.config(image='',text=self.T('Aucune planche pour ce rôle\n\nCopie le prompt ou génère une planche.'),fg=MUTED)
            self.preview_tk=None;return
        src=self.project/rec['planche']
        if not src.exists():return
        width=max(170,self.preview.winfo_width()-24);height=max(170,self.preview.winfo_height()-24)
        try:
            with Image.open(src) as p: img=p.convert('RGB')
            img.thumbnail((width,height),Image.Resampling.LANCZOS)
            if not self.show_technical.get():
                style=self._current_style()
                img=recolor(img,style['palette_id'],style['skin_tone_id'],self.catalog,style['couleurs_libres'])
            self.preview_tk=ImageTk.PhotoImage(img)
            self.preview.config(image=self.preview_tk,text='')
        except (OSError,ValueError):self.preview.config(text=self.T('Erreur d’ouverture de la planche'),image='')

    def _show_cards(self):
        self.card_images=[]
        rec=self.state_data['roles'].get(self.current)
        for i,(f,thumb) in enumerate(self.choices):
            is_selected=bool(rec and rec.get('selection',0)==i)
            f.config(highlightbackground=BRAND if is_selected else LINE)
            if rec:
                src=self.project/'variantes'/self.current/f'{i+1:02}.png'
                if src.exists():
                    with Image.open(src) as p:img=p.convert('RGB')
                    img.thumbnail((127,116),Image.Resampling.LANCZOS)
                    if not self.show_technical.get():
                        style=self._current_style()
                        img=recolor(img,style['palette_id'],style['skin_tone_id'],self.catalog,style['couleurs_libres'])
                    photo=ImageTk.PhotoImage(img);self.card_images.append(photo)
                    thumb.config(image=photo,text='',height=116,width=127)
            else:thumb.config(image='',text='—',height=5,width=12)
        if rec:
            notes=[]
            q=rec['rapport'][rec['selection']]
            if q.get('a_verifier'):notes.extend(self.T(n) for n in q['a_verifier'])
            if rec.get('avertissement'):notes.append(self.T(rec['avertissement']))
            if not notes: notes=[self.T('Découpage prêt · vérifie les six aplats et la cohérence visuelle.')]
            self.alert.config(text=' • '.join(notes))
        else:self.alert.config(text=self.T('Une planche = quatre variantes du même rôle, pas quatre rôles différents.'))

    def _current_style(self):
        style=get_role_style(self.project,self.current,self.state_data)
        style['palette_id']=self.palette_ids[self.palette_var.get()]
        style['skin_tone_id']=self.skin_ids[self.skin_var.get()]
        return style

    def _refresh_previews(self):
        self._show_swatches()
        self._show_preview()
        self._show_cards()

    def _show_swatches(self):
        style=self._current_style()
        colors=get_style_colors(style['palette_id'],style['skin_tone_id'],self.catalog,style['couleurs_libres'])
        for key,(swatch,label,name) in self.swatches.items():
            swatch.configure(bg=colors[key])
            label.configure(text=f'{self.T(name)}  {colors[key]}')
        self.style_note.configure(text=self.T('Aperçu technique uniquement.') if self.show_technical.get()
            else self.T('Peau et vêtements indépendants. Noir et blanc fixes. Les PNG sources restent intacts.'))

    def _style_changed(self,event=None):
        try:
            style=self._current_style()
            set_role_style(self.project,self.current,style['palette_id'],style['skin_tone_id'])
            self.state_data=load_state(self.project)
            self.approve_var.set(bool(self.state_data['roles'].get(self.current,{}).get('valide')))
            self._refresh_previews()
            self._fill_roles()
            self.status.set(self.fmt('Palette et carnation enregistrées pour {role}. Réexporter pour appliquer les couleurs.',
                'Palette and skin tone saved for {role}. Export again to apply colors.',role=self.role_label(self.ids[self.current])))
        except Exception as e:
            messagebox.showerror(self.T('Palette invalide'),str(e))

    def _choose_color(self, region):
        """Teinte individuelle ; impossible de toucher aux contours ou au fond."""
        try:
            style=self._current_style()
            actual=get_style_colors(style['palette_id'],style['skin_tone_id'],self.catalog,
                                    style['couleurs_libres'])
            rgb, hexcode=colorchooser.askcolor(color=actual[region],
                                title=self.T('Couleur — {region}',region=self.T({'cheveux':'Cheveux','haut':'Haut','bas':'Bas','chaussures':'Chaussures','accessoires':'Objets'}[region])),parent=self)
            if not hexcode:return
            set_role_color(self.project,self.current,region,hexcode)
            self._update_after_colors(self.fmt('Couleur {region} modifiée pour {role}',
                '{region} color changed for {role}',region=region,role=self.role_label(self.ids[self.current])))
        except (ValueError,KeyError) as exc:
            messagebox.showerror(self.T('Couleur interdite'),str(exc))

    def _random_colors(self):
        """Associe une couleur distincte à chaque élément, peau inchangée."""
        try:
            rng=random.SystemRandom()
            regions=list(EDITABLE_CHANNELS)
            options={c:sorted({p[c].upper() for p in self.catalog['palettes']
                               if p['id']!='technique'}) for c in regions}
            # Mélange indépendant : pas de teinte unique sur toute la tenue.
            colors={k:rng.choice(options[k]) for k in regions}
            style=self._current_style()
            set_role_style(self.project,self.current,style['palette_id'],style['skin_tone_id'],colors)
            self._update_after_colors(self.fmt('Combinaison multicolore créée pour {role}',
                'Multicolor combination created for {role}',role=self.role_label(self.ids[self.current])))
        except Exception as exc:
            messagebox.showerror(self.T('Palette'),str(exc))

    def _reset_colors(self):
        try:
            style=self._current_style()
            set_role_style(self.project,self.current,style['palette_id'],style['skin_tone_id'],{})
            self._update_after_colors(self.msg('Couleurs individuelles réinitialisées','Custom colors reset to palette'))
        except ValueError as exc:
            messagebox.showerror(self.T('Palette'),str(exc))

    def _update_after_colors(self,msg):
        self.state_data=load_state(self.project)
        self.approve_var.set(bool(self.state_data['roles'].get(self.current,{}).get('valide')))
        self._refresh_previews();self._fill_roles()
        self.status.set(msg+self.msg('. Les contours noirs et le fond blanc restent fixes. Réexporter.',
                                        '. Black outlines and white background stay locked. Export again.'))

    def _copy_prompt(self):
        self.clipboard_clear();self.clipboard_append(prompt_role(self.ids[self.current]))
        self.status.set(self.T('Prompt copié : colle-le dans un outil de génération d’images.'))

    def _export_prompts(self):
        count=export_prompts(self.project)
        self.status.set(self.fmt('{count} prompts créés dans projet/prompts/',
                          '{count} prompts created in projet/prompts/',count=count))
        messagebox.showinfo(self.T('Prompts prêts'),self.fmt('{count} prompts ont été créés.\n\nDossier : projet/prompts/',
                        '{count} prompts created.\n\nFolder: projet/prompts/',count=count))

    def _import_sheet(self):
        path=filedialog.askopenfilename(title=self.T('Importer la planche 2 × 2'),filetypes=[(self.T('Images'),'*.png *.jpg *.jpeg *.webp')])
        if not path:return
        self._accept_sheet(self.current,path)

    def _accept_sheet(self,role_id,src):
        try:
            record=process_sheet(self.project,role_id,src)
            self.state_data=load_state(self.project)
            self.select(role_id)
            if record.get('avertissement'):
                messagebox.showwarning(self.T('Ajustement du découpage'),self.T(record['avertissement']))
            self.status.set(self.fmt('{role} : 4 variantes découpées et enregistrées.',
                        '{role}: 4 poses cropped and saved.',role=self.role_label(self.ids[role_id])))
        except Exception as e:
            messagebox.showerror(self.T('Importation impossible'),str(e))

    def _choose(self,i):
        if self.current not in self.state_data['roles']:
            self.status.set(self.T('Importe d’abord une planche pour sélectionner une pose.'));return
        choose_variant(self.project,self.current,i)
        self.state_data=load_state(self.project)
        self.select(self.current)
        self.status.set(self.fmt('Pose {number} sélectionnée; vérifier à nouveau avant export.',
                      'Pose {number} selected; review again before exporting.',number=i+1))

    def _approve(self):
        if self.current not in self.state_data['roles']:
            self.approve_var.set(False);return
        choose_variant(self.project,self.current,self.state_data['roles'][self.current]['selection'],
                       validate=self.approve_var.get())
        self.state_data=load_state(self.project)
        self._fill_roles()
        self.status.set(self.T('Rôle vérifié.') if self.approve_var.get() else self.T('Validation retirée.'))

    def _generate_one(self):self._start_batch([self.current])

    def _generate_missing(self):
        missing=[r['id'] for r in self.data if r['id'] not in self.state_data['roles']]
        if not missing:messagebox.showinfo(self.T('Terminé'),self.T('Les 38 rôles ont déjà une planche.'));return
        if not messagebox.askyesno(self.T('Confirmer la génération payante'),
            self.fmt('Générer {count} planches manquantes ?\n\n'
            'L’API facture séparément chaque génération.\n'
            'Le traitement est séquentiel et peut être interrompu après chaque planche.\n\nContinuer ?',
            'Generate {count} missing sheets?\n\n'
            'The API bills each generation separately.\n'
            'The batch runs sequentially and can be stopped after each sheet.\n\nContinue?',count=len(missing))):
            return
        self._start_batch(missing)

    def _start_batch(self,role_ids):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(self.T('Génération active'),self.T('Une série est déjà en cours.'));return
        key=self.api_key.get().strip()
        if not key:
            messagebox.showwarning(self.T('Clé API manquante'),self.T('Entre une clé API OpenAI. Elle n’est pas sauvegardée.\n\nSinon, copie les prompts et importe les planches manuellement.'))
            return
        model=self.model.get();quality=self.quality.get()
        self.stop_flag.clear()
        def work():
            for k,role_id in enumerate(role_ids):
                if self.stop_flag.is_set():break
                self.messages.put(('status',self.fmt('Génération {position}/{total} : {role}…',
                         'Generating {position}/{total}: {role}…',position=k+1,total=len(role_ids),
                         role=self.role_label(self.ids[role_id]))))
                try:
                    raw=generate_api(self.ids[role_id],key,model,quality)
                    # Décoder en mémoire. process_sheet sauve la planche et les variantes.
                    tmp=self.project/'temporaires'/f'{role_id}.png'
                    with Image.open(io.BytesIO(raw)) as picture:
                        atomic_save_image(picture.convert('RGB'),tmp)
                    record=process_sheet(self.project,role_id,tmp)
                    tmp.unlink(missing_ok=True)
                    self.messages.put(('done',role_id,record.get('avertissement')))
                except Exception as e:
                    self.messages.put(('error',role_id,str(e)))
                    # Éviter de poursuivre une série payante en état d'erreur.
                    # Un échec n'efface jamais les images déjà produites.
                    break
            self.messages.put(('finished',))
        self.worker=threading.Thread(target=work,daemon=True)
        self.worker.start()
        self.status.set(self.fmt('{count} planche(s) en cours…','{count} sheet(s) running…',count=len(role_ids)))

    def _cancel(self):
        self.stop_flag.set()
        self.status.set(self.T('Arrêt demandé : fin de la planche en cours, puis arrêt.'))

    def _poll(self):
        try:
            while True:
                event=self.messages.get_nowait()
                kind=event[0]
                if kind=='status':self.status.set(event[1])
                elif kind=='done':
                    self.state_data=load_state(self.project)
                    if event[1]==self.current:self.select(self.current)
                    else:self._fill_roles()
                    self.status.set(self.fmt('✓ {role} : planche découpée.','✓ {role}: sheet cropped.',role=self.role_label(self.ids[event[1]])))
                elif kind=='error':
                    self.status.set(self.msg('Erreur de génération : ','Generation error: ')+event[2])
                    messagebox.showerror(self.msg('Génération ','Generation ')+self.role_label(self.ids[event[1]]),event[2])
                elif kind=='finished':
                    self.status.set(self.T('Série terminée. Vérifie les planches et sélectionne une pose par rôle.'))
        except queue.Empty:pass
        if self.winfo_exists():self.after(100,self._poll)

    def _export(self):
        try:
            report=export_kontexte(self.project)
            if report['exportes']==0:
                messagebox.showinfo(self.T('Aucune image'),self.T('Importe ou génère au moins une planche.'));return
            self.status.set(self.fmt('{roles} rôles exportés avec leurs palettes · {pending} à vérifier.',
                         '{roles} roles exported with palettes · {pending} need review.',
                         roles=report['exportes'],pending=report['a_verifier']))
            messagebox.showinfo('Kontexte / Kolor export',self.fmt(
                '{roles}/38 rôles exportés.\n{sheets} planche(s) Ekole assemblée(s).\n'
                '{pending} image(s) encore à vérifier.\n\n'
                'PNG recolorisés : projet/exports/images/roles/\n'
                'PNG natifs colorés : projet/exports/images/roles_natifs/\n'
                'Sources techniques : projet/exports/images/roles_techniques/\n'
                'Planches compatibles : projet/exports/planches_ekole/\n'
                'L’export ne modifie pas le catalogue original.',
                '{roles}/38 roles exported.\n{sheets} Ekole sheet(s) assembled.\n'
                '{pending} image(s) still require review.\n\n'
                'Recolored PNGs: projet/exports/images/roles/\n'
                'Native recolored PNGs: projet/exports/images/roles_natifs/\n'
                'Technical sources: projet/exports/images/roles_techniques/\n'
                'Compatible sheets: projet/exports/planches_ekole/\n'
                'Export does not modify the original catalog.',
                roles=report['exportes'],sheets=report['planches'],pending=report['a_verifier']))
        except Exception as e:messagebox.showerror(self.T('Export impossible'),str(e))

    def _on_close(self):
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno(self.T('Quitter Kolor Studio'),
                 self.T('Une génération est en cours. Quitter l’interrompra peut-être sans sauvegarder la planche active.\nQuitter ?')):
                return
        self.stop_flag.set();self.destroy()


if __name__=='__main__':
    Studio().mainloop()
