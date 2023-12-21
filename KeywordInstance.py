# -*- coding: utf-8 -*-
class KeywordInstance(object):
    def __init__(self, keyword, sequence_number):
        self.keyword = keyword
        self.sequence_number = sequence_number
        self.instances = 1
    
    def SequenceNumber(self):
        return self.sequence_number
    
    def Keyword(self):
        return self.keyword
    
    def InstanceCount(self):
        return self.instances
    
    def IncrementInstances(self):
        self.instances+=1
        
    def SetSequenceNumber(self, position):
        self.sequence_number = position
    
    def Values(self):
        return [self.Keyword(), self.SequenceNumber(), self.InstanceCount()]