# coding:utf-8
import codecs
import os
import re
from os.path import getsize, splitext
import json

luaDir = "tolua++"
# snippetsDir = "C://Users//06wj//AppData//Roaming//Sublime Text 2//Packages//User//snippets"
snippetsDir = "snippets"
template = codecs.open("template.sublime-snippet", "r", "utf-8").read()
data = {}

def cleanDir( Dir ):
    print("cleanDir:", Dir)
    print("wait...")
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

#                     class    AAA    :       {func }
klassP =  re.compile('class\s+(\w+)\s*:?\s*(.*?)\s*{(.*?)}', re.S)

#                   void       func(  int a, int b)
funcP = re.compile('\w+[\s\*&]+(\w+)\((.*?)\)', re.S)

def outPut(klass, func, args):
    print("write:", klass,func)
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

def getSuperKlass(str):
    if str == "":
        return []
    else:
        return re.sub(r"\s*public\s*", "", str).split(",")

def getData(file):
    text = codecs.open(file, "r", "utf-8").read()
    text = re.sub(r"/\*[\S\s]*?\*/", "", text)
    text = re.sub(r"//[^\t\n]*", "", text)
    klasses = klassP.findall(text)
    for klass in klasses:
        klassData = {}
        superKlass = ""
        if len(klass) == 2:
            klassName = klass[0]
            funcStr = klass[1]
        else:
            klassName = klass[0]
            superKlass = klass[1]
            funcStr = klass[2]
        klassData["klass"] = klassName
        klassData["super"] = getSuperKlass(superKlass)
        funcData = klassData["func"] = {}
        print(klassName,":", klassData["super"])
        funcs = funcP.findall(funcStr)
        for func in funcs:
            funcName = func[0]
            args = re.sub(r",[\n\r\s]+", ",", func[1])
            args = re.sub(r"\s+", "_", args)
            funcData[funcName] = args
        data[klassName] = klassData

for file in os.listdir(luaDir):
    if(splitext(file)[1]==".pkg"):
        getData(os.path.join(luaDir, file))


tree = {}

    
def extends(childKlassData, superKlass):
    if superKlass not in data:
        tree[superKlass] = {
            "klass":superKlass,
            "func":"",
            "super":[]
        }
    if superKlass not in tree and len(data[superKlass]["super"]) == 0:
        tree[superKlass] = data[superKlass]
    if superKlass in tree:
        for func in tree[superKlass]["func"]:
            childKlassData["func"][func] = tree[superKlass]["func"][func]
    else:
        for func in data[superKlass]["func"]:
            childKlassData["func"][func] = data[superKlass]["func"][func]
            for superName in data[superKlass]["super"]:
                extends(childKlassData, superName)
    tree[childKlassData["klass"]] = childKlassData


for klass in data:
    print("________________________", klass, "___________________")
    if len(data[klass]["super"]) == 0:
        tree[klass] = data[klass]
    else:
        for superName in data[klass]["super"]:
            print(superName)
            extends(data[klass], superName)


for klass in tree:
    for func in tree[klass]["func"]:
        outPut(klass, func, tree[klass]["func"][func])



if os.name == "nt":
    os.system("pause")