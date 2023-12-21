# -*- coding: utf-8 -*-
from pydub import AudioSegment
from random import uniform
import numpy as np
import contextlib
from scipy.io import wavfile
import noisereduce as nr
from adaptfilt import nlms as normalized_LMS 
import wave

def GetWaveDuration(wavpath):
    with contextlib.closing(wave.open(wavpath,'r')) as f:
         frames = f.getnframes()
         rate = f.getframerate()
         duration = frames / float(rate)
         return duration

def SegmentFromFile(wavpath, elapsed_start_s, elapsed_end_s, newfilename, noisepath = None, noise_reduce = False, adaptive = False, frame_rate = 16000):
    sound_l = AudioSegment.from_wav(wavpath)
    if(noisepath is not None):
        how_long = elapsed_end_s - elapsed_start_s
        max_len = GetWaveDuration(noisepath) - how_long
        start_interval = uniform(0, max_len)
        print("Using noise file: "+noisepath+" on interval: "+str(round(start_interval,2))+" --> "+str(round(start_interval+how_long,2)))
        sound_l = sound_l[float(elapsed_start_s) * 1000:float(elapsed_end_s) * 1000]
        sound_n = AudioSegment.from_wav(noisepath)
        sound_n = sound_n[float(start_interval) * 1000:float(start_interval+how_long) * 1000]
        sound_n = sound_n - 7
        combined = sound_l.overlay(sound_n)
        sound_l.export(newfilename[:-4]+"_speech.wav", format="wav")
        sound_n.export(newfilename[:-4]+"_noise.wav", format="wav")
        combined.export(newfilename, format="wav")
        
        if noise_reduce and not adaptive:
                # load the noisy speech
                rate_l, noisy_speech_data = wavfile.read(newfilename)
                raw_ns = noisy_speech_data.astype(np.float32)
                # select equivalent noise sample
                rate_n, noise_data = wavfile.read(newfilename[:-4]+"_noise.wav")
                raw_n = noise_data.astype(np.float32)
                if(rate_l == rate_n == frame_rate):
                    # perform noise reduction
                    reduced_noise = nr.reduce_noise(audio_clip=raw_ns, noise_clip=raw_n, verbose=False)
                    raw_r = reduced_noise.astype(np.int16)
                    #save a new temp file
                    wavfile.write(newfilename, frame_rate, raw_r)                                        
                    print("Wrote noise reduced wav.")
                else:
                    print("Frame Rate Mismatch: Cannot Perform Noise Reduction")
                    
        if adaptive and not noise_reduce:
            #error checking for wave file lengths resulting in appropriate trimming
            temp_dur = GetWaveDuration(newfilename)
            noise_dur = GetWaveDuration(newfilename[:-4]+"_noise.wav")
            speech_dur = GetWaveDuration(newfilename[:-4]+"_speech.wav")
            
            if(temp_dur > noise_dur or temp_dur > speech_dur):
                diff = 0.000000
                if noise_dur == speech_dur:
                    diff = temp_dur - noise_dur
                    temp_data = AudioSegment.from_wav(newfilename)
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    
                elif (noise_dur < speech_dur):
                    diff = temp_dur - noise_dur
                    temp_data = AudioSegment.from_wav(newfilename)
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    diff = speech_dur - noise_dur
                    temp_data = AudioSegment.from_wav(newfilename[:-4]+"_speech.wav")
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    
                elif (speech_dur < noise_dur):
                    diff = temp_dur - speech_dur
                    temp_data = AudioSegment.from_wav(newfilename)
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    diff = noise_dur - speech_dur
                    temp_data = AudioSegment.from_wav(newfilename[:-4]+"_noise.wav")
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
            
            # get noisy speech data
            rate_l, noisy_speech_data = wavfile.read(newfilename)
            raw_ns = noisy_speech_data.astype(np.float32)
            # get equivalent noise sample
            rate_n, speech_data = wavfile.read(newfilename[:-4]+"_speech.wav")
            raw_n = speech_data.astype(np.float32)            
            M = 100  # Number of filter taps in adaptive filter
            step = 0.1  # Step size
            
            if(rate_l == rate_n == frame_rate):
                filtered_speech, e, w = normalized_LMS.nlms(raw_ns, raw_n, M, step)
                raw_filtered = filtered_speech.astype(np.int16)
                wavfile.write(newfilename, frame_rate, raw_filtered)                    
                print("Wrote noise cancelled wav.")
            else:
                print("Frame Rate Mismatch: Cannot Perform Noise Cancellation")
                
        if noise_reduce and adaptive:
            # load the noisy speech
            rate_l, noisy_speech_data = wavfile.read(newfilename)
            raw_ns = noisy_speech_data.astype(np.float32)
            # select equivalent noise sample
            rate_n, noise_data = wavfile.read(newfilename[:-4]+"_noise.wav")
            raw_n = noise_data.astype(np.float32)
            if(rate_l == rate_n == frame_rate):
                # perform noise reduction
                reduced_noise = nr.reduce_noise(audio_clip=raw_ns, noise_clip=raw_n, verbose=False)
                raw_r = reduced_noise.astype(np.int16)
                #save a new temp file
                wavfile.write(newfilename, frame_rate, raw_r)
                print("Wrote noise reduced wav.")
            else:
                print("Frame Rate Mismatch: Cannot Perform Noise Reduction")
            
            #error checking for wave file lengths resulting in appropriate trimming
            temp_dur = GetWaveDuration(newfilename)
            noise_dur = GetWaveDuration(newfilename[:-4]+"_noise.wav")
            speech_dur = GetWaveDuration(newfilename[:-4]+"_speech.wav")
            
            if(temp_dur > noise_dur or temp_dur > speech_dur):
                print("Trimming temporary files to normalize durations.")
                diff = 0.000000
                if noise_dur == speech_dur:
                    diff = temp_dur - noise_dur
                    temp_data = AudioSegment.from_wav(newfilename)
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    
                elif (noise_dur < speech_dur):
                    diff = temp_dur - noise_dur
                    temp_data = AudioSegment.from_wav(newfilename)
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    diff = speech_dur - noise_dur
                    temp_data = AudioSegment.from_wav(newfilename[:-4]+"_speech.wav")
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    
                elif (speech_dur < noise_dur):
                    diff = temp_dur - speech_dur
                    temp_data = AudioSegment.from_wav(newfilename)
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
                    diff = noise_dur - speech_dur
                    temp_data = AudioSegment.from_wav(newfilename[:-4]+"_noise.wav")
                    temp_data = temp_data[:-diff*1000]
                    temp_data.export(newfilename, format = "wav")
            
            #reload the noisy speech data
            rate_l, noisy_speech_data = wavfile.read(newfilename)
            raw_ns = noisy_speech_data.astype(np.float32)
            # get equivalent noise sample
            rate_n, speech_data = wavfile.read(newfilename[:-4]+"_speech.wav")
            raw_n = speech_data.astype(np.float32)            
            M = 100  # Number of filter taps in adaptive filter
            step = 0.1  # Step size
            
            if(rate_l == rate_n == frame_rate):
                filtered_speech, e, w = normalized_LMS.nlms(raw_ns, raw_n, M, step)
                raw_filtered = filtered_speech.astype(np.int16)
                wavfile.write(newfilename, frame_rate, raw_filtered)
                
                print("Wrote noise cancelled wav.")
            else:
                print("Frame Rate Mismatch: Cannot Perform Noise Reduction")
        
    else:
        sound_l = sound_l[float(elapsed_start_s) * 1000:float(elapsed_end_s) * 1000]
        sound_l.export(newfilename, format="wav")
        
print(GetWaveDuration("E:\\Python\\ASR_Prototype\\temp\\temp.wav"))
print(GetWaveDuration("E:\\Python\\ASR_Prototype\\temp\\temp_speech.wav"))
print(GetWaveDuration("E:\\Python\\ASR_Prototype\\temp\\temp_noise.wav"))