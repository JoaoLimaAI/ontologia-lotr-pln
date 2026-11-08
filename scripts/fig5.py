# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Inter' in f and 'Display' not in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family':'Inter','text.color':'#2B2A28'})
BG='#F7F3EA'; BAND='#EFE8D8'; GRY='#B9B2A3'; DGR='#6B665C'; ACC='#B8860B'; ACC2='#8A3B12'
rows=[('Sauron',-1841,0,False,'Isildur toma o Anel à força'),('Isildur',0,2,False,'Morre; o Anel cai no rio Anduin'),('Déagol',2463,2463,False,'Assassinado por Sméagol'),
('Sméagol / Gollum',2463,2941,False,'Perde o Anel numa caverna'),('Bilbo',2941,3001,True,'Entrega o Anel a Frodo'),('Frodo (1ª posse)',3001,3019,False,'Capturado em Cirith Ungol'),
('Sam',3019,3019,True,'Devolve o Anel a Frodo'),('Frodo (2ª posse)',3019,3019,False,'O Anel é destruído')]
n=len(rows)
fig=plt.figure(figsize=(13,6.8)); gs=fig.add_gridspec(1,3,width_ratios=[1.0,1.5,1.25],wspace=.05)
a1,a2,a3=[fig.add_subplot(gs[i]) for i in range(3)]
for ax in (a1,a2,a3):
    ax.set_facecolor(BG); ax.set_ylim(-.6,n-.4)
    for i in range(n):
        if i%2==0: ax.axhspan(n-1-i-.5,n-1-i+.5,color=BAND,zorder=0)
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.set_yticks([]); 
a1.set_xlim(-1900,300); a2.set_xlim(2420,3100)
a3.axis('off')
for i,(k,x0,x1,vol,how) in enumerate(rows):
    y=n-1-i; ax=a1 if x1<=2 else a2; c=ACC if vol else GRY
    mw=28 if ax is a1 else 10; w=max(x1-x0,mw); ax.barh(y,w,left=x0 if x1-x0>=mw else x0-mw/2,color=c,height=.5,zorder=2)
    a3.text(0.02,y,how,va='center',fontsize=13,color=ACC2 if vol else '#2B2A28',fontweight='bold' if vol else 'normal',transform=a3.get_yaxis_transform())
a1.set_yticks(range(n)); a1.set_yticklabels([r[0] for r in rows][::-1],fontsize=13.5); a1.tick_params(left=False)
for lab,r in zip(a1.get_yticklabels(),rows[::-1]):
    if r[3]: lab.set_fontweight('bold')
a1.set_xticks([-1841,0]); a1.set_xticklabels(['SA 1600','SA 3441\n(TA 0)'],fontsize=12)
a2.set_xticks([2463,2941,3019]); a2.set_xticklabels(['TA 2463','TA 2941','TA 3019'],fontsize=12)
plt.setp(a2.get_xticklabels()[1],ha='right'); plt.setp(a2.get_xticklabels()[2],ha='left')
a1.set_title('Até o início da Terceira Era\n(escala em milênios)',fontsize=12.5,color=DGR,loc='left')
a2.set_title('De TA 2463 a TA 3019\n(escala em anos)',fontsize=12.5,color=DGR,loc='left')
a3.set_title('Como a posse terminou',fontsize=12.5,color=DGR,loc='left')
fig.subplots_adjust(top=.74,left=.15,bottom=.15,right=.985)
fig.patch.set_facecolor(BG)
fig.text(0.02,0.965,'Cada posse do Anel tem início, fim e um evento que a encerra',fontsize=22,fontweight='bold',va='top')
fig.text(0.02,0.90,'Cada barra é um fluente Posse(portador, Anel). Em destaque: as duas posses encerradas por entrega voluntária',fontsize=14,color=DGR,va='top')
fig.text(0.02,0.02,'Fonte: curadoria a partir da obra (Apêndice B de O Senhor dos Anéis); datas aproximadas; SA = Segunda Era, TA = Terceira Era',fontsize=10.5,color=DGR)
fig.savefig('fig/f5_timeline_anel.png',dpi=200,facecolor=BG)
