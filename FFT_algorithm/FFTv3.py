#!/usr/bin/env python
# coding: utf-8

# In[2]:



import scipy
import librosa
import math
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import ntpath
import logging
import warnings
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def fft(file):
  file_name = path_leaf(file)
  file_name = file_name.replace(" ", "")
  warnings.filterwarnings("ignore")
  try:
    samples, sampling_rate = librosa.load(file, sr=None, mono= True, offset = 0,duration = None)
  except:
    print("Loading \"" + file_name+ "\" failed")

  logging.basicConfig(filename ="log.txt", level=logging.DEBUG, format='%(asctime)s %(message)s')
  logging.info("Begining with "+ file_name +" \n")
  num_windows = samples.shape[0] // (sampling_rate//2)  # 50ms
  try:
    windowed_audio = np.array_split(samples, num_windows)
  except ValueError:
    logging.info("Audio must be atealst 0.5 seconds long \n")
    return print("Clip must be atleast 0.5 seconds long")
  
  labels = np.zeros(len(windowed_audio))
  nomosqclip = []
  mosqclip = []
  for i, window in enumerate(windowed_audio):
    n = len(window)
    T = 1/sampling_rate
    yf = scipy.fft.fft(window)
    freq= scipy.fftpack.fftfreq(window.size,1/sampling_rate)


    #Frequenzbereich definieren, hier 200Hz - 4000Hz - FREQ
    index = []
    for x in range(len(freq)):
      if(freq[x] < 400 or freq[x] > 4000):
          index.append(x)
    freqcut = np.delete(freq,index)
    yfcut = np.delete(yf,index)
  #Größtes Maximum vom Magnitude finden - MAX
    maxy=0
    for x in yfcut:
      if maxy < (2.0/n * np.abs(x)):
          maxy = 2.0/n * np.abs(x)     
    if maxy == 0:
        continue 

  #Umrechnung von Magnitude in Decibel - DEC
    ydec =[]
    try:    
        for x in range(len(yfcut)):
                ydec.append((math.log10((2.0/n * np.abs(yfcut[x]))/maxy)))

                
         
    except ValueError:
        return print("Kein Sound in diesem Window gefunden")


    
    # Mittelwert zwischen Frequenzen bilden
    wert = [0,0,0,0,0]
    counter = [0,0,0,0,0]
    for x in range(len(ydec)):     
       if freqcut[x] > 400 and freqcut[x] <= 900:
         counter[0] += 1
         wert[0] += ydec[x]
       if freqcut[x] > 900 and freqcut[x] <= 1100:
         counter[1] += 1
         wert[1] += ydec[x]
       if freqcut[x] > 1100 and freqcut[x] <= 1600:
         counter[2] += 1
         wert[2] += ydec[x]
       if freqcut[x] > 1600 and freqcut[x] <= 2200:
         counter[3] += 1
         wert[3] += ydec[x]
       if freqcut[x] > 2200 and freqcut[x] <= 4000:
         counter[4] += 1
         wert[4] += ydec[x]

    mittelwert = [0,0,0,0,0]
    for x in range(len(mittelwert)):
      mittelwert[x] = wert[x] /counter[x]
    
    #Peaks finden
    peaks= [0,0,0,0,0]
    peakst =[False,False,False,False, False]
    for x in range(len(ydec)):       
        if freqcut[x] > 400 and freqcut[x] <= 900 and  (peakst[0] == False or ydec[x] > ydec[peaks[0]]):
          peaks[0] = x
          peakst[0] = True
        if freqcut[x] > 900 and freqcut[x] <= 1100 and (peakst[1] == False or ydec[x] > ydec[peaks[1]]):
          peaks[1] = x
          peakst[1] = True
        if freqcut[x] > 1100 and freqcut[x] <= 1600 and  (peakst[2] == False or ydec[x] > ydec[peaks[2]]):
          peaks[2] = x
          peakst[2] = True
        if freqcut[x] > 1600 and freqcut[x] <= 2200 and  (peakst[3] == False or ydec[x] > ydec[peaks[3]]):
          peaks[3] = x
          peakst[3] = True
        if freqcut[x] > 2200 and freqcut[x] <= 4000 and  (peakst[4] == False or ydec[x] > ydec[peaks[4]]):
          peaks[4] = x
          peakst[4] = True

    #Peaks löschen, die den Threshhold nicht übertreten( Mittelwert - Peak  > 0.8)
    todelete = []
    for x in range(len(peaks)):
      if mittelwert[x] - ydec[peaks[x]] > -0.8:         
        todelete.append(x)
    sortedtodelete = sorted(todelete,reverse = True)
    for x in sortedtodelete:
      del peaks[x]


    
        
    #Find multiples
    for x in peaks:

      truecount = 0
      mosquito =[]
      for y in peaks:
              #Ist y ein UNGEFÄHRES vielfaches von x?
          
          if  freqcut[x] <= 1000 and freqcut[x] != freqcut[y] and (freqcut[y] % freqcut[x] <= 30 or freqcut[x] - (freqcut[y] % freqcut[x]) <= 30 ):
             # if(i == -1):
              
              truecount +=1
              mosquito.append(round(freqcut[y],1))
              
        
      #Gab es zwei vielfache?        
      if truecount >= 2:
          
       
          labels[i] = 1
          mosquito.insert(0,round(freqcut[x]))

            
            
  ii = np.where(labels == 0)[0]
  iii = np.where(labels == 1)[0]
  #Audio Clips mit und ohne Mosquitos erstellen
  for x in range(len(labels)):
    if labels[x] == 1:
      mosqclip.append(windowed_audio[x])
    else:
      nomosqclip.append(windowed_audio[x])
  if nomosqclip:
   list1 = np.concatenate(nomosqclip)
  if mosqclip:
    list2 = np.concatenate(mosqclip)
  if nomosqclip:
    if os.path.isdir("./no_mosquito") == False:
        os.mkdir("./no_mosquito")
    logging.info("Audio Data written in no_mosquito/ \n")
    sf.write('no_mosquito/nomosquito_'+str(file_name[:-4])+'.wav', list1, sampling_rate)


  if mosqclip:
    if os.path.isdir("./mosquito") == False:
        os.mkdir("./mosquito")
    logging.info("Audio Data written in mosquito/ \n")
    sf.write('mosquito/mosquito_'+str(file_name[:-4])+'.wav', list2, sampling_rate)

  mosquitodata = open("ErgebnisseMosquito.txt","a")
  mosquitodata.write(file_name + "\n")
  mosquitodata.write("no mosquito: " + str(round((len(ii)/(len(ii)+len(iii)))*100,1))+"% "+str(len(ii))+"\n")
  mosquitodata.write("mosquito: " + str(round((len(iii)/(len(ii)+len(iii)))*100,1))+"% "+ str(len(iii))+"\n\n")
  mosquitodata.close()
  print("no mosquito: " + str(round((len(ii)/(len(ii)+len(iii)))*100,1))+"%", str(len(ii)))
  print("mosquito: " + str(round((len(iii)/(len(ii)+len(iii)))*100,1))+"%", str(len(iii)))
  logging.info("Finished with "+ file_name+" \n")
  return labels
  

 


# In[3]:


import os
import sys


AUDIO_PATH = sys.argv[1]
if os.path.isdir(AUDIO_PATH):

    for subdir, dirs, files in os.walk(AUDIO_PATH):
        for file in files:
           if file[-3:] == "wav" or file[-3:] == "m4a" or file[-3:] == "mp3":             
                  print("----------------------------")
                  print("Beginning with " +file+ "\n")
                 # fft(root+"/"+file) 
                  fft(os.path.join(subdir,file))
                  print("----------------------------")
else :
    if AUDIO_PATH[-3:] == "wav" or AUDIO_PATH[-3:] == "m4a" or AUDIO_PATH[-3:] == "mp3": 
        print("----------------------------")
        print("Beginning with " +AUDIO_PATH+ "\n")
        fft(AUDIO_PATH)
        print("----------------------------")
    else :
        print("----------------------------")
        print("Error \"" + AUDIO_PATH+"\" not found \n")
        print("----------------------------")


# In[ ]:




