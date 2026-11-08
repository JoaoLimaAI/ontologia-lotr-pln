# -*- coding: utf-8 -*-
"""Constrói a ontologia (TBox) e o grafo de conhecimento (ABox) da Terra-média.
Fontes: lotr_characters.csv, Characters.csv, WordsByCharacter.csv, Movies.csv, LordOfTheRingsBook.json (via mentions_raw.csv)
+ camada curada manualmente (marcada com lotr:proveniencia 'curadoria')."""
import re, unicodedata, json, pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS
from rdflib.collection import Collection
D='/mnt/user-data/uploads/1.SeminarioOntologiaGrafoConhecimento/'
L=Namespace('http://example.org/lotr#'); g=Graph()
for p,n in [('lotr',L),('owl',OWL),('rdfs',RDFS),('skos',SKOS),('dct',DCTERMS)]: g.bind(p,n)

def slug(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode()
    return re.sub(r'[^A-Za-z0-9]+','_',s).strip('_')
def C(name,label,parent=None,comment=None):
    u=L[name]; g.add((u,RDF.type,OWL.Class)); g.add((u,RDFS.label,Literal(label,lang='pt')))
    if parent: g.add((u,RDFS.subClassOf,L[parent]))
    if comment: g.add((u,RDFS.comment,Literal(comment,lang='pt')))
    return u
def OP(name,label,dom=None,rng=None,types=(),inv=None,sub=None):
    u=L[name]; g.add((u,RDF.type,OWL.ObjectProperty)); g.add((u,RDFS.label,Literal(label,lang='pt')))
    if dom: g.add((u,RDFS.domain,L[dom]))
    if rng: g.add((u,RDFS.range,L[rng]))
    for t in types: g.add((u,RDF.type,t))
    if inv: g.add((u,OWL.inverseOf,L[inv]))
    if sub: g.add((u,RDFS.subPropertyOf,L[sub]))
def DP(name,label,dom=None,rng=XSD.string):
    u=L[name]; g.add((u,RDF.type,OWL.DatatypeProperty)); g.add((u,RDFS.label,Literal(label,lang='pt')))
    if dom: g.add((u,RDFS.domain,L[dom]))
    g.add((u,RDFS.range,rng))

# ============ TBox ============
C('Elemento','Elemento da Terra-média',comment='Raiz da ontologia superior.')
for n,l,p in [('Ser','Ser','Elemento'),('Lugar','Lugar','Elemento'),('Artefato','Artefato','Elemento'),('Grupo','Grupo','Elemento'),
              ('Evento','Evento','Elemento'),('Obra','Obra','Elemento'),('Posse','Posse (fluente reificado)','Elemento'),
              ('Participacao','Participação em grupo (fluente reificado)','Elemento'),('Mencao','Menção em capítulo','Elemento'),
              ('ParticipacaoFalada','Participação falada em filme','Elemento')]: C(n,l,p)
C('Personagem','Personagem','Ser'); C('Criatura','Criatura','Ser')
C('Animal','Animal','Criatura'); C('Aranha','Grande Aranha','Criatura'); C('Aguia','Grande Águia','Criatura'); C('Troll','Troll','Criatura'); C('Dragao','Dragão','Criatura')
povos=[('Hobbit','Hobbit'),('Elfo','Elfo'),('Anao','Anão'),('Homem','Homem'),('Ent','Ent'),('Orc','Orc'),('Ainur','Ainur')]
for n,l in povos: C(n,l,'Personagem')
C('MeioElfo','Meio-elfo','Personagem'); g.add((L.MeioElfo,RDFS.subClassOf,L.Elfo)); g.add((L.MeioElfo,RDFS.subClassOf,L.Homem))  # herança múltipla (Norvig 12.5)
C('UrukHai','Uruk-hai','Orc'); C('Maia','Maia','Ainur'); C('Istari','Istari (Mago)','Maia'); C('Balrog','Balrog','Maia')
C('Espectro','Espectro / morto-vivo','Personagem'); C('Metamorfo','Metamorfo','Personagem')
C('Nazgul','Nazgûl','Espectro'); g.add((L.Nazgul,RDFS.subClassOf,L.Homem))
# Disjunção parcial: povos "puros" são disjuntos entre si (Norvig: Disjuntos / Partição).
pure=['Hobbit','Anao','Ent','Orc','Ainur','Elfo','Homem']
for i,a in enumerate(pure):
    for b in pure[i+1:]:
        if 'Ainur' in (a,b) and ({a,b}&{'Elfo','Homem'}): continue   # v2: Lúthien (Elfo+Maia) refutou a v1 que separava Ainur de Elfo
        if {a,b}=={'Elfo','Homem'}: continue   # MeioElfo exige interseção Elfo∩Homem
        g.add((L[a],OWL.disjointWith,L[b]))
for n,l,p in [('Reino','Reino','Lugar'),('Regiao','Região','Lugar'),('Fortaleza','Fortaleza / cidade','Lugar')]: C(n,l,p)
C('Anel','Anel','Artefato'); C('AnelDePoder','Anel de Poder','Anel'); C('UmAnel','O Um Anel','AnelDePoder')
C('SociedadeDoAnel','Sociedade do Anel','Grupo')
C('Livro','Livro','Obra'); C('Capitulo','Capítulo','Obra'); C('Filme','Filme','Obra'); C('SerieDeFilmes','Série de filmes','Obra')
C('PortadorDeAnel','Portador de Anel',  'Personagem',comment='Classe DEFINIDA: equivale a quem já teve posse de algum Anel de Poder (inferida pelo raciocinador).')
# definição formal (abaixo): PortadorDeAnel ≡ Personagem ⊓ ∃jaPortou.AnelDePoder
OP('portador','portador',dom='Posse',rng='Personagem',inv='ePortadorEm'); OP('anel','anel',dom='Posse',rng='Anel')
OP('iniciadaPor','iniciada por (Inicia)',dom='Posse',rng='Evento'); OP('terminadaPor','terminada por (Termina)',dom='Posse',rng='Evento')
OP('jaPortou','já portou',dom='Personagem',rng='Anel',inv='foiPortadoPor')
chain=BNode(); Collection(g,chain,[L.ePortadorEm,L.anel]); g.add((L.jaPortou,OWL.propertyChainAxiom,chain))
rr=BNode(); g.add((rr,RDF.type,OWL.Restriction)); g.add((rr,OWL.onProperty,L.jaPortou)); g.add((rr,OWL.someValuesFrom,L.AnelDePoder))
eq=BNode(); Collection(g,eq,[L.Personagem,rr]); ec=BNode(); g.add((ec,RDF.type,OWL.Class)); g.add((ec,OWL.intersectionOf,eq))
g.add((L.PortadorDeAnel,OWL.equivalentClass,ec))
OP('conjugeDe','cônjuge de',dom='Personagem',rng='Personagem',types=[OWL.SymmetricProperty])
OP('ancestralDe','ancestral de',dom='Personagem',rng='Personagem',types=[OWL.TransitiveProperty],inv='descendenteDe')
OP('paiOuMaeDe','pai/mãe de',dom='Personagem',rng='Personagem',inv='filhoOuFilhaDe',sub='ancestralDe')
OP('membroDe','membro de',dom='Personagem',rng='Grupo'); OP('habitaEm','habita / governa',dom='Personagem',rng='Lugar')
OP('serveA','serve a',dom='Personagem',rng='Personagem')
OP('personagemRef','personagem',rng='Personagem'); OP('grupoRef','grupo',dom='Participacao',rng='Grupo')
OP('capituloRef','capítulo',dom='Mencao',rng='Capitulo'); OP('filmeRef','filme',dom='ParticipacaoFalada',rng='Filme')
OP('parteDe','parte de',dom='Obra',rng='Obra')
for p in ['participante']: OP(p,'participante',dom='Participacao',rng='Personagem')
OP('iniciadaPorP','participação iniciada por',dom='Participacao',rng='Evento'); OP('terminadaPorP','participação terminada por',dom='Participacao',rng='Evento')
DP('proveniencia','proveniência'); DP('rotuloOriginalPovo','rótulo original de povo/raça (dataset)'); DP('nascimentoTexto','nascimento (texto original)'); DP('morteTexto','morte (texto original)')
DP('nascimentoAno','nascimento (ano relativo ao início da Terceira Era)',rng=XSD.integer); DP('morteAno','morte (ano relativo ao início da Terceira Era)',rng=XSD.integer)
DP('genero','gênero'); DP('urlWiki','URL na wiki de origem',rng=XSD.anyURI); DP('inicioAno','início (ano relativo)',rng=XSD.integer); DP('fimAno','fim (ano relativo)',rng=XSD.integer)
DP('ordem','ordem cronológica',rng=XSD.integer); DP('palavras','palavras faladas',rng=XSD.integer); DP('ocorrencias','ocorrências no capítulo',rng=XSD.integer)
for n in ['duracaoMin','orcamentoMi','bilheteriaMi','indicacoesOscar','vitoriasOscar','notaRT']: DP(n,n,rng=XSD.decimal)

# ============ ABox: personagens do dataset ============
ch=pd.read_csv(D+'lotr_characters.csv'); wiki=pd.read_csv(D+'Characters.csv')
ch.loc[ch.name=='owyn','name']='Éowyn'          # regra de limpeza: perda de caracteres acentuados na origem
wiki.loc[wiki.Name=='owyn','Name']='Éowyn'
wiki_url=dict(zip(wiki.Name,wiki.Url))
POVO={'men':['Homem'],'human':['Homem'],'rohirrim':['Homem'],'hobbits':['Hobbit'],'hobbit':['Hobbit'],'elves':['Elfo'],'elf':['Elfo'],'noldor':['Elfo'],
 'dwarves':['Anao'],'dwarf':['Anao'],'dwarven':['Anao'],'ainur':['Ainur'],'maiar':['Maia'],'god':['Ainur'],'half-elven':['MeioElfo'],
 'orcs':['Orc'],'orc':['Orc'],'goblin':['Orc'],'uruk-hai':['UrukHai'],'black uruk':['UrukHai'],'ents':['Ent'],'onodrim':['Ent'],
 'dragons':['Dragao'],'dragon':['Dragao'],'urulóki':['Dragao'],'balrog':['Balrog'],'balrogs':['Balrog'],'great eagles':['Aguia'],'eagles':['Aguia'],'eagle':['Aguia'],
 'great spiders':['Aranha'],'stone-trolls':['Troll'],'wraith':['Nazgul'],'undead':['Espectro'],'skin-changer':['Metamorfo'],'werewolves':['Criatura'],
 'raven':['Animal'],'horse':['Animal'],'wolfhound':['Animal'],'vampire':['Criatura'],'drúedain':['Homem']}
def eras(txt):
    """ano relativo ao início da Terceira Era (TA 0). SA y -> y-3441 ; FA y -> y-4031 ; FO y -> 3021+y ; ano nu 1000-3100 -> TA (heurística)"""
    if not isinstance(txt,str): return None
    m=re.search(r'\b(TA|SA|FA|FO)\s*(\d{1,4})\b',txt)
    if m:
        e,y=m.group(1),int(m.group(2)); return {'TA':y,'SA':y-3441,'FA':y-4031,'FO':3021+y}[e]
    m=re.search(r'\b(2[0-9]{3}|30[0-9]{2})\b',txt)
    return int(m.group(1)) if m else None
name2uri={}; used=set()
for _,r in ch.iterrows():
    s=slug(r['name']); 
    while s in used: s+='_2'
    used.add(s); u=L[s]; name2uri[r['name']]=u
    g.add((u,RDF.type,L.Personagem)); g.add((u,RDFS.label,Literal(r['name'])))
    g.add((u,L.proveniencia,Literal('dataset:lotr_characters.csv')))
    raw=r['race']
    if isinstance(raw,str):
        g.add((u,L.rotuloOriginalPovo,Literal(raw)))
        for tok in [t.strip().lower() for t in raw.split(',')]:
            for cls in POVO.get(tok,[]): g.add((u,RDF.type,L[cls]))
    for col,pn,an in [('birth','nascimentoTexto','nascimentoAno'),('death','morteTexto','morteAno')]:
        v=r[col]
        if isinstance(v,str):
            g.add((u,L[pn],Literal(v)))
            y=eras(v)
            if y is not None: g.add((u,L[an],Literal(y,datatype=XSD.integer)))
    if isinstance(r['gender'],str):
        gv=r['gender'].lower(); gv='Masculino' if 'male' in gv and 'fe' not in gv else ('Feminino' if 'female' in gv else None)
        if gv: g.add((u,L.genero,Literal(gv)))
    if r['name'] in wiki_url: g.add((u,L.urlWiki,Literal(wiki_url[r['name']],datatype=XSD.anyURI)))
# cônjuges a partir do texto (apenas quando o nome do cônjuge existe como entidade)
n_sp=0; naive_pairs=[]; fixed=[]
rec=dict(zip(ch.name,ch.spouse))
def povos_of(nm):
    raw=ch.loc[ch.name==nm,'race'].iloc[0] if (ch.name==nm).any() else None
    out=set()
    if isinstance(raw,str):
        for tok in [t.strip().lower() for t in raw.split(',')]:
            for c in POVO.get(tok,[]): out|={'Elfo','Homem'} if c=='MeioElfo' else ({'Elfo'} if c=='Elfo' else ({'Homem'} if c=='Homem' else {c}))
    return out
for _,r in ch.iterrows():
    sp=r['spouse']
    if not isinstance(sp,str) or 'Unnamed' in sp: continue
    naive = sp if sp in name2uri else None
    cands=[n for n in name2uri if n==sp or n.startswith(sp+' ') or n.startswith(sp+' (')]
    recip=[n for n in cands if rec.get(n)==r['name'] or (isinstance(rec.get(n),str) and rec.get(n).startswith(r['name']))]
    pick = recip[0] if recip else naive
    if naive:
        A,B=povos_of(r['name']),povos_of(naive)
        if A and B and not (A&B): naive_pairs.append((r['name'],naive))
    if pick:
        if naive and pick!=naive: fixed.append((r['name'],naive,pick))
        g.add((name2uri[r['name']],L.conjugeDe,name2uri[pick])); n_sp+=1
# lugares (realm)
reinos={'Gondor','Rohan','Arnor','Arthedain','Númenor','Reunited Kingdom','Doriath','Rivendell','Lothlórien','Shire','Isengard','Mordor','Eregion'}
for _,r in ch.iterrows():
    if isinstance(r['realm'],str):
        for p in [x.strip() for x in r['realm'].split(',') if x.strip()]:
            lu=L[slug(p)]
            if (lu,RDF.type,None) not in g:
                g.add((lu,RDF.type,L.Reino if p in reinos else L.Lugar)); g.add((lu,RDFS.label,Literal(p)))
            g.add((name2uri[r['name']],L.habitaEm,lu))

# ============ Camada curada ============
CUR=Literal('curadoria')
def P(nm,label=None,cls=None,new=False):
    if nm in name2uri: return name2uri[nm]
    u=L[slug(nm)]; name2uri[nm]=u; g.add((u,RDF.type,L.Personagem)); g.add((u,RDFS.label,Literal(label or nm)))
    g.add((u,L.proveniencia,CUR))
    if cls: g.add((u,RDF.type,L[cls]))
    return u
def prov(u): g.add((u,L.proveniencia,CUR))
for nm,c in [('Éomer','Homem'),('Eldarion','Homem'),('Elendil','Homem')]: u=P(nm,cls=c)
# tipos curados que o dataset deixa vazios / equivocados
for nm,c in [('Gandalf','Istari'),('Saruman','Istari'),('Radagast','Istari'),('Gollum','Hobbit'),('Bilbo Baggins','Hobbit'),('Frodo Baggins','Hobbit'),
             ('Samwise Gamgee','Hobbit'),('Meriadoc Brandybuck','Hobbit'),('Peregrin Took','Hobbit'),('Legolas','Elfo'),('Gimli','Anao'),
             ('Sauron','Maia'),('Witch-king of Angmar','Nazgul'),('Treebeard','Ent'),('Éomer','Homem')]:
    g.add((P(nm),RDF.type,L[c]))
g.add((P('Sauron'),SKOS.altLabel,Literal('Senhor Sombrio'))); 
alt={'Aragorn II Elessar':['Passolargo (Strider)','Elessar','Estel','Thorongil'],'Gandalf':['Mithrandir','Olórin','Tharkûn','Incánus'],
     'Gollum':['Sméagol','Stinker'],'Frodo Baggins':['Sr. Subterrâneo (Underhill)'],'Treebeard':['Fangorn','Barbárvore']}
for k,v in alt.items():
    for a in v: g.add((name2uri[k],SKOS.altLabel,Literal(a)))
# Sociedade do Anel
soc=L.Sociedade_do_Anel; g.add((soc,RDF.type,L.SociedadeDoAnel)); g.add((soc,RDFS.label,Literal('A Sociedade do Anel'))); prov(soc)
ev={}
def E(k,label,ano,ordem):
    u=L['ev_'+k]; ev[k]=u; g.add((u,RDF.type,L.Evento)); g.add((u,RDFS.label,Literal(label,lang='pt')))
    g.add((u,L.inicioAno,Literal(ano,datatype=XSD.integer))); g.add((u,L.ordem,Literal(ordem,datatype=XSD.integer))); prov(u); return u
E('conselho','Conselho de Elrond',3018,1)
E('forja','Forja do Um Anel (SA ~1600)',1600-3441,0); E('corte','Isildur toma o Anel (SA 3441)',0,1)
E('anduin','Anel se perde no Anduin (TA 2)',2,2); E('achado','Déagol encontra o Anel (TA 2463)',2463,3)
E('assassinato','Sméagol mata Déagol e toma o Anel (TA 2463)',2463,4); E('caverna','Bilbo acha o Anel nas cavernas dos orcs (TA 2941)',2941,5)
E('partidaBilbo','Bilbo deixa o Anel com Frodo (TA 3001)',3001,6); E('cirith','Sam toma o Anel em Cirith Ungol (TA 3019)',3019,7)
E('devolucao','Sam devolve o Anel a Frodo (TA 3019)',3019,8); E('orodruin','Destruição do Anel na Montanha da Perdição (TA 3019)',3019,9)
E('quebra','Quebra da Sociedade (26 fev TA 3019)',3019,10)
um=L.Um_Anel; g.add((um,RDF.type,L.UmAnel)); g.add((um,RDFS.label,Literal('O Um Anel'))); prov(um)
bearers=[('Sauron','forja','corte',-1841,0),('Isildur','corte','anduin',0,2),('Déagol','achado','assassinato',2463,2463),
         ('Gollum','assassinato','caverna',2463,2941),('Bilbo Baggins','caverna','partidaBilbo',2941,3001),('Frodo Baggins','partidaBilbo','cirith',3001,3019),
         ('Samwise Gamgee','cirith','devolucao',3019,3019),('Frodo Baggins','devolucao','orodruin',3019,3019)]
for i,(who,a,b,y0,y1) in enumerate(bearers):
    u=L[f'posse_{i}']; g.add((u,RDF.type,L.Posse)); g.add((u,L.portador,P(who))); g.add((u,L.anel,um))
    g.add((u,L.iniciadaPor,ev[a])); g.add((u,L.terminadaPor,ev[b])); g.add((u,L.inicioAno,Literal(y0,datatype=XSD.integer))); g.add((u,L.fimAno,Literal(y1,datatype=XSD.integer)))
    g.add((u,L.ordem,Literal(i+1,datatype=XSD.integer))); prov(u)
g.add((P('Sauron'),RDFS.comment,Literal('Forjou o Um Anel; portador original.',lang='pt')))
# Participação na Sociedade (fluente: valida entre o Conselho e a Quebra)
fell=['Frodo Baggins','Samwise Gamgee','Meriadoc Brandybuck','Peregrin Took','Gandalf','Aragorn II Elessar','Legolas','Gimli','Boromir']
for nm in fell:
    u=L['part_'+slug(nm)]; g.add((u,RDF.type,L.Participacao)); g.add((u,L.participante,P(nm))); g.add((u,L.grupoRef,soc))
    g.add((u,L.iniciadaPorP,ev['conselho'])); g.add((u,L.terminadaPorP,ev['quebra'])); g.add((P(nm),L.membroDe,soc)); prov(u)
# parentesco e casamentos curados
kin=[('Elrond','Arwen'),('Celebrían','Arwen'),('Galadriel','Celebrían'),('Celeborn','Celebrían'),('Arathorn II','Aragorn II Elessar'),
     ('Aragorn II Elessar','Eldarion'),('Arwen','Eldarion'),('Denethor II','Boromir'),('Denethor II','Faramir'),('Théoden','Théodred'),
     ('Hamfast Gamgee','Samwise Gamgee'),('Samwise Gamgee','Elanor Gardner'),('Rosie Cotton','Elanor Gardner'),('Elendil','Isildur'),('Isildur','Valandil')]
for a,b in kin:
    if a in name2uri or True: g.add((P(a),L.paiOuMaeDe,P(b)))
for a,b in [('Aragorn II Elessar','Arwen'),('Elrond','Celebrían'),('Galadriel','Celeborn'),('Samwise Gamgee','Rosie Cotton')]: g.add((P(a),L.conjugeDe,P(b)))
for a,b in [('Witch-king of Angmar','Sauron'),('Gríma Wormtongue','Saruman'),('Saruman','Sauron')]: g.add((P(a),L.serveA,P(b)))
# aliases / identidade (owl:sameAs) — Sméagol aparece como falante distinto nos dados de fala
smg=L.Smeagol_falante; g.add((smg,RDF.type,L.Personagem)); g.add((smg,RDFS.label,Literal('Sméagol (falante)'))); prov(smg); g.add((smg,OWL.sameAs,name2uri['Gollum']))

# ============ Obras ============
mv=pd.read_csv(D+'Movies.csv'); mv['Name']=mv.Name.str.strip()
film_uri={}
for _,r in mv.iterrows():
    u=L['film_'+slug(r['Name'])]; film_uri[r['Name']]=u
    serie = 'Series' in r['Name']
    g.add((u,RDF.type,L.SerieDeFilmes if serie else L.Filme)); g.add((u,RDFS.label,Literal(r['Name'])))
    for c,p in [('RuntimeInMinutes','duracaoMin'),('BudgetInMillions','orcamentoMi'),('BoxOfficeRevenueInMillions','bilheteriaMi'),('AcademyAwardNominations','indicacoesOscar'),('AcademyAwardWins','vitoriasOscar'),('RottenTomatoesScore','notaRT')]:
        g.add((u,L[p],Literal(float(r[c]),datatype=XSD.decimal)))
    g.add((u,L.proveniencia,Literal('dataset:Movies.csv')))
for fam,nm in [('The Fellowship of the Ring','The Lord of the Rings Series'),('The Two Towers','The Lord of the Rings Series'),('The Return of the King','The Lord of the Rings Series')]:
    g.add((film_uri[fam],L.parteDe,film_uri[nm]))
book=json.load(open(D+'LordOfTheRingsBook.json'))
bk_names={'TheFellowshipOfTheRing':'A Sociedade do Anel','TheTwoTowers':'As Duas Torres','TheReturnOfTheKing':'O Retorno do Rei'}
bk_uri={}
for k,v in bk_names.items(): u=L['livro_'+k]; bk_uri[k]=u; g.add((u,RDF.type,L.Livro)); g.add((u,RDFS.label,Literal(v,lang='pt')))
cap_uri={}
for i,c in enumerate(book,1):
    u=L[f'cap_{i:02d}']; cap_uri[i]=u; g.add((u,RDF.type,L.Capitulo)); g.add((u,RDFS.label,Literal(c['ChapterName'].strip())))
    g.add((u,L.parteDe,bk_uri[c['BookName']['Case']])); g.add((u,L.ordem,Literal(i,datatype=XSD.integer)))
# menções (camada extraída do texto por casamento de padrões — mini "entity linking")
men=pd.read_csv('mentions_raw.csv'); agg=men.groupby(['cap_idx','entidade']).n.sum().reset_index(); agg=agg[agg.n>0]
for _,r in agg.iterrows():
    u=L[f"men_{r.cap_idx:02d}_{slug(r.entidade)}"]; g.add((u,RDF.type,L.Mencao)); g.add((u,L.personagemRef,P(r.entidade)))
    g.add((u,L.capituloRef,cap_uri[r.cap_idx])); g.add((u,L.ocorrencias,Literal(int(r.n),datatype=XSD.integer))); g.add((u,L.proveniencia,Literal('extraido:LordOfTheRingsBook.json')))
# falas nos filmes
w=pd.read_csv(D+'WordsByCharacter.csv')
WMAP={'Aragorn':'Aragorn II Elessar','Arwen':'Arwen','Bilbo':'Bilbo Baggins','Boromir':'Boromir','Celeborn':'Celeborn','Deagol':'Déagol','Denethor':'Denethor II','Elrond':'Elrond','Eomer':'Éomer','Eowyn':'Éowyn','Faramir':'Faramir','Farmer Maggot':'Farmer Maggot','Frodo':'Frodo Baggins','Gaffer':'Hamfast Gamgee','Galadriel':'Galadriel','Gamling':'Gamling','Gandalf':'Gandalf','Gimli':'Gimli','Gollum':'Gollum','Grima Wormtongue':'Gríma Wormtongue','Haldir':'Haldir (Lorien)','Hama':'Háma','Isildur':'Isildur','Legolas':'Legolas','Lobelia Sackville-Baggins':'Lobelia Sackville-Baggins','Merry':'Meriadoc Brandybuck','Mouth Of Sauron':None,'Pippin':'Peregrin Took','Rosie':'Rosie Cotton','Sam':'Samwise Gamgee','Saruman':'Saruman','Shagrat':'Shagrat','Smeagol':'__SMEAGOL__','Theoden':'Théoden','Treebeard':'Treebeard','Ugluk':'Uglúk','Witch King':'Witch-king of Angmar','Grishnakh':'Grishnákh'}
film_short={'The Fellowship Of The Ring':'film_The_Fellowship_of_the_Ring','The Two Towers':'film_The_Two_Towers','The Return Of The King':'film_The_Return_of_the_King'}
wa=w.groupby(['Film','Character']).Words.sum().reset_index()
res=0; tot=int(wa.Words.sum()); rows_w=[]
for _,r in wa.iterrows():
    tgt=WMAP.get(r.Character)
    if tgt is None and r.Character not in WMAP: rows_w.append((r.Film,r.Character,None,int(r.Words)));continue
    if tgt=='__SMEAGOL__': pu=smg
    elif tgt is None: rows_w.append((r.Film,r.Character,None,int(r.Words)));continue
    else: pu=P(tgt)
    u=L[f"fala_{slug(r.Film)}_{slug(r.Character)}"]; g.add((u,RDF.type,L.ParticipacaoFalada)); g.add((u,L.personagemRef,pu)); g.add((u,L.filmeRef,L[film_short[r.Film]]))
    g.add((u,L.palavras,Literal(int(r.Words),datatype=XSD.integer))); g.add((u,L.proveniencia,Literal('dataset:WordsByCharacter.csv'))); res+=int(r.Words); rows_w.append((r.Film,r.Character,str(pu),int(r.Words)))
pd.DataFrame(rows_w,columns=['film','falante','entidade','palavras']).to_csv('falas_resolvidas.csv',index=False)
g.add((L.Ontologia,RDF.type,OWL.Ontology)); g.add((L.Ontologia,OWL.versionInfo,Literal('2.0 — disjunção Ainur/Elfo removida após inconsistência detectada em Lúthien'))); g.add((L.Ontologia,RDFS.label,Literal('Ontologia da Terra-média (O Senhor dos Anéis)',lang='pt')))
# separa TBox/ABox para exportação
g.serialize('/mnt/user-data/outputs/ontologia_lotr_completa.ttl',format='turtle')
json.dump(dict(casais_interpovos_ingenuo=sorted({tuple(sorted(x)) for x in naive_pairs}),homonimos_corrigidos=fixed,triplas=len(g),personagens=len(ch),conjuges_texto=n_sp,palavras_total=tot,palavras_resolvidas=res),open('stats_kg.json','w'),indent=1)
print(open('stats_kg.json').read())
