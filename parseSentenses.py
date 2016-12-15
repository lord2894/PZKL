import os
import pymorphy2
from nltk.corpus import stopwords
from Lemmatizer import Lemmatizer
from nltk.tokenize import TweetTokenizer
import re
from collections import Counter

def sortByNumWords(inputStr):
    inputStrSplt = inputStr.split(' ')
    return len(inputStrSplt)

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
    return x_longest - longest,x_longest

def longest_common_substring_words_with_verb(s1, s2):
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
    substrsList =[]
    for i in range(1, 1 + len(s1)):
        for j in range(1, 1 + len(s2)):
            if m[i][j] != 0:
                substrsList.append((m[i][j],i-m[i][j],i))
    substrsList.sort(key=lambda t: t[1])
    substrsList.sort(key=lambda t: t[0], reverse=True)
    for substr in substrsList:
        s1_substr = s1[substr[1]:substr[2]]
        if 'V' in s1_substr:
            return substr[1],substr[2]
    return 0,0

def getFactsSents(inputFile):
    books = {}
    input = open(inputFile,"r",encoding="utf-8-sig")
    lastBook = ""
    for line in input:
        if "book_" in line:
            line = line.replace('\n','')
            books[line] = {}
            lastBook = line
            continue
        elif "|" in line:
            line = line.replace('\n','')
            lineSplt = line.split("|")
            if lineSplt[0].strip() in books[lastBook]:
                books[lastBook][lineSplt[0].strip()] += " " + lineSplt[1].strip()
            else:
                books[lastBook][lineSplt[0].strip()] = lineSplt[1].strip()
    return books

def getFacts(dir):
    facts = {}
    mainTree = os.walk(dir)
    for d in mainTree:
        for subf in d[2]:
            filePath = d[0] + "/" + subf
            if ".facts" in subf:
                openFile = open(filePath,"r",encoding = "utf-8-sig")
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
                        spanO = False
                        for item in lineSplt[1:]:
                            if "obj" in item:
                                spanO = False
                                facts[docNum][factNum]["parts"].append({"type":"obj","num":item[3:],"name":""})
                            elif "span" in item:
                                spanO = True
                                facts[docNum][factNum]["parts"].append({"type":"span","num":item[4:],"name":""})
                            elif spanO:
                                if item == "|":
                                    spanO = False
                                    continue
                                else:
                                    facts[docNum][factNum]["parts"][len(facts[docNum][factNum]["parts"])-1]["name"] += item + " "
                    else:
                        newFact = False
                openFile.close()
    return facts
def getCorefs(dir,facts):
    corefs = {}
    mainTree = os.walk(dir)
    for d in mainTree:
        for subf in d[2]:
            filePath = d[0] + "/" + subf
            if ".coref" in subf:
                docNum = subf.split(".")[0]
                #print(docNum)
                if docNum in facts:
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
                            contain = False
                            for fact in facts[docNum]:
                                obj = [part for part in facts[docNum][fact]["parts"] if part["type"] == "obj" and part["num"] == corefNum]
                                if len(obj) > 0:
                                    contain = True
                                    break
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

