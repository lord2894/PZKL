import os
import pymorphy2
from nltk.corpus import stopwords
from Lemmatizer import Lemmatizer
from nltk.tokenize import TweetTokenizer
import re
import json
from collections import Counter

def getTexts(dir):
    booksTexts = {}
    mainTree = os.walk(dir)
    for d in mainTree:
        for subf in d[2]:
            filePath = d[0] + "/" + subf
            if ".txt" in subf:
                docNum = subf.split(".")[0]
                openFile = open(filePath,"r",encoding = "utf-8-sig")
                text = openFile.read()
                book = {}
                textSplt = text.split("|")
                book["text"] = textSplt[0]
                book["pos"] = textSplt[1]
                booksTexts[docNum] = book
                openFile.close()
    return booksTexts
def getCorefs(dir):
    corefs = {}
    mainTree = os.walk(dir)
    for d in mainTree:
        for subf in d[2]:
            filePath = d[0] + "/" + subf
            if ".coref" in subf:
                docNum = subf.split(".")[0]
                #print(docNum)
                openFile = open(filePath,"r",encoding = "utf-8-sig")
                corefNum = None
                spaceLine = True
                newCoref = True
                for line in openFile:
                    if line == "" or line == "\n":
                        spaceLine = True
                        continue
                    lineSplt = line.split()
                    if spaceLine:
                        newCoref = True
                        spaceLine = False
                        corefNum = lineSplt[0]
                        contain = True
                        # for fact in facts[docNum]:
                        #     obj = [part for part in facts[docNum][fact]["parts"] if part["type"] == "obj" and part["num"] == corefNum]
                        #     if len(obj) > 0:
                        #         contain = True
                        #         break
                        if contain:
                            if not docNum in corefs:
                                corefs[docNum] = {}
                            corefs[docNum][corefNum] = {}
                            corefs[docNum][corefNum]["objs"] = []
                            for item in lineSplt[1:]:
                                corefs[docNum][corefNum]["objs"].append(item)
                    elif "descriptor" in lineSplt and docNum in corefs and corefNum in corefs[docNum]:
                        if not "corf" in corefs[docNum][corefNum]:
                            corefs[docNum][corefNum]["corf"] = []
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]))
                    elif "name" in lineSplt and docNum in corefs and corefNum in corefs[docNum]:
                        if not "corf" in corefs[docNum][corefNum]:
                            corefs[docNum][corefNum]["corf"] = []
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]))
                    elif "firstname" in lineSplt and docNum in corefs and corefNum in corefs[docNum]:
                        if not "corf" in corefs[docNum][corefNum]:
                            corefs[docNum][corefNum]["corf"] = []
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]))
                    elif "lastname" in lineSplt and docNum in corefs and corefNum in corefs[docNum]:
                        if not "corf" in corefs[docNum][corefNum]:
                            corefs[docNum][corefNum]["corf"] = []
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]))
                openFile.close()
    return corefs
def getBookParts(book):
    posSplt = book["pos"].split()
    textSplt = book["text"].split()
    parts = {}
    parts["pat"] = []
    parts["sent"] = []
    parts["inds"] = []
    parts["objects"] = []
    newpat = []
    newsent = []
    factEntity = False
    oldEntity = ""
    for i,token in enumerate(posSplt):
        if "FactEntity" in token:
            if factEntity:
                #factEntity = False
                if len(newpat)> 0 and 'V' in newpat:
                    parts["pat"].append(newpat)
                    parts["sent"].append(newsent)
                    parts["inds"].append(i)
                    parts["objects"].append({"first":oldEntity,"second":token})
                    oldEntity = token
                newpat = []
                newsent = []
            else:
                factEntity = True
                newpat = []
                newsent = []
                newobject = {}
                oldEntity = token
        else:
            if factEntity:
                newpat.append(token)
                newsent.append(textSplt[i])
    return parts

def find_sub_list(sl,l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll] == sl:
            results.append((ind,ind+sll-1))
    return results

def findFirst_sub_list(sl,l):
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return ind,ind+sll-1

def getPatterns(inputFile):
    openFile = open(inputFile,"r",encoding = "utf-8-sig")
    jsonText = openFile.read()
    jsonDicts = json.loads(jsonText)
    openFile.close()
    return jsonDicts

