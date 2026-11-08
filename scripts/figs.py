# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, json, re, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Inter' in f and 'Display' not in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family':'Inter','font.size':15,'axes.spines.top':False,'axes.spines.right':False,'text.color':'#2B2A28','axes.labelcolor':'#2B2A28','xtick.color':'#6B665C','ytick.color':'#2B2A28'})
BG='#F7F3EA'; INK='#2B2A28'; GRY='#B9B2A3'; DGR='#6B665C'; ACC='#B8860B'; ACC2='#8A3B12'
D='/mnt/user-data/uploads/1.SeminarioOntologiaGrafoConhecimento/'
def fin(fig,name,title,sub=None,src=None):
    fig.patch.set_facecolor(BG)
    fig.text(0.02,0.965,title,fontsize=22,fontweight='bold',va='top',ha='left',wrap=True)
    if sub: fig.text(0.02,0.90,sub,fontsize=14,color=DGR,va='top',ha='left')
    if src: fig.text(0.02,0.012,'Fonte: '+src,fontsize=10.5,color=DGR,ha='left')
    fig.savefig(f'fig/{name}.png',dpi=200,facecolor=BG); plt.close(fig)

# ---- F1 aliases ----
m=pd.read_csv('mentions_raw.csv'); a=m[m.entidade=='Aragorn II Elessar'].groupby('alias').n.sum()
al=a[a>0].sort_values(); tot=al.sum(); print(al.to_dict(), tot, 1-al['Aragorn']/tot)
fig,ax=plt.subplots(figsize=(11,6)); ax.set_facecolor(BG)
cols=[ACC if k!='Aragorn' else GRY for k in al.index]
ax.barh(al.index,al.values,color=cols,height=.6)
for y,(k,v) in enumerate(al.items()): ax.text(v+8,y,f'{v}',va='center',fontsize=15,fontweight='bold')
ax.set_xlim(0,820); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.spines['left'].set_visible(False); ax.tick_params(left=False,labelsize=16)
ax.text(500,1.45,f'{(tot-al["Aragorn"])/tot:.0%} das menções\nnão usam o nome "Aragorn"',fontsize=17,color=ACC2,fontweight='bold',va='center')
fig.subplots_adjust(top=.78,left=.14,bottom=.1,right=.97)
fin(fig,'f1_aragorn_aliases','Buscar só "Aragorn" no livro deixa de fora 1 em cada 4 menções','Menções ao mesmo personagem no texto de O Senhor dos Anéis, por nome usado',src='LordOfTheRingsBook.json (62 capítulos); contagem por casamento de padrões, elaboração própria')
json.dump({'aragorn':int(al['Aragorn']),'strider':int(al['Strider']),'elessar':int(al['Elessar']),'total':int(tot)},open('stats_hook.json','w'))

# ---- F2 rótulos de povo ----
ch=pd.read_csv(D+'lotr_characters.csv'); rc=ch.race.fillna('(sem rótulo)').value_counts()
POV={'Men':'Homem','Hobbits':'Hobbit','Hobbit':'Hobbit','Elves':'Elfo','Elf':'Elfo','Dwarves':'Anão','Dwarf':'Anão','Dwarven':'Anão','Orcs':'Orc','Orc':'Orc'}
top=rc.drop('(sem rótulo)').head(12); lab_cnt=ch.race.nunique()
print('rótulos distintos',lab_cnt, 'sem rótulo',rc['(sem rótulo)'], 'total',len(ch))
colmap={'Homem':'#B07A4B','Hobbit':'#5B8C5A','Elfo':'#4A78A8','Anão':'#8A5A9E','Orc':'#7A2E2E'}
fig,ax=plt.subplots(figsize=(12,6.6)); ax.set_facecolor(BG)
items=list(top.items())[::-1]
for i,(k,v) in enumerate(items):
    c=colmap.get(POV.get(k),GRY); ax.barh(i,v,color=c,height=.62)
    ax.text(v+4,i,f'{v}',va='center',fontsize=13)
