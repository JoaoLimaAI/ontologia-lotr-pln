import zipfile,re,subprocess,shutil,os,html,sys
src='/mnt/user-data/outputs/roteiro_seminario_ontologias.docx'
tmp='/tmp/toc'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
z=zipfile.ZipFile(src); x=z.read('word/document.xml').decode()
heads=[]
for m in re.finditer(r'<w:p>(?:(?!</w:p>).)*?<w:pStyle w:val="Heading([12])"/>(?:(?!</w:p>).)*?</w:p>',x,re.S):
    t=''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',m.group(0))); heads.append((int(m.group(1)),html.unescape(t)))
heads=[h for h in heads if h[1]!='Sumário']
subprocess.run(['python3',[p for p in __import__('glob').glob('/root/.claude/skills/synced/*/docx/scripts/office/soffice.py')][0],'--headless','--convert-to','pdf',src,'--outdir',tmp],capture_output=True)
pdf=tmp+'/roteiro_seminario_ontologias.pdf'
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
pages=[subprocess.run(['pdftotext','-f',str(i),'-l',str(i),'-layout',pdf,'-'],capture_output=True,text=True).stdout for i in range(1,n+1)]
norm=lambda t:re.sub(r'\s+',' ',t)
pg=[];cur=3
for lvl,t in heads:
    for i in range(cur-1,n):
        if norm(t) in norm(pages[i]) and (i+1)>=3:
            cur=i+1; break
    pg.append(cur)
def entry(lvl,t,p):
    ind='<w:ind w:left="360"/>' if lvl==2 else ''
    b='<w:b/>' if lvl==1 else ''
    rpr=f'<w:rPr>{b}<w:sz w:val="22"/></w:rPr>'
    return f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9638"/></w:tabs><w:spacing w:before="{80 if lvl==1 else 0}" w:after="40"/>{ind}</w:pPr><w:r>{rpr}<w:t xml:space="preserve">{html.escape(t)}</w:t></w:r><w:r>{rpr}<w:tab/></w:r><w:r>{rpr}<w:t>{p}</w:t></w:r></w:p>'
ents=[entry(l,t,p) for (l,t),p in zip(heads,pg)]
old=re.search(r'<w:sdtContent><w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/>.*?</w:sdtContent>',x,re.S).group(0)
begin='<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve">TOC \\h \\o &quot;1-2&quot;</w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'
first=ents[0].replace('<w:r>',begin+'<w:r>',1)
new='<w:sdtContent>'+first+''.join(ents[1:])+'<w:p><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:sdtContent>'
x2=x.replace(old,new)
out='/tmp/toc/new.docx'
zo=zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED)
for it in z.infolist():
    d=z.read(it.filename)
    if it.filename=='word/document.xml': d=x2.encode()
    zo.writestr(it,d)
zo.close(); shutil.copy(out,src)
print(len(heads),'entradas; páginas',pg[:12],n)
