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
funcP = re.compile('\w+[\s\*]+(\w+)\((.*?)\)', re.S)

def outPut(klass, func, args):
    tpl = template.replace("%class", klass)
    tpl = tpl.replace("%func", func)
    argList = args.split(",")
    args = ""
    i = 1
    if len(argList)==0 or argList[0]=="void":
        args = ""
    else:
        for arg in argList:
            args += "${" + str(i) + ":" + arg + "}" + ","
            i+=1
        args = args[:-1]
    tpl = tpl.replace("%args", args)
    ff = codecs.open(os.path.join(snippetsDir, klass+"_"+func)+".sublime-snippet", "w", "utf-8")
    ff.write(tpl)
    ff.close()

def getData(file):
    text = codecs.open(file, "r", "utf-8").read()
    klasses = klassP.findall(text)
    for klass in klasses:
        klassName = klass[0]
        print(klassName)
        funcs = funcP.findall(klass[1])
        for func in funcs:
            funcName = func[0]
            args = re.sub(r",[\n\r\s]+", ",", func[1])
            args = re.sub(r"\s+", "_", args)
            outPut(klassName, funcName, args)

for file in os.listdir(luaDir):
    if(splitext(file)[1]==".pkg"):
        getData(os.path.join(luaDir, file))

