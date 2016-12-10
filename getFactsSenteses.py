# -*- coding: utf-8 -*-
import os
import json
import math
from collections import Counter

def main():
    devSet = '/media/D/factRuEval/devset'
    facts = {}
    corefs = {}
    objects = {}
    spans = {}
    tokens = {}
    mainTree = os.walk(devSet)
    outputFile = open("devset.txt","w",encoding="utf-8")
    sentenses = {}
    for d in mainTree:
        for subf in d[2]:
            filePath = d[0] + "/" + subf
            if ".facts" in subf:
                openFile = open(filePath,"r",encoding = "utf-8")
                docNum = None
                factNum = None
                newFact = True
                for line in openFile:
                    lineSplt = line.split()
                    if "Deal" in lineSplt:
                        newFact = True  
                        docNum = subf.split(".")[0]
                        if not docNum in facts:
                            facts[docNum] = {}
                        factNum = lineSplt[0].split('-')[1]
                        facts[docNum][factNum] = {} 
                    elif "Type" in lineSplt and newFact:
                        facts[docNum][factNum]["type"] = lineSplt[1]
                    elif "Participant" in lineSplt and newFact:
                        if not "parts" in facts[docNum][factNum]:
                            facts[docNum][factNum]["parts"] = []
                        objspan = False
                        for item in lineSplt[1:]:
                            if "obj" in item:
                                facts[docNum][factNum]["parts"].append({"type":"obj","num":item[3:]})
                            elif "span" in item:
                                facts[docNum][factNum]["parts"].append({"type":"span","num":item[4:]})
                    else:
                        newFact = False  
                openFile.close()   
                #print(facts)  
        for subf in d[2]:
            filePath = d[0] + "/" + subf                 
            if ".coref" in subf:
                docNum = subf.split(".")[0]
                #print(docNum)
                if docNum in facts:
                    openFile = open(filePath,"r",encoding = "utf-8")
                    corefNum = None
                    spaceLine = True
                    newCoref = True
                    for line in openFile:
                        #print(line)
                        if line == "" or line == "\n":
                            spaceLine = True
                            continue
                        lineSplt = line.split()
                        if spaceLine:
                            newCoref = True
                            spaceLine = False
                            corefNum = lineSplt[0]
                            contain = False
                            for fact in facts[docNum]:
                                obj = [part for part in facts[docNum][fact]["parts"] if part["type"]=="obj" and part["num"] == corefNum]
                                if len(obj) > 0:
                                    contain = True
                                    break
                            if contain:
                                if not docNum in corefs:
                                    corefs[docNum] = {}
                                corefs[docNum][corefNum] = []
                                for item in lineSplt[1:]:
                                    corefs[docNum][corefNum].append(item)
                    openFile.close()
        for subf in d[2]:
            filePath = d[0] + "/" + subf                 
            if ".objects" in subf:
                docNum = subf.split(".")[0]
                #print(docNum)
                if docNum in corefs:
                    openFile = open(filePath,"r",encoding = "utf-8")
                    objectNum = None
                    for line in openFile:
                        lineSplt = line.split()
                        objectNum = lineSplt[0]
                        contain = False
                        for coref in corefs[docNum]:
                            obj = [ob for ob in corefs[docNum][coref] if ob == objectNum]
                            if len(obj) > 0:
                                contain = True
                                break
                        if contain:
                            if not docNum in objects:
                                objects[docNum] = {}
                            objects[docNum][objectNum] = {}
                            objects[docNum][objectNum]["type"] = lineSplt[1]
                            objects[docNum][objectNum]["spans"] = []
                            for item in lineSplt[2:]:
                                if item != "#":
                                    objects[docNum][objectNum]["spans"].append(item)
                                else:
                                    break
                    openFile.close()
            #print(objects)  
        for subf in d[2]:
            filePath = d[0] + "/" + subf                 
            if ".spans" in subf:
                docNum = subf.split(".")[0]
                #print(docNum)
                if docNum in objects:
                    #print(docNum)
                    openFile = open(filePath,"r",encoding = "utf-8")
                    spanNum = None
                    for line in openFile:
                        lineSplt = line.split()
                        spanNum = lineSplt[0]
                        contain = False
                        for fact in facts[docNum]:
                            obj = [part for part in facts[docNum][fact]["parts"] if part["type"]=="span" and part["num"] == spanNum]
                            if len(obj) > 0:
                                contain = True
                                break
                        #print(spanNum,objects[docNum])
                        obj = [ob for ob in objects[docNum] if spanNum in objects[docNum][ob]["spans"]]
                        if len(obj) > 0:
                            contain = True
                        if contain:
                            if not docNum in spans:
                                spans[docNum] = {}
                            spans[docNum][spanNum] = {}
                            spans[docNum][spanNum]["type"] = lineSplt[1]
                            spans[docNum][spanNum]["token"] = lineSplt[4]
                    openFile.close()
            #print(spans)  
        for subf in d[2]:
            filePath = d[0] + "/" + subf                 
            if ".tokens" in subf:
                docNum = subf.split(".")[0]
                if docNum in spans:
                    openFile = open(filePath,"r",encoding = "utf-8")
                    tokens[docNum] = {}
                    tokens[docNum]["sens"] = []
                    tokens[docNum]["tokens"] = {}
                    tokenNum = None
                    newSentence = True
                    sentenceNum = 0
                    for line in openFile:
                        if line == "" or line == "\n":
                            newSentence = True
                            continue
                        lineSplt = line.split()
                        if newSentence:
                            newSentence = False
                            sentenceNum = len(tokens[docNum]["sens"])
                            tokens[docNum]["sens"].append([])
                            tokens[docNum]["sens"][sentenceNum].append(lineSplt[0])
                            tokens[docNum]["tokens"][lineSplt[0]] = lineSplt[3]
                        else:
                            tokens[docNum]["sens"][sentenceNum].append(lineSplt[0])
                            tokens[docNum]["tokens"][lineSplt[0]] = lineSplt[3]
                    openFile.close()
    for doc in facts:
        sentenses[doc] = {}
        # print("doc",doc)
        for fact in facts[doc]:
            sentenses[doc][fact] = set()
            # print("facts",fact,facts[doc])
            # print("\n")
            for part in facts[doc][fact]["parts"]:
                if part["type"] == "obj":
                    # print("coref",part)
                    # print("\n")
                    for obj in corefs[doc][part["num"]]:
                        # print("objects",corefs[doc][part["num"]])
                        # print("\n")
                        for span in objects[doc][obj]["spans"]:
                            # print("spans",objects[doc][obj]["spans"])
                            # print("\n")
                            tokenNum = spans[doc][span]["token"]
                            for sent in tokens[doc]["sens"]:
                                if tokenNum in sent:
                                    sentence = ""
                                    for tok in sent:
                                        sentence += " " + tokens[doc]["tokens"][tok]
                                    sentenses[doc][fact].add(fact + " | "+ sentence+"\n")
                                    #outputFile.write(sentence+"\n")
                elif part["type"] == "span":
                    tokenNum = spans[doc][part["num"]]["token"]
                    for sent in tokens[doc]["sens"]:
                        if tokenNum in sent:
                            sentence = ""
                            for tok in sent:
                                sentence += " " + tokens[doc]["tokens"][tok]
                            #print(sentence)
                            sentenses[doc][fact].add(fact + " | "+ sentence+"\n")
                            #outputFile.write(sentence+"\n")
    for doc in sentenses:
        outputFile.write(doc+"\n")
        for fact in sentenses[doc]:
            for sent in sentenses[doc][fact]:
                outputFile.write(sent)
            outputFile.write("\n")
        outputFile.write("\n\n\n\n")
    outputFile.close()
if __name__ == "__main__":
    main()