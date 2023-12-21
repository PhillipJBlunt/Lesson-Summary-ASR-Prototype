# -*- coding: utf-8 -*-
                
class LessonAssociation(object):
    def __init__(self, number, header, keyword):
        self.number = number
        self.header = header
        self.keywords = []
        self.keywords.append(keyword)
        
    def Values(self):
        return self.number + " " + self.header, self.keywords
        
    def AddKeyword(self, keyword):
        return self.keywords.append(keyword)
        
    def GetAssociationString(self):
        keywords = ""
        for k in self.keywords: 
            keywords+=str(k)+", "
        keywords = keywords[0:-2]
        return str(self.number) + " " + self.header
    
    def SectionNumber(self):
        return [int(val) for val in self.number.split(".")]