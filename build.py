# coding:utf-8
import codecs
import os
import re
from os.path import getsize, splitext

luaDir = os.path.join("tolua++")
snippetsDir = os.path.join("snippets")
template = codecs.open("template.sublime-snippet", "r", "utf-8").read()

def cleanDir( Dir ):
    if os.path.isdir( Dir ):
        paths = os.listdir( Dir )
        for path in paths:
            filePath = os.path.join( Dir, path )
            if os.path.isfile( filePath ):
                try:
                    os.remove( filePath )
                except os.error:
                    autoRun.exception( "remove %s error." %filePath )#引入logging
            elif os.path.isdir( filePath ):
                shutil.rmtree(filePath,True)
    return True

cleanDir(snippetsDir)

klassP =  re.compile('class\s+(\w+)\s*:\s*.*?{(.*?)}', re.S)
funcP = re.compile('\w+\s+(\w+)\((.+?)\)', re.S)

def getData(file):
	text = codecs.open(file, "r", "utf-8").read()
	klasses = klassP.findall(text)
	for klass in klasses:
		print(klass[0])
		funcs = funcP.findall(klass[1])
		for func in funcs:
			print(klass[0]+":"+func[0]+":"+func[1])


for file in os.listdir(luaDir):
	if(splitext(file)[1]==".pkg"):
		getData(os.path.join(luaDir, file))