ax.set_yticks(range(len(items))); ax.set_yticklabels([k for k,_ in items],fontsize=14); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.spines['left'].set_visible(False); ax.tick_params(left=False)
ax.text(200,3.2,f'{lab_cnt} rótulos distintos\npara ~8 povos reais.\n\n{rc["(sem rótulo)"]} de {len(ch)} personagens\n({rc["(sem rótulo)"]/len(ch):.0%}) sem rótulo algum',fontsize=15,color=ACC2,fontweight='bold',va='center')
fig.subplots_adjust(top=.80,left=.17,bottom=.08,right=.97)
fin(fig,'f2_rotulos_povo','47 grafias para cerca de 8 povos, e 15% das personagens sem povo','Contagem de personagens por rótulo original de "race" (colorido = povo após normalização)',src='lotr_characters.csv (911 personagens); elaboração própria')

# ---- F4 palavras ----
wr=pd.read_csv('falas_resolvidas.csv'); w0=pd.read_csv(D+'WordsByCharacter.csv').groupby('Character').Words.sum()
base=w0.sort_values(ascending=False).head(9)
smg=w0['Smeagol']; gol=w0['Gollum']
rank0=list(w0.sort_values(ascending=False).index).index('Gollum')+1
w1=w0.copy(); w1['Gollum']=gol+smg; w1=w1.drop('Smeagol'); rank1=list(w1.sort_values(ascending=False).index).index('Gollum')+1
print('Gollum',gol,'Smeagol',smg,'rank',rank0,'->',rank1)
top=w1.sort_values(ascending=False).head(9)[::-1]
fig,ax=plt.subplots(figsize=(12,6.8)); ax.set_facecolor(BG)
for i,(k,v) in enumerate(top.items()):
    if k=='Gollum':
        ax.barh(i,gol,color=ACC,height=.62); ax.barh(i,smg,left=gol,color='#E3C77B',height=.62)
        ax.text(v+30,i,f'{int(v):,}'.replace(',','.'),va='center',fontsize=14,fontweight='bold',color=ACC2)
    else:
        ax.barh(i,v,color=GRY,height=.62); ax.text(v+30,i,f'{int(v):,}'.replace(',','.'),va='center',fontsize=14)
ax.set_yticks(range(len(top))); ax.set_yticklabels(top.index,fontsize=15); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.spines['left'].set_visible(False); ax.tick_params(left=False)
gi=list(top.index).index('Gollum')
ax.text(2000,gi,f'= Gollum ({int(gol):,}) + Sméagol ({int(smg):,})'.replace(',','.'),va='center',fontsize=13.5,color=ACC2)
ax.text(3000,1.3,f'Antes de unir as duas\nidentidades, Gollum era\no {rank0}º; depois, o {rank1}º.',fontsize=15,fontweight='bold',color=ACC2)
ax.set_xlim(0,5400); fig.subplots_adjust(top=.80,left=.12,bottom=.08,right=.97)
fin(fig,'f4_palavras','Unir Sméagol a Gollum muda o ranking de falas nos filmes','Palavras faladas nas três partes de O Senhor dos Anéis (Peter Jackson), 9 maiores falantes',src='WordsByCharacter.csv; entidades unificadas via owl:sameAs')
json.dump({'gollum':int(gol),'smeagol':int(smg),'rank0':rank0,'rank1':rank1},open('stats_words.json','w'))

# ---- F5 timeline do Anel ----
bear=[('Sauron',-1841,0,False,'tomado à força por Isildur'),('Isildur',0,2,False,'morto; Anel cai no Anduin'),('Déagol',2463,2463,False,'assassinado por Sméagol'),
('Sméagol / Gollum',2463,2941,False,'perde o Anel na caverna'),('Bilbo',2941,3001,True,'entrega a Frodo'),('Frodo (1ª posse)',3001,3019,False,'capturado em Cirith Ungol'),
('Sam',3019,3019,True,'devolve a Frodo'),('Frodo (2ª posse)',3019,3019,False,'Anel destruído')]
n=len(bear)
fig=plt.figure(figsize=(13,6.8)); gs=fig.add_gridspec(1,2,width_ratios=[1,1.7],wspace=.04)
a1=fig.add_subplot(gs[0]); a2=fig.add_subplot(gs[1])
for ax in (a1,a2): ax.set_facecolor(BG); ax.set_ylim(-.9,n-.4); ax.spines['left'].set_visible(False); ax.set_yticks([])
a1.set_xlim(-1900,60); a2.set_xlim(2420,3420); a2.spines['left'].set_visible(False)
for i,(k,x0,x1,vol,how) in enumerate(bear):
    y=n-1-i; c=ACC if vol else GRY
    ax=a1 if x1<=2 else a2
    w=max(x1-x0,9); ax.barh(y,w,left=x0 if x1-x0>=9 else x0-4,color=c,height=.55)
    a1.text(-1950 if True else 0,y,k,ha='right',va='center',fontsize=13.5,fontweight='bold' if vol else 'normal',color=INK) if False else None
    t=a2.text(max(x1,x0)+30,y,how,va='center',fontsize=12.5,color=ACC2 if vol else DGR,fontweight='bold' if vol else 'normal') if x1>2 else a1.text(max(x1,x0)+40 if x1==0 else 80,y,how,va='center',fontsize=12.5,color=DGR,ha='left') if False else None
    if x1<=2: a1.text(x1+(60 if x1==0 else 60),y,'' ,fontsize=1)
