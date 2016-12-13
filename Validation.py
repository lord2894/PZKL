import os
import pymorphy2
from nltk.corpus import stopwords
from Lemmatizer import Lemmatizer
from nltk.tokenize import TweetTokenizer
import re
import json
from collections import Counter
import requests

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
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]).lower())
                    elif "name" in lineSplt and docNum in corefs and corefNum in corefs[docNum]:
                        if not "corf" in corefs[docNum][corefNum]:
                            corefs[docNum][corefNum]["corf"] = []
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]).lower())
                    elif "firstname" in lineSplt and docNum in corefs and corefNum in corefs[docNum]:
                        if not "corf" in corefs[docNum][corefNum]:
                            corefs[docNum][corefNum]["corf"] = []
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]).lower())
                    elif "lastname" in lineSplt and docNum in corefs and corefNum in corefs[docNum]:
                        if not "corf" in corefs[docNum][corefNum]:
                            corefs[docNum][corefNum]["corf"] = []
                        corefs[docNum][corefNum]["corf"].append(' '.join(lineSplt[1:]).lower())
                openFile.close()
    return corefs
def longest_common_substring_words(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest:x_longest]

def main():
    devSetPatterns = 'E:\\PycharmProjects\\PZKL\\devsetOutput'
    factsPatterns = {}
    mainTree = os.walk(devSetPatterns)
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
                        if not docNum in factsPatterns:
                            factsPatterns[docNum] = {}
                        factNum = lineSplt[0].split('-')[1]
                        factsPatterns[docNum][factNum] = {}
                    elif "Type" in lineSplt and newFact:
                        factsPatterns[docNum][factNum]["type"] = lineSplt[1]
                    elif "Participant" in lineSplt and newFact:
                        if not "parts" in factsPatterns[docNum][factNum]:
                            factsPatterns[docNum][factNum]["parts"] = []
                        objspan = False
                        for item in lineSplt[1:]:
                            if "obj" in item:
                                factsPatterns[docNum][factNum]["parts"].append({"type":"obj","num":item[3:]})
                            elif "span" in item:
                                factsPatterns[docNum][factNum]["parts"].append({"type":"span","num":item[4:]})
                    else:
                        newFact = False
                openFile.close()
                #print(facts)
    devSetRuFactEval = 'E:\\PycharmProjects\\PZKL\\devset'
    factsRuFactEval = {}
    mainTree = os.walk(devSetRuFactEval)
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
                        if not docNum in factsRuFactEval:
                            factsRuFactEval[docNum] = {}
                        factNum = lineSplt[0].split('-')[1]
                        factsRuFactEval[docNum][factNum] = {}
                    elif "Type" in lineSplt and newFact:
                        factsRuFactEval[docNum][factNum]["type"] = lineSplt[1]
                    elif "Participant" in lineSplt and newFact:
                        if not "parts" in factsRuFactEval[docNum][factNum]:
                            factsRuFactEval[docNum][factNum]["parts"] = []
                        objspan = False
                        for item in lineSplt[1:]:
                            if "obj" in item:
                                factsRuFactEval[docNum][factNum]["parts"].append({"type":"obj","num":item[3:]})
                            elif "span" in item:
                                factsRuFactEval[docNum][factNum]["parts"].append({"type":"span","num":item[4:]})
                    else:
                        newFact = False
                openFile.close()
                #print(facts)
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
    print("Start Validation")
    allFactsPatternsCount = 0
    for book in factsPatterns:
        allFactsPatternsCount += len(factsPatterns[book])
    print("allFactsPatternsCount = ",allFactsPatternsCount)
    allFactsRuFactEvalCount = 0
    for book in factsRuFactEval:
        allFactsRuFactEvalCount += len(factsRuFactEval[book])
    print("allFactsRuFactEvalCount = ",allFactsRuFactEvalCount)
    trueFactsPatternsCount = 0
    #objWordsRuFactEval = {}
    # i = 0
    # for book in factsRuFactEval:
    #     for fact in factsPatterns[book]:
    #         newFactObjs = []
    #         for factObj in factsRuFactEval[book][fact]["parts"]:
    #             newFactObjs.append([])
    #             newFactObjs[i] += corefs[book][factObj["num"]]["corf"]
    #         objWordsRuFactEval[fact] = newFactObjs
    #         i += 1
    for book in factsPatterns:
        if book in factsRuFactEval:
            objWordsRuFactEval = {}
            for fact in factsRuFactEval[book]:
                if not fact in objWordsRuFactEval:
                    objWordsRuFactEval[fact] = []
                i=0
                for factObj in factsRuFactEval[book][fact]["parts"]:
                    objWordsRuFactEval[fact].append(set())
                    objWordsRuFactEval[fact][i].update(corefs[book][factObj["num"]]["corf"])
                    i += 1
            for fact in factsPatterns[book]:
                objWordsPatterns = []
                i = 0
                for factObj in factsPatterns[book][fact]["parts"]:
                    objWordsPatterns.append(set())
                    objWordsPatterns[i].update(corefs[book][factObj["num"]]["corf"])
                    baseObjWordsPatterns = list(objWordsPatterns[i])
                    for word in baseObjWordsPatterns:
                        wordSplt = word.split()
                        if len(wordSplt) == 1:
                            wordSplt = wordSplt[0]
                            try:
                                r = requests.get('http://ling.go.mail.ru/dsm/news/'+wordSplt+'/api/json', verify=False)
                                if r.status_code == 200 and not 'unknown' in r.content.decode("utf-8-sig"):
                                #reqDict = json.loads(r.content.decode("utf-8-sig"))
                                    reqDict = r.json()
                                    for key in reqDict["news"]:
                                        dict = list(reqDict["news"][key].items())
                                        dict.sort(key=lambda t: t[0])
                                        dict.sort(key=lambda t: t[1], reverse=True)
                                        objWordsPatterns[i].add(dict[0][0].split('_')[0])
                            except Exception as e:
                                print(e)
                    i+=1
                # objWordsRuFactEval = {}
                if len(objWordsPatterns) != 2:
                    print("error")
                    continue
                match = False
                for fact in objWordsRuFactEval:
                    if len(objWordsRuFactEval[fact]) != 2:
                        print("error "+book+" "+fact)
                        continue
                    sub1 = longest_common_substring_words(list(objWordsPatterns[0]),list(objWordsRuFactEval[fact][0]))
                    sub2 = longest_common_substring_words(list(objWordsPatterns[1]),list(objWordsRuFactEval[fact][1]))
                    if len(sub1) >= 1 and len(sub2) >= 1:
                        match = True
                        trueFactsPatternsCount += 1
                        break
                    else:
                        sub1 = longest_common_substring_words(list(objWordsPatterns[0]),list(objWordsRuFactEval[fact][1]))
                        sub2 = longest_common_substring_words(list(objWordsPatterns[1]),list(objWordsRuFactEval[fact][0]))
                        if len(sub1) >= 1 and len(sub2) >= 1:
                            match = True
                            trueFactsPatternsCount += 1
                            break
    print("trueFactsPatternsCount = ",trueFactsPatternsCount)
    Precision = trueFactsPatternsCount/allFactsPatternsCount
    Recall = trueFactsPatternsCount/allFactsRuFactEvalCount
    Fmeasure = 2*(Precision*Recall)/(Precision+Recall)
    print(Precision,Recall,Fmeasure)






if __name__ == "__main__":
    main()