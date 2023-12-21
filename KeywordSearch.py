# -*- coding: utf-8 -*-
from KeywordInstance import KeywordInstance
import ahocorasick

class KeywordSearch(object):
    def __init__(self):
        self.keyword_instances = []
        self.aho = None
        
    def StartSession(self, keywords_list):
        self.keyword_instances = []
        self.aho = ahocorasick.Automaton()
        self.AddAhoKeywords(keywords_list)
        self.aho.make_automaton()
    
    def KeyIndex(self,Keyword):
        Keys = self.GetIdentifiedKeywords()
        if Keyword in Keys:
            return Keys.index(Keyword)
        else:
            return -1
        
    def GetIdentifiedKeywords(self):
        keywords = []
        for kw in self.keyword_instances:
            keywords.append(kw.Keyword())
        return keywords
    
    def GetIdentifiedKeywordValues(self):
        keyword_values = []
        if self.keyword_instances != []:
            for kw in self.keyword_instances:
                if kw.InstanceCount() != 0:
                    keyword_values.append([kw.Keyword(),kw.SequenceNumber(),kw.InstanceCount()])
            return keyword_values
        else:
            return None
        
    def GetKeywordStrings(self):
        keyword_strings = []
        if self.keyword_instances != []:
            for kw in self.keyword_instances:
                    keyword_strings.append("'" + kw.Keyword() + "' first mentioned in position: " + str(kw.SequenceNumber()) + "; " + str(kw.InstanceCount()) + " times.")
            return keyword_strings
        else:
            return None
        
    def IncrementInstances(self, Keyword):
        idx = self.KeyIndex(Keyword)
        if (idx != -1) and (self.Exists(Keyword) == True):
            self.keyword_instances[idx].IncrementInstances()
    
    def Exists(self, Keyword):
        if Keyword in self.aho:
            return True
        else:
            return False
        
    def AddIdentifiedKeyword(self, Keyword):
        self.keyword_instances.append(KeywordInstance(Keyword,len(self.GetIdentifiedKeywords())+1))
        
    def AddAhoKeywords(self, Keywords):
        for idx, key in enumerate(Keywords):
            self.aho.add_word(key, (idx, key))

    def SearchString(self, search_string):
        search_string_lower = search_string.lower()
        keyword_search = []
        for end_index, (insert_order, original_value) in self.aho.iter(search_string_lower):
            try:
                keyword_search.append([end_index, original_value])
                start_index = end_index - len(original_value)
                assert search_string_lower[start_index:end_index] == original_value, "Search indices went out of bounds"
            except AssertionError:
                pass
        
        for result in keyword_search:
            charindex, word = result
            idx = self.KeyIndex(word)
            if(idx !=-1):
                self.keyword_instances[idx].IncrementInstances()
            else:
                self.AddIdentifiedKeyword(word)
            