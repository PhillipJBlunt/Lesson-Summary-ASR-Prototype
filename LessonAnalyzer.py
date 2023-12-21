# -*- coding: utf-8 -*-
from KeywordSearch import KeywordSearch
from pypiASR import pypiASR
import WavHandler as wav
import StringHandler as strng
from DB_Connection import DBConn
from LessonAssociation import LessonAssociation

import PdfHandler

#scripts to arbitrarily analyze a wave file, generate a transcript, spot keywords and associated timestamps while keeping a running total of identified keywords

class LessonAnalyzer(object):
    def __init__(self):
        self.test_script = None #set by access methods
        self.wavpath = None #set by access methods
        self.dbconn = DBConn()
        self.kws = KeywordSearch() #initialize the keyword search object
        self.asr = pypiASR() #initialize pypiASR library wrapper
        
    def PostLectureAnalysis(self, wave_path, lesson_details, output_path = "result\\Lesson_Summary.pdf", noisepath = None, noisereduce = False, adaptive = False, overlap_comparison_length = 25, comparison_limit = 4, overlap_s = 15.000, length_s = 90.000,  frame_rate = 16000, recognizer = "google"):
        #setup object variables
        self.wavpath = wave_path
        s_max = wav.GetWaveDuration(self.wavpath) #the length in seconds of the lecture wav file
        start = 0.000 #time in seconds for the start of the interval
        end = length_s #time in seconds for the end of the interval
        if(end >= s_max): #check there isnt a wave duration issue with the overlap and length of current analysis window
            end = s_max
        tname = "temp\\temp.wav" #the name of the temp file for each interval analysis
        transcript = [] #list of strings for each word in the transcript (to be separated by spaces)
        current_s = [] #the current list of strings for analysis
        current_s_long = "" #the result of converting current_s to a long string
        temp_s = [] #the last list of strings from analysis
        done = False #the loop ending boolean
        check = False #the final iteration boolean
        word_intervals = [] #list of integers used to break up the transcript appropriately
        
        #initialize the keyword search object - Ahocorasick search algorithm, with the specified keywords to identify
        self.kws.StartSession(self.dbconn.GetKeywordsList())
        
        print("")
        while not done:
            #analysis in the current time interval
            print("Lesson audio analysis on: " + self.wavpath + " from: " +str(round(start,2)) + " --> "+str(round(end,2)))
            
            #segment the lecture audio based on the current time interval of analysis
            wav.SegmentFromFile(self.wavpath, start, end, tname, noisepath, noisereduce, adaptive, frame_rate)
            
            #check if its the last iteration of the loop
            if check:
                done = True
                
            #determine what was said in the given window using the given recognizer
            print("Uploading...")
            current_s = self.asr.RecognizeFile(tname, recognizer)
            
            #if the transcript is empty
            if(len(transcript) == 0):
                #add each recognized word to the transcript
                for word in current_s:
                    transcript.append(word)
                    
                #append the number (the count) of transcribed words to the intervals list to be broken up for presentation purposes
                word_intervals.append(len(current_s))
                
                #convert back to a long string for keyword analysis
                current_s_long = strng.ToString(current_s)
                
                #get the keyword search results
                self.kws.SearchString(current_s_long)
            else:
                #determine what needs to be appended based on what is in the transcript and what was recently analyzed by ASR
                print("Matching...")
                match, iclip, current_s = strng.AlignTranscript(temp_s, current_s, comparison_limit,  overlap_comparison_length)
                
                #remove overlapping keywords from the transcript and update the last word interval
                transcript = transcript[:len(transcript) - iclip]
                word_intervals[len(word_intervals)-1] -= iclip 
                
                #add new words to the transcript
                for word in current_s:
                    transcript.append(word)
                    
                #append the length of the current number of new transcribed words, to break up the transcript later for presentation purposes
                word_intervals.append(len(current_s))
                    
                #convert back to a long string for keyword analysis
                current_s_long = strng.ToString(current_s)
                
                #perform keyword analysis and add to instance count while accounting for the loop iteration and the two extra added words
                self.kws.SearchString(current_s_long)
 
            #setup next loop iteration with the last overlap_comparison_length words
            temp_s = transcript[len(transcript)-overlap_comparison_length:]
            
            start = end - overlap_s
            end = start + length_s
            if(end > s_max):
                end = s_max
                check = True
            print("")
        
        #Get Pie Chart Info
        keyword_details = self.kws.GetIdentifiedKeywordValues()
        keywords = []
        mentions = []
        other = "*Other Keyword Terms: "
        other_mentions = 0
        if keyword_details is not None:
            for detail in keyword_details:
                if detail is not None:
                    keyword, sequence, utterances = detail
                    if utterances >= 4:
                        keywords.append("("+str(sequence)+") " + keyword)
                        mentions.append(utterances)
                    else:
                        other+="("+str(sequence)+") "+keyword+", "
                        other_mentions += utterances
                    
        if other != "*Other Keyword Terms: ":
            other = other[0:-2]
            keywords.append("Other")
            mentions.append(other_mentions)
        
        #determine the associations between identified keywords and course content
        associations = self.GetLessonAssociations(self.kws.GetIdentifiedKeywords())
        associations.sort(key=lambda asso:asso.SectionNumber())
        
        #convert these associations to strings to be written to the pdf lesson summary
        textual_associations = []
        for asso in associations:
            textual_associations.append(asso.GetAssociationString())
        
        #write the lesson summary to a pdf document
        PdfHandler.CreatePDF(output_path, lesson_details, keywords, mentions, other, textual_associations, strng.ToString(transcript, word_intervals))
        
        print(other)
        
        #return the values for evaluation
        return associations
    
    def TranscribeAudio(self, wave_path, overlap_comparison_length = 25, comparison_limit = 4, overlap_s = 15.000, length_s = 90.000,  frame_rate = 16000, recognizer = "google"):
        self.wavpath = wave_path
        s_max = wav.GetWaveDuration(self.wavpath) #the length in seconds of the lecture wav file
        start = 0.000 #time in seconds for the start of the interval
        end = length_s #time in seconds for the end of the interval
        tname = "temp\\temp.wav" #the name of the temp file for each interval analysis
        transcript = [] #list of strings for each word in the transcript (to be separated by spaces)
        current_s = [] #the current list of strings for analysis
        temp_s = [] #the last list of strings from analysis
        done = False #the loop ending boolean
        check = False #the final iteration boolean
        word_intervals = [] #list of integers used to break up the transcript appropriately

        while not done:
            #analysis in the current time interval
            print("Lesson audio analysis on: " + self.wavpath + " from: " +str(round(start,2)) + " --> "+str(round(end,2)))
            
            #segment the lecture audio based on the current time interval of analysis
            wav.SegmentFromFile(self.wavpath, start, end, tname)
            
            #check if its the last iteration of the loop
            if check:
                done = True
                
            #determine what was said in the given window using the given speech recognizer
            current_s = self.asr.RecognizeFile(tname, recognizer)
            
            #if the transcript is empty
            if(len(transcript) == 0):
                #add each recognized word to the transcript
                for word in current_s:
                    transcript.append(word)
                    
                #append the number (the count) of transcribed words to the intervals list to be broken up for presentation purposes
                word_intervals.append(len(current_s))
                
            else:
                #determine what needs to be appended based on what is in the transcript and what was recently analyzed by ASR
                match, iclip, current_s = strng.AlignTranscript(temp_s, current_s, comparison_limit,  overlap_comparison_length)
                
                #remove overlapping keywords from the transcript and update the last word interval
                transcript = transcript[:len(transcript) - iclip]
                word_intervals[len(word_intervals)-1] -= iclip 
                
                #add new words to the transcript
                for word in current_s:
                    transcript.append(word)
                    
                #append the length of the current number of new transcribed words, to break up the transcript later for presentation purposes
                word_intervals.append(len(current_s))
 
            #setup next loop iteration with the last overlap_comparison_length words
            temp_s = transcript[len(transcript)-overlap_comparison_length:]
            
            start = end - overlap_s
            end = start + length_s
            if(end > s_max):
                end = s_max
                check = True
        
        #return the values for evaluation
        return strng.ToString(transcript, word_intervals)

        
    def TestScriptAnalysis(self, test_script, lesson_details, output_path = "result\\Lesson_Summary.pdf", overlap_comparison_length = 25, comparison_limit = 4, overlap_w = 10, length_w = 150):
        #method used to test analysis algorithm with a known script (a long string)
        
        #split up the transcript on space characters for windowing
        self.test_script = strng.ToStringArray(test_script)
        
        #initialize the keyword search object - Ahocorasick search algorithm, with the specified keywords to identify
        self.kws.StartSession(self.dbconn.GetKeywordsList())
        
        
        s_max = len(self.test_script)-1 #the number of words in the test script
        start = 0 #position in words of the start of the first interval
        end = length_w-1 #position in words of the end of the first interval
        current_s_long = "" #result of converting the current transcribed text into a long string
        transcript = [] #list of strings for each word in the transcript (to be separated by spaces later)
        current_s = [] #the current list of strings from analysis within the interval
        temp_s = [] #the last list of strings from analysis of size overlap_comparison_length
        done = False #the loop ending boolean
        check = False #the final iteration boolean check
        word_intervals = [] #list of integers used to break up the transcript appropriately based on the analysis window
        
        while not done:
            #analysis in the current time interval
            print("Lesson analysis on: Test Script from word position: " +str(start) + " --> "+str(end))
                        
            #check if its the last iteration of the loop
            if check:
                done = True
            
            #setup the current string of transcribed words (would otherwise be obtained by pypiASR)
            if(end >= s_max):
                current_s = self.test_script[start:]
            else:
                current_s = self.test_script[start:end]
            
            #if the transcript is empty
            if(len(transcript) == 0):
                #add each recognized word to the transcript
                for word in current_s:
                    transcript.append(word)
                    
                #append the number (the count) of transcribed words to the intervals list to be broken up for presentation purposes
                word_intervals.append(len(current_s))
                
                #convert back to a long string for keyword analysis
                current_s_long = strng.ToString(current_s)
                
                #search the current string for keywords
                self.kws.SearchString(current_s_long)
                    
            else:                
                #determine what needs to be appended based on what is in the transcript and what was recently analyzed by ASR
                match, iclip, current_s = strng.AlignTranscript(temp_s, current_s, comparison_limit,  overlap_comparison_length)
                
                #remove overlapping keywords from the transcript and update the last word interval
                transcript = transcript[:len(transcript) - iclip]
                word_intervals[len(word_intervals)-1] -= iclip 
                
                #add new words to the transcript
                for word in current_s:
                    transcript.append(word)
                    
                word_intervals.append(len(current_s))
                    
                #convert back to a long string for keyword analysis
                current_s_long = strng.ToString(current_s)
                
                #search the current string for keywords
                self.kws.SearchString(current_s_long)
                    
            #setup next loop iteration with the last 20 words (the limit argument) and update the start and end value window limits with respect to the overlap
            temp_s = transcript[len(transcript)-overlap_comparison_length:]
            start = end - overlap_w
            end = start + length_w
            if(end > s_max):
                end = s_max
                check = True
        
        #Get Pie Chart Info
        keyword_details = self.kws.GetIdentifiedKeywordValues()
        keywords = []
        mentions = []
        other = "*Other Keyword Terms: "
        other_mentions = 0
        
        for detail in keyword_details:
            keyword, sequence, utterances = detail
            if utterances >= 4:
                keywords.append("("+str(sequence)+") " + keyword)
                mentions.append(utterances)
            else:
                other+="("+str(sequence)+") "+keyword+", "
                other_mentions += utterances

        if other != "*Other Keyword Terms: ":
            other = other[0:-2]
            keywords.append("Other")
            mentions.append(other_mentions)
        
        #determine the associations between identified keywords and course content
        associations = self.GetLessonAssociations(self.kws.GetIdentifiedKeywords())
        associations.sort(key=lambda asso:asso.SectionNumber())
        
        #convert these associations to strings to be written to the pdf lesson summary
        textual_associations = []
        for asso in associations:
            textual_associations.append(asso.GetAssociationString())
        
        #write the lesson summary to a pdf document
        PdfHandler.CreatePDF(output_path, lesson_details, keywords, mentions, other, textual_associations, strng.ToString(transcript, word_intervals))
        
        #return the values for evaluation
        return associations
    
    def GetLessonAssociations(self, identified_keywords):
        header_numbers = []
        associations = []
        for keyword in identified_keywords:
            for result in self.dbconn.GetKeywordAssociations(self.dbconn.GetKeywordID(keyword)):
                number, header = result
                if number not in header_numbers:
                    header_numbers.append(number)
                    new_association = LessonAssociation(number, header, keyword)
                    associations.append(new_association)
                else:
                    idx = header_numbers.index(number)
                    associations[idx].AddKeyword(keyword)
                    
        return associations