def main():
    books ={}
    books.update(getFactsSents("devset_short.txt"))
    books.update(getFactsSents("testset_short.txt"))
    devSet = 'E:\\PycharmProjects\\PZKL\\devset'
    facts = getFacts('E:\\PycharmProjects\\PZKL\\devset')
    corefs = getCorefs('E:\\PycharmProjects\\PZKL\\devset',facts)
    facts.update(getFacts('E:\\PycharmProjects\\PZKL\\testset'))
    corefs.update(getCorefs('E:\\PycharmProjects\\PZKL\\testset',facts))
    pathToWordNetDict = "C:\\WordNet\\dict"
    wordPatternEng = re.compile(u"^((?:[a-zA-Z]+)(?:[-']([?:[a-zA-Z]+))*)$")
    wordPatternRus = re.compile(u"^((?:[а-яА-яЁё]+)(?:[-]([?:[а-яА-яЁё]+))*)$")
    RuLemmatizer = pymorphy2.MorphAnalyzer()
    EngLemmatizer = Lemmatizer(pathToWordNetDict)
    tokenizer = TweetTokenizer(reduce_len=True, preserve_case=True)
    stopwords_eng = set(stopwords.words('english'))
    stopwords_rus = set(stopwords.words('russian'))
    PUNCTUATION = [u';', u':', u',', u'.',
       u'!', u'?', u'...', u'…',
       u'»', u'«', u'\\', u'-',
       u'{', u'..', u'|', u'—',
       u'&', u'*', u'@', u'#',
       u'^', u'(', u')', u'_'
       u'/', u'%', u'$', u'№',
       u'\'', u'\"', u'~', u'[',
       u']', u'+', u'=', u'’',
       u'>', u'<', ]
    output = open("devsetSents.txt","w",encoding="utf-8-sig")
    outputSents = set()
    for book in books:
        for fact in books[book]:
            tokens = tokenizer.tokenize(books[book][fact])
            normTokens = []
            for token in tokens:
                if not token in PUNCTUATION:
                    if wordPatternEng.match(token):
                        word = token.upper()# Приводим слово к нижнему регистру
                        lemma = EngLemmatizer.GetLemma(word).upper() 	# Нормализуем слово
                        if (lemma != ""):
                            normTokens.append(lemma)
                        else:
                            normTokens.append(word)
                    elif wordPatternRus.match(token):
                        word = token.upper()# Приводим слово к нижнему регистру
                        lemma = list(RuLemmatizer.normal_forms(word))[0].upper()#.encode("utf-8") 	# Нормализуем слово
                        if (lemma != ""):
                            normTokens.append(lemma)
                        else:
                            normTokens.append(word)
                    else:
                        normTokens.append(token.upper())
            normFact = ' '.join(normTokens)
            k = 0
            for part in facts[book][fact]["parts"]:
                if part["type"] == "obj":
                    corefs[book][part["num"]]["corf"].sort(key=sortByNumWords, reverse=True)
                    for cor in corefs[book][part["num"]]["corf"]:
                        cor = cor.strip()
                        if not cor in ['',' ','\n']:
                            tokens = tokenizer.tokenize(cor)
                            normTokensCor = []
                            for token in tokens:
                                if not token in PUNCTUATION:
                                    if wordPatternEng.match(token):
                                        word = token.upper()# Приводим слово к нижнему регистру
                                        lemma = EngLemmatizer.GetLemma(word).upper() 	# Нормализуем слово
                                        if (lemma != ""):
                                            normTokensCor.append(lemma)
                                        else:
                                            normTokensCor.append(word)
                                    elif wordPatternRus.match(token):
                                        word = token.upper()# Приводим слово к нижнему регистру
                                        lemma = list(RuLemmatizer.normal_forms(word))[0].upper()#.encode("utf-8") 	# Нормализуем слово
                                        if (lemma != ""):
                                            normTokensCor.append(lemma)
                                        else:
                                            normTokensCor.append(word)
                                    else:
                                        normTokensCor.append(token)
                                else:
                                    normTokensCor.append(token)
                            normCor = ' '.join(normTokensCor)
                            normFact = normFact.replace(normCor, str(k) + "FactEntity")
                        # if "0FactEntity00FactEntityF0Fac" in normFact:
                        #     print("here")
                elif part["type"] == "span":
                    tokens = tokenizer.tokenize(part["name"])
                    normTokensCor = []
                    for token in tokens:
                        if not token in PUNCTUATION:
                            if wordPatternEng.match(token):
                                word = token.upper()# Приводим слово к нижнему регистру
                                lemma = EngLemmatizer.GetLemma(word).upper() 	# Нормализуем слово
                                if (lemma != ""):
                                    normTokensCor.append(lemma)
                                else:
                                    normTokensCor.append(word)
                            elif wordPatternRus.match(token):
                                word = token.upper()# Приводим слово к нижнему регистру
                                lemma = list(RuLemmatizer.normal_forms(word))[0].upper()#.encode("utf-8") 	# Нормализуем слово
                                if (lemma != ""):
                                    normTokensCor.append(lemma)
                                else:
                                    normTokensCor.append(word)
                            else:
                                normTokensCor.append(token)
                        else:
                            normTokensCor.append(token)
                    normCor = ' '.join(normTokensCor)
                    normFact = normFact.replace(normCor, str(k) + "FactEntity") #str(part["num"])
                k += 1

            newTokens = tokenizer.tokenize(normFact)
            prevToken = ""
            newTokensClear = []
            newTokensPOS = []
            for token in newTokens:
                if token == prevToken:
                    continue
                else:
                    if "FactEntity" in token:
                        newTokensClear.append(token)
                        newTokensPOS.append(token)
                    else:
                        if wordPatternEng.match(token):
                            newTokensClear.append(token)
                            newTokensPOS.append("W")
                        elif wordPatternRus.match(token):
                            newTokensClear.append(token)
                            keyPOS = RuLemmatizer.parse(token)[0].tag.POS
                            if keyPOS == "NOUN":
                                newTokensPOS.append("N")
                            elif keyPOS in ["ADJF","ADJS","COMP"]:
                                newTokensPOS.append("A")
                            elif keyPOS == "VERB" or keyPOS == "INFN":
                                newTokensPOS.append("V")
                            elif keyPOS == "PRTF" or keyPOS == "PRTS":
                                newTokensPOS.append("Pa")
                            elif keyPOS == "GRND":
                                newTokensPOS.append("Ap")
                            elif keyPOS == "NUMR":
                                newTokensPOS.append("Num")
                            elif keyPOS == "ADVB" or keyPOS == "PRED":
                                newTokensPOS.append("Av")
                            elif keyPOS == "NPRO":
                                newTokensPOS.append("Pn")
                            elif keyPOS == "PREP":
                                newTokensPOS.append("Pr")
                            elif keyPOS == "CONJ":
                                newTokensPOS.append("Cn")
                            elif keyPOS == "INTJ":
                                newTokensPOS.append("Int")
                            else:
                                newTokensPOS.append("W")
                        else:
                            newTokensClear.append(token)
                            newTokensPOS.append("W")
                prevToken = token
            outputSents.add(' '.join(newTokensClear).replace("\n",'')+" | "+' '.join(newTokensPOS).replace("\n",'')+"\n")

    sentencies = []
    pattern = False
    for i,s in enumerate(outputSents):
        newsentpat = {}
        newsentpat["pat"] = []
        newsentpat["sent"] = []
        splt = s.split('|')
        output.write(splt[0].strip()+"\n")
        output.write(splt[1].strip())
        output.write("\n\n")
        patSplt = splt[1].split()
        sentSplt = splt[0].split()
        newpat = []
        newsent = []
        for j, pSplt in enumerate(patSplt):
            if "FactEntity" in pSplt:
                patSplt[j] = "FactEntity"
                if not pattern:
                    pattern = True
                    newpat = []
                    newsent = []
                else:
                    # pattern = False
                    if len(newpat)> 0 and 'V' in newpat:
                        newsentpat["pat"].append(newpat)
                        newsentpat["sent"].append(newsent)
                        # newsent.append(newpat)
                    newpat = []
                    newsent = []
            else:
                if pattern:
                    newpat.append(pSplt)
                    newsent.append(sentSplt[j])
                    # newpat.append(pSplt)
        if len(newsentpat["pat"]) > 0:
            sentencies.append(newsentpat)

                # for item in patSplt:
        #     if "FactEntity" in item:
        #         item = "FactEntity"
        # patterns.append(patSplt)
    output.close()
    similarParts = Counter()
    patterns = {}
    co = 0
    output = open("testsetPatterns.txt","w",encoding="utf-8-sig")
    for i in range(0,len(sentencies)):
        for k in range(0,len(sentencies[i]["pat"])):
            for j in range(i+1,len(sentencies)):
                for p in range(0,len(sentencies[j]["pat"])):
                    longestFrom, longestTo = longest_common_substring_words_with_verb(sentencies[i]["pat"][k],sentencies[j]["pat"][p])
                    longestSbstr = sentencies[i]["pat"][k][longestFrom:longestTo]
                    if len(longestSbstr) > 0 and 'V' in longestSbstr:
                        newpattern = ' '.join(longestSbstr)
                        if not newpattern in patterns:
                            patterns[newpattern] = {}
                            patterns[newpattern]["words"] = set()
                            patterns[newpattern]["minLeft"] = 100
                            patterns[newpattern]["minRight"] = 100
                            patterns[newpattern]["maxLeft"] = 0
                            patterns[newpattern]["maxRight"] = 0
                        if not newpattern in similarParts:
                            similarParts[newpattern] = 0
                        else:
                            similarParts[newpattern] += 1
                        longestFrom2, longestTo2 = longest_common_substring_words_with_verb(sentencies[j]["pat"][p],longestSbstr)
                        patterns[newpattern]["words"].add(' '.join(sentencies[i]["sent"][k][longestFrom:longestTo]))
                        patterns[newpattern]["words"].add(' '.join(sentencies[j]["sent"][p][longestFrom2:longestTo2]))
                        if longestFrom < patterns[newpattern]["minLeft"]:
                            patterns[newpattern]["minLeft"] = longestFrom
                        if longestFrom > patterns[newpattern]["maxLeft"]:
                            patterns[newpattern]["maxLeft"] = longestFrom
                        if longestFrom2 < patterns[newpattern]["minLeft"]:
                            patterns[newpattern]["minLeft"] = longestFrom2
                        if longestFrom2 > patterns[newpattern]["maxLeft"]:
                            patterns[newpattern]["maxLeft"] = longestFrom2

                        if len(sentencies[i]["pat"][k])-longestTo < patterns[newpattern]["minRight"]:
                            patterns[newpattern]["minRight"] = len(sentencies[i]["pat"][k])-longestTo
                        if len(sentencies[i]["pat"][k])-longestTo > patterns[newpattern]["maxRight"]:
                            patterns[newpattern]["maxRight"] = len(sentencies[i]["pat"][k])-longestTo
                        if len(sentencies[j]["pat"][p])-longestTo2 < patterns[newpattern]["minRight"]:
                            patterns[newpattern]["minRight"] = len(sentencies[j]["pat"][p])-longestTo2
                        if len(sentencies[j]["pat"][p])-longestTo2 > patterns[newpattern]["maxRight"]:
                            patterns[newpattern]["maxRight"] = len(sentencies[j]["pat"][p])-longestTo2
                        co += 1
                    # if longestSbstr[0] == "FactEntity" and longestSbstr[len(longestSbstr)-1] == "FactEntity" and len(longestSbstr)>1:
                    #     similarParts.append(longestSbstr)
    dict = list(similarParts.items())
    dict.sort(key=lambda t: t[0])
    dict.sort(key=lambda t: t[1], reverse=True)

    jsonText = "{"
    i = 0
    for item in dict:
        jsonText += "\""+item[0]+"\" : {"
        # jsonText += "\""+"count"+"\" : "+str(item[1]) + ",\n"
        jsonText += "\""+"minLeft"+"\" : "+str(patterns[item[0]]["minLeft"]) + ",\n"
        jsonText += "\""+"maxLeft"+"\" : "+str(patterns[item[0]]["maxLeft"]) + ",\n"
        jsonText += "\""+"minRight"+"\" : "+str(patterns[item[0]]["minRight"]) + ",\n"
        jsonText += "\""+"maxRight"+"\" : "+str(patterns[item[0]]["maxRight"]) + ",\n"
        jsonText += "\""+"words"+"\" : [\n"
        for j,it in enumerate(patterns[item[0]]["words"]):
            jsonText += "\""+it+"\""
            if j != len(patterns[item[0]]["words"])-1:
                jsonText += ","
        jsonText += "]}"
        if i != len(dict)-1:
            jsonText += ",\n"
        else:
            jsonText += "}"
        i+=1
    output.write(jsonText)
    # for item in dict:
    #     output.write(item[0]+"\n")
    #     for var in patterns[item[0]]:
    #         output.write("\t"+var+"\n")
    #     output.write("\n\n")
    output.close()


if __name__ == "__main__":
    main()