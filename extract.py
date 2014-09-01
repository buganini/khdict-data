# -*- coding: utf-8 -*-
import os
import sys
import zipfile
import re
import json
import icu
from xml.dom.minidom import parseString

def grapheme_clusters(s):
	b=icu.BreakIterator.createCharacterInstance(icu.Locale.getEnglish())
	b.setText(s)
	l=0
	r=[]
	for p in b:
		if s[p-1]==u"\u17d2":
			continue
		r.append(s[l:p])
		l=p
	if l<len(s):
		r.append(s[l:])
	return r

def getText(n):
	s=""
	for child in n.childNodes:
		if hasattr(child, "data"):
			s+=child.data
		else:
			s+=getText(child)
	return s

"""
0: sn
1: key
2: sn2
3: pronounce
4: from
5: class
6: definition
7: alias
8: ingredient
"""

d={}

for x in sys.argv[1:]:
	sys.stderr.write(x+"\n")
	zf=zipfile.ZipFile(x)
	xml=zf.read("content.xml")
	dom=parseString(xml)

	rows=dom.getElementsByTagName('table:table-row')
	i=0
	while True:
		cells=rows[i].getElementsByTagName('table:table-cell')
		if len(cells)==9:
			break
		else:
			i+=1
	keys=[getText(cell) for cell in cells]
	if keys[0]!=u"ល.រ":
		break
	key=""
	for row in rows[i+1:]:
		cells=row.getElementsByTagName('table:table-cell')
		if(len(cells)!=9):
			sys.stderr.write("["+str(len(cells))+"]: "+", ".join([getText(cell) for cell in cells])+"\n")
			sys.exit(1)
		cells=[getText(cells[i]) for i in range(9)]
		if not cells[1]:
			cells[1]=key
		key=cells[1]
		entry={
			"pronounce": cells[3],
			"source": cells[4],
			"class": cells[5],
			"definition": cells[6],
			"alias": cells[7],
			"ingredient": cells[8],
		}
		if key not in d:
			d[key]=[]
		d[key].append(entry)
	zf.close()

keys=d.keys()
keys=[u"\ufeff"+u"\ufeff\ufeff".join(grapheme_clusters(k))+u"\ufeff" for k in keys]
keys.sort(key=lambda x: -len(x))
r=re.compile("("+"|".join(keys)+")")
total=len(keys)
idx=0
for k in d:
	idx+=1
	sys.stderr.write(str(idx)+"/"+str(total)+" "+k+"\n")
	for e in d[k]:
		df=u"\ufeff"+u"\ufeff\ufeff".join(grapheme_clusters(e["definition"]))+u"\ufeff"
		df=r.sub("`\\1~", df)
		df=df.replace(u"\ufeff","")
		e["definition"]=df

print json.dumps(d)
