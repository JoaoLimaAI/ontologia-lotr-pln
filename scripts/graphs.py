# -*- coding: utf-8 -*-
import subprocess, textwrap
BG='#F7F3EA'; INK='#2B2A28'
def dot(name,src):
    open(f'fig/{name}.dot','w').write(src); subprocess.run(['dot','-Tpng','-Gdpi=170',f'fig/{name}.dot','-o',f'fig/{name}.png'],check=True)
H=f'bgcolor="{BG}" fontname="Inter" '
# ---- TBox taxonomia ----
tax='''digraph T{ rankdir=TB; '''+H+'''nodesep=.22; ranksep=.6; node[shape=box,style="rounded,filled",fontname="Inter",fontsize=16,color="#8A7F6B",fillcolor="#FFFDF7",fontcolor="#2B2A28",margin="0.14,0.08"]; edge[color="#8A7F6B",arrowhead=empty,arrowsize=.8];
Elemento[fillcolor="#2B2A28",fontcolor="#F7F3EA"];
Elemento->{Ser Lugar Artefato Grupo Evento Obra};
Evento[fillcolor="#EAD9A8"]; Posse[label="Posse\\n(fluente)",fillcolor="#EAD9A8"]; Participacao[label="Participação\\n(fluente)",fillcolor="#EAD9A8"]; Elemento->Posse; Elemento->Participacao;
Ser->{Personagem Criatura}; Personagem[fillcolor="#C8962E",fontcolor="white"];
Personagem->{Hobbit Elfo Anao Homem Ent Orc Ainur Espectro MeioElfo PortadorDeAnel};
PortadorDeAnel[label="PortadorDeAnel\\n(classe definida)",style="rounded,filled,dashed",fillcolor="#FFF1C9"];
MeioElfo[label="MeioElfo\\n(Elfo ⊓ Homem)",style="rounded,filled,dashed"];
Ainur->Maia->{Istari Balrog}; Orc->UrukHai; Espectro->Nazgul; Nazgul->Homem[style=dashed,color="#B8860B",constraint=false];
MeioElfo->Elfo[style=dashed,color="#B8860B",constraint=false]; MeioElfo->Homem[style=dashed,color="#B8860B",constraint=false];
Criatura->{Animal Aranha Aguia Troll Dragao}; Artefato->Anel->AnelDePoder->UmAnel; Grupo->SociedadeDoAnel; Lugar->Reino; Obra->{Livro Filme};
}'''
dot('t1_taxonomia',tax)
# ---- TBox relações ----
rel='''digraph R{ '''+H+'''rankdir=LR; nodesep=.45; ranksep=1.1; node[shape=box,style="rounded,filled",fontname="Inter",fontsize=16,color="#8A7F6B",fillcolor="#FFFDF7",fontcolor="#2B2A28",margin="0.2,0.1"]; edge[color="#6B665C",fontname="Inter",fontsize=13,fontcolor="#8A3B12",arrowsize=.8];
Personagem[fillcolor="#C8962E",fontcolor="white"]; Posse[fillcolor="#EAD9A8"]; Participacao[fillcolor="#EAD9A8"]; Evento[fillcolor="#EAD9A8"]; Mencao[label="Menção\\n(extraída do texto)",fillcolor="#E8E3D3"]; Falada[label="ParticipaçãoFalada\\n(dataset de falas)",fillcolor="#E8E3D3"];
Personagem->Personagem[label="cônjugeDe (simétrica)\\npaiOuMãeDe ⊑ ancestralDe (transitiva)\\nserveA"];
Posse->Personagem[label="portador"]; Posse->Anel[label="anel"]; Posse->Evento[label="iniciadaPor / terminadaPor",style=dashed];
Participacao->Personagem[label="participante"]; Participacao->Grupo[label="grupo"]; Participacao->Evento[label="iniciada/terminadaPor",style=dashed];
Personagem->Lugar[label="habitaEm"]; Mencao->Personagem[label="personagem"]; Mencao->Capitulo[label="capítulo"]; Capitulo->Livro[label="parteDe"];
Falada->Personagem[label="personagem"]; Falada->Filme[label="filme"];
Personagem->Anel[label="jaPortou\\n(= portador⁻¹ ∘ anel)",color="#B8860B",fontcolor="#B8860B",penwidth=2];
}'''
dot('t2_relacoes',rel)
# ---- KG: Anel + Sociedade + parentesco ----
cors={'Hobbit':'#5B8C5A','Elfo':'#4A78A8','Homem':'#B07A4B','Anao':'#8A5A9E','Maia':'#C8962E','MeioElfo':'#4A78A8'}
people={'Frodo':'Hobbit','Sam':'Hobbit','Merry':'Hobbit','Pippin':'Hobbit','Bilbo':'Hobbit','Gollum':'Hobbit','Déagol':'Hobbit','Gandalf':'Maia','Sauron':'Maia','Aragorn':'Homem','Boromir':'Homem','Isildur':'Homem','Denethor II':'Homem','Faramir':'Homem','Legolas':'Elfo','Gimli':'Anao','Elrond':'MeioElfo','Arwen':'MeioElfo','Galadriel':'Elfo','Celebrían':'Elfo','Celeborn':'Elfo','Eldarion':'Homem'}
n=''.join(f'"{k}"[fillcolor="{cors[v]}",fontcolor="white"];' for k,v in people.items())
mem=['Frodo','Sam','Merry','Pippin','Gandalf','Aragorn','Legolas','Gimli','Boromir']
e=''.join(f'"{k}"->"Sociedade\\ndo Anel"[color="#6B665C",arrowsize=.6];' for k in mem)
ring=[('Sauron','Isildur'),('Isildur','Déagol'),('Déagol','Gollum'),('Gollum','Bilbo'),('Bilbo','Frodo'),('Frodo','Sam')]
e+=''.join(f'"{a}"->"{b}"[color="#B8860B",penwidth=3,len=1.1];' for a,b in ring)
for a,b in [('Galadriel','Celebrían'),('Celeborn','Celebrían'),('Celebrían','Arwen'),('Elrond','Arwen'),('Arwen','Eldarion'),('Aragorn','Eldarion'),('Denethor II','Boromir'),('Denethor II','Faramir')]: e+=f'"{a}"->"{b}"[color="#8A7F6B",arrowsize=.6,style=dashed];'
for a,b in [('Aragorn','Arwen'),('Elrond','Celebrían'),('Galadriel','Celeborn')]: e+=f'"{a}"->"{b}"[dir=none,color="#8A3B12",penwidth=2];'
kg=f'''digraph K{{ {H} layout=neato; overlap=false; splines=true; sep="+12"; ratio=0.62; edge[len=1.4]; node[shape=ellipse,style=filled,fontname="Inter",fontsize=15,color="#2B2A28",penwidth=0,margin="0.1,0.05"]; "Sociedade\\ndo Anel"[shape=box,style="rounded,filled",fillcolor="#2B2A28",fontcolor="#F7F3EA",fontsize=18]; {n} {e} }}'''
dot('t3_kg',kg)

tax2='''digraph T{ rankdir=TB; '''+H+'''nodesep=.25; ranksep=.55; node[shape=box,style="rounded,filled",fontname="Inter",fontsize=17,color="#8A7F6B",fillcolor="#FFFDF7",fontcolor="#2B2A28",margin="0.16,0.09"]; edge[color="#8A7F6B",arrowhead=empty,arrowsize=.8];
Personagem[fillcolor="#C8962E",fontcolor="white"];
Personagem->{Hobbit Elfo Anao Homem Ent Orc Ainur Espectro MeioElfo PortadorDeAnel};
PortadorDeAnel[label="PortadorDeAnel\\n(definida, inferida)",style="rounded,filled,dashed",fillcolor="#FFF1C9"];
MeioElfo[label="MeioElfo\\n(Elfo ⊓ Homem)",style="rounded,filled,dashed"];
Ainur->Maia->{Istari Balrog}; Orc->UrukHai; Espectro->Nazgul; Nazgul->Homem[style=dashed,color="#B8860B",constraint=false];
MeioElfo->Elfo[style=dashed,color="#B8860B",constraint=false]; MeioElfo->Homem[style=dashed,color="#B8860B",constraint=false];
}'''
dot('t1b_personagens',tax2)
print('ok')
