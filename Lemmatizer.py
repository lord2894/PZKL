# -*- coding: utf-8 -*- 


from WordNetAdjective import WordNetAdjective
from WordNetAdverb import WordNetAdverb
from WordNetVerb import WordNetVerb

from WordNetNoun import WordNetNoun


class Lemmatizer:
    def __init__(self, pathToWordNetDict):

        # Разделитель составных слов
        self.splitter = "-"

        # Инициализируем объекты с частям речи
        adj = WordNetAdjective(pathToWordNetDict)  # Прилагательные
        noun = WordNetNoun(pathToWordNetDict)  # Существительные
        adverb = WordNetAdverb(pathToWordNetDict)  # Наречия
        verb = WordNetVerb(pathToWordNetDict)  # Глаголы

        self.wordNet = [verb, noun, adj, adverb]


    # Метод возвращает лемму слова (возможно, составного)
    def GetLemma(self, word):
        # Если в слове есть тире, разделим слово на части, нормализуем каждую часть(каждое слово) по отдельности, а потом соединим
        wordArr = word.split(self.splitter)
        resultWord = []
        for word in wordArr:
            lemma = self.__GetLemmaWord(word)
            if (lemma != None):
                resultWord.append(lemma)
        if (resultWord != None):
            return self.splitter.join(resultWord)
        return None


    # Метод возвращает лемму(нормализованную форму слова)
    def __GetLemmaWord(self, word):
        for item in self.wordNet:
            lemma = item.GetLemma(word)
            if (lemma != None):
                return lemma
        return None