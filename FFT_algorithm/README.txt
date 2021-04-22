USAGE: 

Either one single audio is given and can be analyzed or a folder can be iterated through. The script then creates two folders: no_mosquito and mosquito. Audio Bits containing Mosquito will be connected and saved in the correct 
Folder.

EXAMPLES:

Python3 FFTv3.py audio.mp3

This will analyze one single audio.

Python3 FFTv3.py audio/

This will analyze every audio contained in the audio/ folder. It also iterates through all folders in audio/.

This script works with Mp3, WAV and m4a. Other data types might also work, but it is tested with those three.

The Audio File to be analyzed has to be larger than 0.5 seconds

WHAT THE SCRIPT DOES:

1. First the audio File is loaded

2. The Audio is then divided in 0.5 second long windows.

3. A Fast Fourier Transformation is then performed on each window.

4.  Frequencies below 400 and above 4000 are then removed.

5. The Magnitude is then converted to Decibel.

6. 5 Peaks of Decibel are then determined. This first peak has to be between 400 and 900 Hz. The second has to be between 900 and 1100 Hz. The third between 1100 and 1600 Hz. The fourth between 1600 and 2200 Hz and 
the fifth between 2200 and 4000 Hz. Those Frequency ranges are used since those seemed to make most sense while determining Mosquitos.

7. Each Peak has to be 0,8 Db louder than the average Db in its frequency range. This helps differentiate between Noise and Mosquito. 

8. The Peaks are then compared and multiples of each other are determined. For example: 500 Hz, 1000 Hz and 1500 Hz. The script then determines the analyzed window as containing Mosquitos. 

9. The Windows containing Mosquitos are then grouped together and those not containing Mosquitos are also grouped together.

10. Audio Files are then written.