for i,(k,x0,x1,vol,how) in enumerate(bear):
    y=n-1-i
    fig.text(0.205,0.0,'')
    (a1 if x1<=2 else a2)
# nomes dos portadores no eixo y esquerdo, via texto no a1
for i,(k,x0,x1,vol,how) in enumerate(bear):
    y=n-1-i; a1.text(-1930,y+0.0,'',fontsize=1)
a1.set_yticks(range(n)); a1.set_yticklabels([b[0] for b in bear][::-1],fontsize=13.5)
for lab,b in zip(a1.get_yticklabels(),bear[::-1]):
    if b[3]: lab.set_fontweight('bold')
a1.tick_params(left=False)
# rótulos do término
a1.text(60,n-1,'',fontsize=1)
a1.annotate('tomado à força',xy=(0,n-1),xytext=(-1000,n-1.5),fontsize=12.5,color=DGR,ha='center') if False else None
a1.text(-1840+30,n-1+.42,'forja do Anel (SA 1600)',fontsize=11.5,color=DGR)
a1.text(-900,n-1-.0,'',fontsize=1)
a1.text(-1830,n-2.62,'',fontsize=1)
a1.text(-1500,n-2,'toma o Anel a Sauron (SA 3441)  →  morre; Anel cai no Anduin (TA 2)',fontsize=11.5,color=DGR,ha='left') if False else None
a1.text(60,n-2,'',fontsize=1)
a1.set_xticks([-1841,0]); a1.set_xticklabels(['SA 1600','SA 3441'],fontsize=11.5)
a2.set_xticks([2463,2941,3019]); a2.set_xticklabels(['TA 2463','TA 2941','TA 3019'],fontsize=11.5)
for ax in (a1,a2): ax.tick_params(axis='x',length=3)
a1.spines['right'].set_visible(False)
a1.text(-950,n-3.1,'Isildur: perdeu o Anel no Anduin (TA 2)\n2.461 anos sem portador',ha='center',fontsize=12.5,color=DGR,style='italic') if False else None
a1.text(-900,2.6,'2.461 anos sem portador\n(Anel no leito do Anduin)',ha='center',va='center',fontsize=13,color=DGR,style='italic')
for i,(k,x0,x1,vol,how) in enumerate(bear):
    y=n-1-i
    if x1<=2: a1.text(80 if False else 15,y,'',fontsize=1)
a1.text(-1840,n-1-.0,'',fontsize=1)
for i,(k,x0,x1,vol,how) in enumerate(bear):
    y=n-1-i
    if x1<=2: a1.text(-1800 if k=='Isildur' else -1500,y-.0,'',fontsize=1)
# rótulos dos dois primeiros dentro do painel esquerdo
a1.text(-1800,n-1+.0,'',fontsize=1)
a1.text(-1780,n-1-.42,'',fontsize=1)
a1.text(-860,n-1,how_ := 'Sauron: tomado à força',fontsize=1) if False else None
a1.text(-1000,n-2+.0,'',fontsize=1)
a1.text(-1870,n-1.62,'',fontsize=1)
a1.text(-900,n-1,'termina: tomado à força por Isildur',fontsize=12,color=DGR,ha='center',va='center',bbox=dict(fc=BG,ec='none',pad=1)) if False else None
a1.text(-880,n-1,'  Anel tomado à força por Isildur',fontsize=12,color=BG,ha='center',va='center')
a1.text(-1800,n-2,'morre; Anel cai no Anduin',fontsize=12,color=DGR,ha='left',va='center')
fig.text(0.02,0.07,'■ Posse encerrada por entrega voluntária (2 de 8, ambas entre hobbits)',fontsize=13.5,color=ACC2,fontweight='bold')
fig.subplots_adjust(top=.80,left=.17,bottom=.17,right=.99)
fin(fig,'f5_timeline_anel','O Um Anel só foi entregue voluntariamente duas vezes, e sempre por hobbits','Posses do Um Anel como intervalos de tempo (cálculo de eventos): cada barra é um fluente Posse(portador, Anel), com início e fim',src='Curadoria a partir da obra (Apêndice B); eixo = ano relativo ao início da Terceira Era; escala quebrada entre TA 2 e TA 2463')