def main():
    books = {}
    books.update(getTexts('E:\\PycharmProjects\\PZKL\\devsetNorm'))
    patterns = {}
    patterns.update(getPatterns('E:\\PycharmProjects\\PZKL\\testsetPatterns.txt'))
    result = {}
    corefsFiles = {}
    corefsFiles.update(getCorefs('E:\\PycharmProjects\\PZKL\\devset'))
    corefs = {}
    for book in corefsFiles:
        for corefNum in corefsFiles[book]:
            if "corf" in corefsFiles[book][corefNum]:
                if not book in corefs:
                    corefs[book] = {}
                if not corefNum in corefs[book]:
                    corefs[book][corefNum] = {}
                corefs[book][corefNum] = corefsFiles[book][corefNum]
    corefsFiles.clear()
    for book in books:
        parts = getBookParts(books[book])
        for partInd,part in enumerate(parts["pat"]):
            for pattern in patterns:
                #matches = find_sub_list(part,pattern.split())
                matches = find_sub_list(pattern.split(),part)
                for match in matches:
                    wordS =  ' '.join(parts["sent"][partInd][match[0]:match[1]+1])
                    if wordS in patterns[pattern]["words"]:
                        if match[0] >= patterns[pattern]["minLeft"] and match[0] <= patterns[pattern]["maxLeft"]:
                            if len(part)-(match[1]+1) >= patterns[pattern]["minRight"]  \
                               and len(part)-(match[1]+1) <= patterns[pattern]["maxRight"] \
                               and match[0] >= patterns[pattern]["minLeft"] \
                               and match[0] <= patterns[pattern]["maxLeft"]:
                                if not book in result:
                                    result[book] = {}
                                    result[book]["pat"] = []
                                    result[book]["pattern"] = []
                                result[book]["pat"].append(partInd)
                                result[book]["pattern"].append(pattern)
                                # Добавить в результат
                    else:
                        continue
        if book in result:
            outputFileFacts = open("E:\\PycharmProjects\\PZKL\\devsetOutput\\"+book+".facts","w",encoding="utf-8-sig")
            outputFileFactsInfo = open("E:\\PycharmProjects\\PZKL\\devsetOutput\\"+book+".factsinfo","w",encoding="utf-8-sig")
            bookNum = book.split('_')[1]
            uniqParts = set()
            for res in result[book]["pat"]:
                uniqParts.add(res)
            for ind,res in enumerate(uniqParts):
                #.fact
                outputFileFacts.write(bookNum+"-"+str(ind+1)+" Deal\n")
                partNum1 = parts["objects"][res]["first"].replace("FactEntity","")
                partNum2 = parts["objects"][res]["second"].replace("FactEntity","")
                outputFileFacts.write("Participant obj"+partNum1)
                for l,coref in enumerate(corefs[book][partNum1]["corf"]):
                    outputFileFacts.write(" "+coref)
                    if l != len(corefs[book][partNum1]["corf"])-1:
                        outputFileFacts.write(" |")
                outputFileFacts.write("\n")
                outputFileFacts.write("Participant obj"+partNum2)
                for l,coref in enumerate(corefs[book][partNum2]["corf"]):
                    outputFileFacts.write(" "+coref)
                    if l != len(corefs[book][partNum2]["corf"])-1:
                        outputFileFacts.write(" |")
                outputFileFacts.write("\n\n")
                #.factinfo
                outputFileFactsInfo.write(bookNum+"-"+str(ind+1)+" Deal\n")
                partNum1 = parts["objects"][res]["first"].replace("FactEntity","")
                partNum2 = parts["objects"][res]["second"].replace("FactEntity","")
                outputFileFactsInfo.write("Participant obj"+partNum1)
                for l,coref in enumerate(corefs[book][partNum1]["corf"]):
                    outputFileFactsInfo.write(" "+coref)
                    if l != len(corefs[book][partNum1]["corf"])-1:
                        outputFileFactsInfo.write(" |")
                outputFileFactsInfo.write("\n")
                outputFileFactsInfo.write("Participant obj"+partNum2)
                for l,coref in enumerate(corefs[book][partNum2]["corf"]):
                    outputFileFactsInfo.write(" "+coref)
                    if l != len(corefs[book][partNum2]["corf"])-1:
                        outputFileFactsInfo.write(" |")
                outputFileFactsInfo.write("\n")
                outputFileFactsInfo.write(' '.join(parts["sent"][res])+"\n")
                outputFileFactsInfo.write(' '.join(parts["pat"][res])+"\n")
                outputFileFactsInfo.write("\n")




# 215-1 Deal
# Participant obj277 Майкрософт
# Participant obj278 ЕС | Европейский союз
# Type наложение/выплата штрафа




if __name__ == "__main__":
    main()