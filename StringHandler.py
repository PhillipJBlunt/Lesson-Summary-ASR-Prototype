# -*- coding: utf-8 -*-
import string
def ToString(string_array, line_breaks = None):
    result = ""
    current_break = -1
    start = -1
    end = -1
    done = False
    check = False
        
    if(line_breaks == None):
        for x in range(0,len(string_array)):
            result += string_array[x]
            if(x < len(string_array)-1):
                result+=" "
    else:
        if(len(string_array) != sum(line_breaks)):
            print("Could not align line breaks with transcript content, using default method")
            for x in range(0,len(string_array)):
                result += string_array[x]
                if(x < len(string_array)-1):
                    result+=" "
        else:
            start = 0
            current_break = 0
            end = line_breaks[current_break]-1
            while not done:
                if check:
                    done = True
                for x in range(start,end+1):
                    result += string_array[x]
                    if(x < end):
                        result+=" "
                    else:
                        result+="...\n\n\t\t"
                start += line_breaks[current_break]
                if(current_break < len(line_breaks)-1):
                    current_break += 1
                    end += line_breaks[current_break]
                if(current_break == len(line_breaks)-2):
                    check = True
    return result
    
def ToStringArray(strng):
    return strng.split(" ")
            
def RemovePunctuation(sentence):
    for i in range(0,len(sentence)):
        temp = ""
        for j in range(0,len(sentence[i])):
            if sentence[i][j] in string.punctuation:
                temp+=""
            else:
                temp+=sentence[i][j]
            sentence[i] = temp
    return sentence

def AlignTranscript(temp_s, current_s, comparison_limit, overlap_comparison_length):
    #method termination boolean
    matched = False
        
    #overlap interval for the temp and current strings
    temp_clip = 0
    current_clip = 0
    length = 0
    limit = 0
    
    #handle any and all potential parameterization issues
    err = False
    if(len(temp_s) == overlap_comparison_length and len(temp_s) > comparison_limit and len(current_s) == overlap_comparison_length and len(current_s) > comparison_limit):
        #all is well
        length = overlap_comparison_length
        limit = comparison_limit
    elif(len(temp_s) <= overlap_comparison_length and len(temp_s) >= comparison_limit) and (len(current_s) <= overlap_comparison_length and len(current_s) >= comparison_limit):
        #some sequence is too short for default comparison length
        if (len(temp_s) < len(current_s)):
            length = len(temp_s)
            limit = comparison_limit
        elif(len(current_s) < len(temp_s)):
            length = len(current_s)
            limit = comparison_limit
        elif(len(temp_s) == len(current_s)):
            length = len(temp_s)
            limit = comparison_limit
    elif(len(temp_s) < comparison_limit or len(current_s) < comparison_limit):
        #some sequence is too short for default comparison limits
        err = True
    
    if err == False:
        #convert temp and current strings to lower case for string comparison, retaining original case of current_s
        lower_temp_s = []
        for s in temp_s:
            lower_temp_s.append(s.lower())
        lower_current_s = []
        for s in current_s:
            lower_current_s.append(s.lower())
        
        #determine the overlap between the lower case temp and current strings
        for i in range((len(lower_temp_s) - length) + length,limit,-1):
            if(matched):
                break
            temp = lower_temp_s[i-comparison_limit:i]
            for j in range(0,(len(lower_current_s) - length) + length-limit,1):
                if(matched):
                    break
                current = lower_current_s[j:j+(comparison_limit)]
                #print("Comparing: " + str(i) + ":" + str(temp) + " with " + str(j) + ":" + str(current))
                if SequenceMatch(temp, current):
                    temp_clip = len(lower_temp_s) - i
                    current_clip = j+comparison_limit
                    matched = True                    
        if not matched:
            print("(!) Caution: Could not align transcript segments, however, a full alignment attempt was made, adding what was most recently recognized to the transcript, 'as is'...")
            print("(?) Help: This is likely caused by poor LVCSR system performance with inaccurate or highly inconsistent recognition.")
            temp_clip = 0
            current_clip = 0
        elif matched:
            print("(%) Transcript segments successfully aligned. The transcipt is being updated...")
    else:
        print("(!) Error: Could not attempt to align transcript segments due to parameterization issues in overlap comparison length and limit, adding what was most recently recognized to the transcript, 'as is'...")
        print("(?) Help: This can occur for two reasons: (1) The LVCSR system's recognition performance is inaccurate or highly inconsistent - and/or - (2) The overlap comparison length and comparison limit arguments do not align with the current length of the analysis window.")
    
    #return the results from the overlap analysis; whether there was a match, the number of words to remove from the transcript, and the new segment of text to add to the transcript
    return matched, temp_clip, current_s[current_clip:]
        
def SequenceMatch(a, b):
        check = False
        if len(a) == len(b):
            count = 0
            for i in range(0,len(a)):
                if(a[i]==b[i]):
                    count+=1
                if count==0:
                    break
            if(count == len(a)):
                check = True
        return check