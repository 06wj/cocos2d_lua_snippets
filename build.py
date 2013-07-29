# coding:utf-8
import codecs
import os
import re
from os.path import getsize, splitext
import json
import shutil

luaDir = "tolua++"
snippetsDir = "snippets"
templatePath = "template.sublime-snippet"
completionTemplatePath = "template_completions.sublime-completions"
completionItemTemplatePath = "template_completions_item.sublime-completions"


template = codecs.open(templatePath, "r", "utf-8").read()
templateCompletion = codecs.open(completionTemplatePath, "r", "utf-8").read()
templateCompletionItem = codecs.open(completionItemTemplatePath, "r", "utf-8").read()
data = {}
dictStr = []

def cleanDir( Dir ):
    print("cleanDir:", Dir)
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
                print("clean", filePath)
                shutil.rmtree(filePath,True)
    return True

os.makedirs(snippetsDir, exist_ok=True)
cleanDir(snippetsDir)

#                     class    AAA    :       {func }
klassP =  re.compile('class\s+(\w+)\s*:?\s*(.*?)\s*{(.*?)}', re.S)

#                   void       func(  int a, int b)
funcP = re.compile('\w+[\s\*&]+(\w+)\((.*?)\)', re.S)
funcSP = re.compile('\s+static\s+\w+[\s\*&]+(\w+)\((.*?)\)', re.S)

#                   typedef enum {}typename;
enumP = re.compile('\s*enum[\s\S]*?{([\s\S]*?)}', re.S)
enumItem = re.compile('\s+([_a-zA-Z][_a-zA-Z0-9]*)', re.S)

def outDict():
    tpl = templateCompletion
    contentStr = ""
    for str in dictStr:
        contentStr = contentStr + '\t\t"' + str + '"' + ",\n"
    if len(contentStr) > 2:
        contentStr = contentStr[:-2]
    tpl = tpl.replace("%content",contentStr)
    ff = codecs.open(os.path.join(snippetsDir, "enum.sublime-completions"), "w", "utf-8")
    ff.write(tpl)
    ff.close()

def outputFunAPI(tree):
    contentStr = ""
    for klass in tree:
        contentStr = contentStr + outputKclass(klass,tree[klass])
        contentStr = contentStr + "\n"
    if len(contentStr) > 3:
        contentStr = contentStr[:-3]
    tpl = templateCompletion
    tpl = tpl.replace("%content",contentStr)
    ff = codecs.open(os.path.join(snippetsDir, "api.sublime-completions"), "w", "utf-8")
    ff.write(tpl)
    ff.close()    



def outputKclass(className, classData):
    contentStr = ""
    for sign in classData["func"]:
        funcData = classData["func"][sign]
        str = outPut(className, funcData["funcName"], funcData["args"], False)
        contentStr = contentStr + '\t\t' + str  + ",\n"
    if "static_func" in classData:
        for sign in classData["static_func"]:
            funcData = classData["static_func"][sign]
            str = outPut(className, funcData["funcName"], funcData["args"], True)
            contentStr = contentStr + '\t\t' + str  + ",\n"
    return contentStr

def outPut(klass, func, args, is_static):
    #print("write:", klass,func)
    tpl = templateCompletionItem
    if is_static == False:
        tpl = tpl.replace("%class:", "")    
    tpl = tpl.replace("%class", klass)
    tpl = tpl.replace("%func", func)
    argList = args.split(",")
    argVal = ""
    argHint = ""
    i = 1
    if args == "" or argList[0]=="void":
        argVal = ""
    else:
        for arg in argList:
            argVal += "${" + str(i) + ":" + arg + "}" + ","
            argHint += arg + ","
            i+=1
        argVal = argVal[:-1]
    tpl = tpl.replace("%args", argVal)
    tpl = tpl.replace("%argHint", argHint)
    return tpl

def getSuperKlass(str):
    if str == "":
        return []
    else:
        return re.sub(r"\s*public\s*", "", str).split(",")

def saveFuncSignature(table, funcStr, reg):
    funcs = reg.findall(funcStr)
    for func in funcs:
        funcName = func[0]
        args = re.sub(r",[\n\r\s]+", ",", func[1])
        args = re.sub(r"\s+", "_", args)
        signature = funcName + ":" + args
        table[signature] = {}
        table[signature]["funcName"] = funcName
        table[signature]["args"] = args

def getData(file):
    text = codecs.open(file, "r", "utf-8").read()
    text = re.sub(r"/\*[\S\s]*?\*/", "", text)
    text = re.sub(r"//[^\t\n]*", "", text)

    enumDefs = enumP.findall(text)
    for enumDef in enumDefs:
        #print(enumStrs)
        enumStrs = enumItem.findall(enumDef)
        for enumStr in enumStrs:
            #print(enumStr)
            if (enumStr in dictStr) == False:
                dictStr.append(enumStr)

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

        staticFuncData = klassData["static_func"] = {}
        saveFuncSignature(staticFuncData,funcStr,funcSP)
        funcStr = funcSP.sub("",funcStr)

        funcData = klassData["func"] = {}
        saveFuncSignature(funcData,funcStr,funcP)
        data[klassName] = klassData

for file in os.listdir(luaDir):
    #if(splitext(file)[1]==".pkg" and splitext(file)[0]=="CCApplication"):
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
    #print("________________________", klass, "___________________")
    if len(data[klass]["super"]) == 0:
        tree[klass] = data[klass]
    else:
        for superName in data[klass]["super"]:
            #print(superName)
            extends(data[klass], superName)


outputFunAPI(tree)
outDict()


if os.name == "nt":
    os.system("pause")
