# -*- coding: utf-8 -*-
"""Demonstração de consultas SPARQL e raciocínio OWL-RL sobre a ontologia da Terra-média.
Uso: python3 consultas_sparql.py ontologia_lotr_completa.ttl"""
import sys, owlrl
from rdflib import Graph, Namespace, RDF, OWL
L=Namespace('http://example.org/lotr#')
f=sys.argv[1] if len(sys.argv)>1 else 'ontologia_lotr_completa.ttl'
g=Graph().parse(f); inf=Graph()
for t in g: inf.add(t)
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(inf)
P='PREFIX lotr:<http://example.org/lotr#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX owl:<http://www.w3.org/2002/07/owl#> '
def run(gr,q): return [tuple(str(x).split('#')[-1] if str(x).startswith('http') else str(x) for x in r) for r in gr.query(P+q)]
Q=[
('Q1. Quem já portou o Um Anel? (nenhum "PortadorDeAnel" foi declarado: o raciocinador infere)','inf','SELECT DISTINCT ?x WHERE{?x a lotr:PortadorDeAnel} ORDER BY ?x'),
('Q2. Sequência de posses do Um Anel (evento Inicia/Termina)','g','SELECT ?o ?quem ?inicio ?fim WHERE{?p a lotr:Posse; lotr:ordem ?o; lotr:portador ?q; lotr:inicioAno ?inicio; lotr:fimAno ?fim. ?q rdfs:label ?quem} ORDER BY ?o'),
('Q3. Ancestrais de Arwen (propriedade transitiva)','inf','SELECT ?x WHERE{?x lotr:ancestralDe lotr:Arwen} ORDER BY ?x'),
('Q4. Membros da Sociedade do Anel por povo (herança de classes)','inf','SELECT ?povo (COUNT(DISTINCT ?m) AS ?n) WHERE{?m lotr:membroDe lotr:Sociedade_do_Anel; a ?povo. VALUES ?povo {lotr:Hobbit lotr:Homem lotr:Elfo lotr:Anao lotr:Maia}} GROUP BY ?povo ORDER BY DESC(?n)'),
('Q5. Casais cujos cônjuges NÃO compartilham nenhum povo (auditoria de qualidade / casos legítimos)','inf','''SELECT DISTINCT ?a ?b WHERE{?a lotr:conjugeDe ?b. FILTER(STR(?a)<STR(?b)) ?a a ?ta. ?b a ?tb.
 VALUES ?ta {lotr:Hobbit lotr:Elfo lotr:Homem lotr:Anao lotr:Maia lotr:Orc} VALUES ?tb {lotr:Hobbit lotr:Elfo lotr:Homem lotr:Anao lotr:Maia lotr:Orc}
 FILTER NOT EXISTS{?a a ?c. ?b a ?c. VALUES ?c {lotr:Hobbit lotr:Elfo lotr:Homem lotr:Anao lotr:Maia lotr:Orc}}}'''),
('Q6. Palavras faladas após resolver identidades (owl:sameAs: Sméagol = Gollum), top 6','g','''SELECT ?c (SUM(?w) AS ?palavras) WHERE{?f a lotr:ParticipacaoFalada; lotr:personagemRef ?p; lotr:palavras ?w. ?p owl:sameAs? ?c. FILTER NOT EXISTS{?c owl:sameAs ?z}} GROUP BY ?c ORDER BY DESC(?palavras) LIMIT 6'''),
('Q7. Mundo aberto: personagens SEM povo declarado (desconhecido ≠ inexistente)','g','SELECT (COUNT(?x) AS ?n) WHERE{?x a lotr:Personagem. FILTER NOT EXISTS{?x a ?t. VALUES ?t {lotr:Hobbit lotr:Elfo lotr:Homem lotr:Anao lotr:Maia lotr:Ent lotr:Orc lotr:Ainur lotr:Espectro lotr:Criatura lotr:Animal lotr:Dragao lotr:Troll lotr:Aguia lotr:Aranha lotr:Metamorfo}}}'),
('Q8. Participação na Sociedade como fluente: quem deixou de ser membro e por qual evento?','g','SELECT ?quem ?evento WHERE{?p a lotr:Participacao; lotr:participante ?q; lotr:terminadaPorP ?e. ?q rdfs:label ?quem. ?e rdfs:label ?evento}'),
]
out=[]
for t,w,q in Q:
    r=run(inf if w=='inf' else g,q); out.append('## '+t+'\n'); out+=['- '+' | '.join(x) for x in r[:12]]+[('- ... (%d linhas)'%len(r)) if len(r)>12 else '']; out.append('')
# Teste de consistência (injeção deliberada)
h=Graph()
for t in g: h.add(t)
h.add((L.Frodo_Baggins,RDF.type,L.Anao)); i2=Graph()
for t in h: i2.add(t)
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(i2)
err=[str(o) for s,p,o in i2 if str(p).endswith('#error')]
out.append('## Q9. Teste de consistência: afirmar que Frodo é Anão\n'); out+=['- '+e for e in err]
open('resultados_consultas.md','w').write('\n'.join(out)); print('\n'.join(out))