# ---- F6 heatmap presença ----
mm=m.groupby(['cap_idx','entidade']).n.sum().unstack(fill_value=0)
rows=['Frodo Baggins','Samwise Gamgee','Gollum','Meriadoc Brandybuck','Peregrin Took','Gandalf','Aragorn II Elessar','Legolas','Gimli','Boromir','Saruman','Sauron']
lab={'Frodo Baggins':'Frodo','Samwise Gamgee':'Sam','Gollum':'Gollum / Sméagol','Meriadoc Brandybuck':'Merry','Peregrin Took':'Pippin','Gandalf':'Gandalf','Aragorn II Elessar':'Aragorn','Legolas':'Legolas','Gimli':'Gimli','Boromir':'Boromir','Saruman':'Saruman','Sauron':'Sauron'}
M=mm[rows].T.values.astype(float); Z=np.log1p(M)
nine=['Frodo Baggins','Samwise Gamgee','Meriadoc Brandybuck','Peregrin Took','Gandalf','Aragorn II Elessar','Legolas','Gimli','Boromir']
trio=['Frodo Baggins','Samwise Gamgee','Gollum']; nine9=trio+['Aragorn II Elessar','Gandalf','Legolas','Gimli','Meriadoc Brandybuck','Peregrin Took']
blocks={'I-II':(1,22),'III':(23,33),'IV':(34,43),'V':(44,53),'VI':(54,62)}
share={k:float(mm.loc[a:b,trio].values.sum()/mm.loc[a:b,nine9].values.sum()) for k,(a,b) in blocks.items()}; print(share)
json.dump(share,open('stats_heat.json','w'))
from matplotlib.colors import LinearSegmentedColormap
cm=LinearSegmentedColormap.from_list('c',[BG,'#EAD9A8','#C8962E','#7A4A0A'])
fig,ax=plt.subplots(figsize=(14,6.8)); ax.set_facecolor(BG)
ax.imshow(Z,aspect='auto',cmap=cm,interpolation='nearest',extent=[.5,62.5,len(rows)-.5,-.5])
ax.set_yticks(range(len(rows))); ax.set_yticklabels([lab[r] for r in rows],fontsize=13.5); ax.set_xticks([1,22,33,43,53,62]); ax.set_xticklabels(['1','22','33','43','53','62'],fontsize=12)
for x in (33.5,43.5,53.5): ax.axvline(x,color=INK,lw=1)
ax.axvline(22.5,color=ACC2,lw=3)
for (nm,(a,b)),txt in zip(blocks.items(),['Livros I–II ','Livro III','Livro IV','Livro V','Livro VI']):
    ax.text((a+b)/2,-.8,txt,ha='center',fontsize=12.5,color=DGR)
    if nm!='I-II': ax.text((a+b)/2,len(rows)+.35,f'trio: {share[nm]:.0%}',ha='center',va='top',fontsize=11.5,color=ACC2 if share[nm]>.5 else DGR,fontweight='bold' if share[nm]>.5 else 'normal')
ax.text(22.5,-.8,'◀ Quebra',ha='right',fontsize=12,color=ACC2,fontweight='bold')
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_xlabel('Capítulo (1–62)   |   “trio” = % das menções de Frodo+Sam+Gollum entre 9 personagens do bloco',fontsize=12,labelpad=36)
fig.subplots_adjust(top=.80,left=.14,bottom=.20,right=.98)
fin(fig,'f6_presenca','Depois da quebra, o livro alterna dois fios: o grupo disperso e a dupla Frodo–Sam','Menções por capítulo (mais escuro = mais menções). A relação "membro da Sociedade" vale só entre o Conselho e a Quebra: é um fluente',src='LordOfTheRingsBook.json; aliases resolvidos (Passolargo, Sméagol etc.); % calculado entre 9 personagens; elaboração própria')
print('ok')
