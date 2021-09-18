Usage of autocorrelation_detection.py:
python3 autocorrelation_detection.py fmin fmax --filenames filenames

Where fmin and fmax are integers denoting the minimum and maximum fundamental frequency, which the script should consider to be a mosquito.
filenames should consist of space separated filenames, not including the source directory of the audios, e.g.
audio_1.wav instead of path_to_audio/audio_1.wav

The path to the audios should be set in the script, on line 106 with the variable AUDIO_PATH

The script writes the labels (0 or 1) for each 100ms portion of the audio, as well as the concatenated parts where it detected mosquito, to the disk.
To prevent false positives from voice recordings from contaminating the data, when smaller sampling rates are used,
the first 0.5 seconds of audio are cut off before saving the file.
If you wish to keep those 0.5 seconds, you can change the slicing on lines 133 and 141.
