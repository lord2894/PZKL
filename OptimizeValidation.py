import shutil
import os
import json
import requests


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
                try:
                    book["text"] = textSplt[0]
                    book["pos"] = textSplt[1]
                except Exception as e:
                    print(docNum)
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
def getProcessBook(patterns):
    if os.path.exists("E:\\PycharmProjects\\PZKL\\testsetOutput"):
        shutil.rmtree("E:\\PycharmProjects\\PZKL\\testsetOutput")
    if not os.path.exists("E:\\PycharmProjects\\PZKL\\testsetOutput"):
        os.makedirs("E:\\PycharmProjects\\PZKL\\testsetOutput", mode=0o777)
    books = {}
    books.update(getTexts('E:\\PycharmProjects\\PZKL\\testsetNorm'))
    result = {}
    corefsFiles = {}
    corefsFiles.update(getCorefs('E:\\PycharmProjects\\PZKL\\testset'))
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
            outputFileFacts = open("E:\\PycharmProjects\\PZKL\\testsetOutput\\"+book+".facts","w",encoding="utf-8-sig")
            outputFileFactsInfo = open("E:\\PycharmProjects\\PZKL\\testsetOutput\\"+book+".factsinfo","w",encoding="utf-8-sig")
            bookNum = book.split('_')[1]
            uniqParts = set()
            for res in result[book]["pat"]:
                uniqParts.add(res)
            for ind,res in enumerate(uniqParts):
                #.fact
                outputFileFacts.write(bookNum+"-"+str(ind+1)+" Deal\n")
                try:
                    partNum1 = parts["objects"][res]["first"].replace("FactEntity","")
                    partNum2 = parts["objects"][res]["second"].replace("FactEntity","")
                    outputFileFacts.write("Participant obj"+partNum1)
                    for l,coref in enumerate(corefs[book][partNum1]["corf"]):
                        outputFileFacts.write(" "+coref)
                        if l != len(corefs[book][partNum1]["corf"])-1:
                            outputFileFacts.write(" |")
                    outputFileFacts.write("\n")
                    outputFileFacts.write("Participant obj"+partNum2)
                    try:
                        for l,coref in enumerate(corefs[book][partNum2]["corf"]):
                            outputFileFacts.write(" "+coref)
                            if l != len(corefs[book][partNum2]["corf"])-1:
                                outputFileFacts.write(" |")
                        outputFileFacts.write("\n\n")
                    except Exception as e:
                        print(book,res,e)
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
                except Exception as e:
                    print(bookNum,res)
                    continue
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
def getValidation():
    devSetPatterns = 'E:\\PycharmProjects\\PZKL\\testsetOutput'
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
    devSetRuFactEval = 'E:\\PycharmProjects\\PZKL\\testset'
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
    corefsFiles.update(getCorefs('E:\\PycharmProjects\\PZKL\\testset'))
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
                    try:
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
                    except Exception as e:
                        print(book, factObj["num"])
                        print(factObj)
                        continue
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
    if allFactsPatternsCount != 0:
        Precision = trueFactsPatternsCount/allFactsPatternsCount
    else:
        Precision = 0
    if allFactsRuFactEvalCount != 0:
        Recall = trueFactsPatternsCount/allFactsRuFactEvalCount
    else:
        Recall = 0
    if Precision != 0 or Recall != 0:
        Fmeasure = 2*(Precision*Recall)/(Precision+Recall)
    else:
        Fmeasure = 0
    print(Precision,Recall,Fmeasure)
    return trueFactsPatternsCount,Fmeasure

def main():
    patterns = {}
    patterns.update(getPatterns('E:\\PycharmProjects\\PZKL\\testsetPatterns.txt'))
    newPatterns = {}
    maxTrueFactsPatternsCount = 0
    maxFmeasure = 0
    for pattern in patterns:
        if not pattern in newPatterns:
            newPatterns[pattern] = {}
        if not "minLeft" in newPatterns[pattern]:
            newPatterns[pattern]["minLeft"] = patterns[pattern]["minLeft"]
        if not "maxLeft" in newPatterns[pattern]:
            newPatterns[pattern]["maxLeft"] = patterns[pattern]["maxLeft"]
        if not "minRight" in newPatterns[pattern]:
            newPatterns[pattern]["minRight"] = patterns[pattern]["minRight"]
        if not "maxRight" in newPatterns[pattern]:
            newPatterns[pattern]["maxRight"] = patterns[pattern]["maxRight"]
        if not "words" in newPatterns[pattern]:
            newPatterns[pattern]["words"] = []
        for word in patterns[pattern]["words"]:
            newPatterns[pattern]["words"].append(word)
            getProcessBook(newPatterns)
            trueFactsPatternsCount,Fmeasure = getValidation()
            if trueFactsPatternsCount > maxTrueFactsPatternsCount and Fmeasure > maxFmeasure:
                maxTrueFactsPatternsCount = trueFactsPatternsCount
                maxFmeasure = Fmeasure
            else:
                newPatterns[pattern]["words"].remove(word)
    jsonText = ""
    output = open('E:\\PycharmProjects\\PZKL\\testsetPatternsNEW_normalOptimize.txt','w',encoding="utf-8-sig")
    i=0
    for pattern in newPatterns:
        jsonText += "\""+pattern+"\" : {"
        # jsonText += "\""+"count"+"\" : "+str(item[1]) + ",\n"
        jsonText += "\""+"minLeft"+"\" : "+str(newPatterns[pattern]["minLeft"]) + ",\n"
        jsonText += "\""+"maxLeft"+"\" : "+str(newPatterns[pattern]["maxLeft"]) + ",\n"
        jsonText += "\""+"minRight"+"\" : "+str(newPatterns[pattern]["minRight"]) + ",\n"
        jsonText += "\""+"maxRight"+"\" : "+str(newPatterns[pattern]["maxRight"]) + ",\n"
        jsonText += "\""+"words"+"\" : [\n"
        for j,it in enumerate(newPatterns[pattern]["words"]):
            jsonText += "\""+it+"\""
            if j != len(newPatterns[pattern]["words"])-1:
                jsonText += ","
        jsonText += "]}"
        if i != len(newPatterns)-1:
            jsonText += ",\n"
        else:
            jsonText += "}"
        i+=1
    output.write(jsonText)




if __name__ == "__main__":
    main()