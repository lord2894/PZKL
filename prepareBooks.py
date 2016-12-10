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
    #return s1[x_longest - longest: x_longest]

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
                booksTexts[docNum] = text
                openFile.close()
    return booksTexts

def main():
    #books ={}
    booksTexts = {}
    booksTexts.update(getTexts('E:\\PycharmProjects\\PZKL\\devset'))
    #books.update(getFactsSents("testset_short_3.txt"))
    #facts = {}
    corefs = {}
    corefsFiles = {}
    #facts.update(getFacts('E:\\PycharmProjects\\PZKL\\devset'))
    corefsFiles.update(getCorefs('E:\\PycharmProjects\\PZKL\\devset'))
    for book in corefsFiles:
        for corefNum in corefsFiles[book]:
            if "corf" in corefsFiles[book][corefNum]:
                if not book in corefs:
                    corefs[book] = {}
                if not corefNum in corefs[book]:
                    corefs[book][corefNum] = {}
                corefs[book][corefNum] = corefsFiles[book][corefNum]
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
    outputSents = set()
    for book in booksTexts:
        output = open("E:\\PycharmProjects\\PZKL\\devsetNorm\\"+book+".txt","w",encoding="utf-8-sig")
        tokens = tokenizer.tokenize(booksTexts[book])
        normTokens = []
        for token in tokens:
            if not token in PUNCTUATION:
                if wordPatternEng.match(token):
                    word = token.upper()
                    lemma = EngLemmatizer.GetLemma(word).upper() 	# Нормализуем слово
                    if (lemma != ""):
                        normTokens.append(lemma)
                    else:
                        normTokens.append(word)
                elif wordPatternRus.match(token):
                    word = token.upper()
                    lemma = list(RuLemmatizer.normal_forms(word))[0].upper()#.encode("utf-8") 	# Нормализуем слово
                    if (lemma != ""):
                        normTokens.append(lemma)
                    else:
                        normTokens.append(word)
                else:
                    normTokens.append(token.upper())
        k = 0
        newNormTokens = list(normTokens)
        for corefNum in corefs[book]:
            if "corf" in corefs[book][corefNum]:
                corefs[book][corefNum]["corf"].sort(key=sortByNumWords, reverse=True)
                for cor in corefs[book][corefNum]["corf"]:
                        cor = cor.strip()
                        if not cor in ['',' ','\n']:
                            tokens = tokenizer.tokenize(cor)
                            normTokensCor = []
                            for token in tokens:
                                if not token in PUNCTUATION:
                                    if wordPatternEng.match(token):
                                        word = token.upper()
                                        lemma = EngLemmatizer.GetLemma(word).upper() 	# Нормализуем слово
                                        if (lemma != ""):
                                            normTokensCor.append(lemma)
                                        else:
                                            normTokensCor.append(word)
                                    elif wordPatternRus.match(token):
                                        word = token.upper()
                                        lemma = list(RuLemmatizer.normal_forms(word))[0].upper()#.encode("utf-8") 	# Нормализуем слово
                                        if (lemma != ""):
                                            normTokensCor.append(lemma)
                                        else:
                                            normTokensCor.append(word)
                                    else:
                                        normTokensCor.append(token)
                                else:
                                    normTokensCor.append(token)
                            if len(normTokensCor) == 1:
                                newNormTokens = [x if x != normTokensCor[0] else str(corefNum) + "FactEntity" for x in newNormTokens]
                            else:
                                normText = ' '.join(newNormTokens)
                                normCor = ' '.join(normTokensCor)
                                normText = normText.replace(normCor, str(corefNum) + "FactEntity")
                                newNormTokens = tokenizer.tokenize(normText)
                k += 1
        newTokens = newNormTokens
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
        # outputSents.add(' '.join(newTokensClear).replace("\n",'')+" | "+' '.join(newTokensPOS).replace("\n",'')+"\n")
        output.write(' '.join(newTokensClear).replace("\n",'')+" | "+' '.join(newTokensPOS).replace("\n",'')+"\n")
        output.close()


if __name__ == "__main__":
    main()