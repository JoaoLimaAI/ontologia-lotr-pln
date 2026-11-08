import json, re, pandas as pd
D='/mnt/user-data/uploads/1.SeminarioOntologiaGrafoConhecimento/'
book=json.load(open(D+'LordOfTheRingsBook.json'))
ALIASES={
 'Frodo Baggins':['Frodo'],'Samwise Gamgee':['Sam','Samwise'],'Meriadoc Brandybuck':['Merry'],'Peregrin Took':['Pippin'],
 'Gandalf':['Gandalf','Mithrandir'],'Aragorn II Elessar':['Aragorn','Strider','Elessar','Estel','Thorongil'],
 'Legolas':['Legolas'],'Gimli':['Gimli'],'Boromir':['Boromir'],'Gollum':['Gollum','Sméagol','Smeagol'],
 'Sauron':['Sauron'],'Saruman':['Saruman'],'Bilbo Baggins':['Bilbo'],'Elrond':['Elrond'],'Galadriel':['Galadriel'],
 'Théoden':['Théoden','Theoden'],'Éowyn':['Éowyn','Eowyn'],'Éomer':['Éomer','Eomer'],'Faramir':['Faramir'],
 'Denethor II':['Denethor'],'Treebeard':['Treebeard','Fangorn'],'Arwen':['Arwen'],'Celeborn':['Celeborn'],
 'Gríma Wormtongue':['Gríma','Wormtongue'],'Isildur':['Isildur'],'Rosie Cotton':['Rosie'],
}
rows=[]
for i,ch in enumerate(book,1):
    t=ch['ChapterData']; bk=ch['BookName']['Case']
    for ent,al in ALIASES.items():
        for a in al:
            n=len(re.findall(r'(?<![A-Za-zÀ-ÿ])'+re.escape(a)+r"(?![A-Za-zÀ-ÿ])",t))
            rows.append(dict(cap_idx=i,livro=bk,capitulo=ch['ChapterName'].strip(),entidade=ent,alias=a,n=n,palavras_cap=len(t.split())))
df=pd.DataFrame(rows); df.to_csv('mentions_raw.csv',index=False)
print(df.groupby(['entidade','alias']).n.sum().loc[['Aragorn II Elessar','Gollum','Gandalf','Samwise Gamgee','Frodo Baggins','Treebeard']])
print(df.groupby('entidade').n.sum().sort_values(ascending=False).head(12))
print(df.groupby('livro').capitulo.nunique())
print(sorted(set(df[df.livro=='TheFellowshipOfTheRing'].cap_idx))[-3:], df[df.cap_idx==22].capitulo.iloc[0], df[df.cap_idx==23].capitulo.iloc[0])
