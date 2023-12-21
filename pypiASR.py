# -*- coding: utf-8 -*-
import speech_recognition as sr
import StringHandler as strng
#quiet the endless 'insecurerequest' warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class pypiASR(object):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def RecognizeFile(self,wavpath, recognizer = "google"):
        sentence = ""
        with sr.AudioFile(wavpath) as source: 
            #reads the audio file. Here we use record instead of listen 
            audio = self.recognizer.record(source)   
            try:
                if(recognizer.lower() == "google"):
                    sentence = strng.ToStringArray(self.recognizer.recognize_google(audio))
                elif(recognizer.lower() == "google cloud"):
                    sentence = strng.ToStringArray(self.recognizer.recognize_google_cloud(audio))
                elif(recognizer.lower() == "sphinx"):
                    sentence = strng.ToStringArray(self.recognizer.recognize_sphinx(audio))
                elif(recognizer.lower() == "ibm"):
                    sentence = strng.ToStringArray(self.recognizer.recognize_ibm(audio))
                elif(recognizer.lower() == "bing"):
                    sentence = strng.ToStringArray(self.recognizer.recognize_bing(audio))
                else:
                    print("The specified recognizer does not exist. Use: Google, Google Cloud, Sphinx, IBM or Bing.")
                
            except sr.UnknownValueError: 
                print("The specified recognizer could not understand the audio.")
                sentence = []
            except sr.RequestError as e: 
                print("Could not request results from the speech recognition service; check you internet connection. ERROR CODE: {0}".format(e))
                sentence = []
            except TimeoutError:
                print("A connection timeout occurred, please ensure you have appropriate bandwidth to upload the audio file.")
                sentence = []
            return sentence        