import argparse
import logging
import os
from time import perf_counter
import math

import librosa, librosa.display
import scipy
import numpy as np
import matplotlib.pyplot as plt
from soundfile import write as wav_write


def plot_correlation(correlation, no):
    plt.plot(correlation)
    plt.title(f"{no}")
    plt.savefig(f"{no}.png")
    plt.close()


def is_periodic(correlation, distance, sr):
    """
    Determines whether a given correlation is (almost) periodic
    :param correlation: correlation values for each sample lag; np.array of floats
    :param distance: Min distance between correlation peaks; int
    :return: Estimate wether periodic or not and first distance (or 0); Bool and int
    """
    # Get peaks
    peaks, _ = scipy.signal.find_peaks(correlation, distance=distance)  # Distance should exclude tiny peaks and maximum

    # If correlation just represents noise, there often are no peaks that meet the minimum height
    # This statement prevents the function from crashing in such a case
    if peaks.size < 2:
        return False, 0

    # Compute distance between each peak and its successor
    # Excludes last peak, because that tends to be off
    distances = np.diff(peaks[:-1])

    # Determine whether distances are roughly periodic
    tolerance = math.ceil(sr//1000//10)
    if tolerance > 1:
        pass
    else:
        tolerance = 2
    close = np.isclose(distances[0], distances, atol=tolerance)  # Similarity of ca. 5-6% of samples between peaks
    if np.bincount(close)[0] < close.shape[0] // 10:  # At least 90% periodic
        return True, distances[0]

    return False, 0


def detection(filename, fmin, fmax, verify=False):
    """
    Detects whether a mosquito is present in 100ms snippets of a given audio file
    :param filename: Name of audio file; String
    :param fmin: Minimum frequency to look for; int
    :param fmax: Maximum frequency to look for; int
    :param verify: Whether or not to make plots for human verification of the result; Bool
    :return: Mosquito audio snippets AND binary Labels for all 100ms snippets of the audio AND sampling rate; 
             np.array of floats AND np.array of ints AND int
    """
    audio_parts = []
    # Load and apply bandpass filter
    audio, sr = librosa.load(filename, sr=None)
    b, a = scipy.signal.butter(N=2, Wn=[300, 2048], btype='bandpass', fs=sr)
    audio = scipy.signal.lfilter(b, a, audio)

    # Calculate windows for signal
    ms100_window = sr // 10  # 100ms
    num_windows = audio.size // ms100_window
    start = 0

    # Store labels for mosquito presence in hot-one-encoding
    labels = np.zeros(shape=num_windows, dtype=int)
    for i, window in enumerate(range(num_windows)):
        # Autocorrelation
        window = audio[start:start+ms100_window]
        r = librosa.autocorrelate(window)

        periodic, first_distance = is_periodic(r, sr//1000, sr)
        if periodic:
            # Pitch Detection
            T = (first_distance / sr)  # Calculate period in seconds
            f0 = round(1 / T, 2)  # Physics, f = 1/T in Hz

            if fmin <= f0 <= fmax:  # Roughly mosquito frequency range (across species)
                labels[i] = 1
                audio_parts.append(window)

        if verify:
            peaks, _ = scipy.signal.find_peaks(r, distance=sr//1000)
            plt.plot(r)
            plt.plot(peaks[:-1], r[peaks[:-1]], marker="x")
            plt.savefig(f"{i}.png")
            plt.close()

        start += ms100_window

    return audio_parts, labels, sr


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description="Detect presence of mosquitos in given audio files")
    parser.add_argument("fmin", help="Min fundamental frequency to look for")
    parser.add_argument("fmax", help="Max fundamental frequency to look for")
    parser.add_argument("--filenames", nargs='+', help="Names of wav files", required=True)
    args = parser.parse_args()

    AUDIO_PATH = "data/audio"

    # Setup directories
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    if not os.path.isdir("data/labels"):
        os.mkdir("data/labels")

    # Configure logger
    logging.basicConfig(filename='logs/mosquito_detection.log',
                        format='[%(asctime)s][%(levelname)s]: %(message)s',
                        datefmt='%d.%m.%y %H:%M:%S',
                        level=logging.INFO)

    for name in args.filenames:
        logging.info(f'Processing {name[:-4]}')
        start_time = perf_counter()
        audio_parts, audio_labels, sampling_rate = detection(os.path.join(AUDIO_PATH, name), int(args.fmin), int(args.fmax))
        stop_time = perf_counter()
        logging.info(f"Finished in: {stop_time - start_time:.3f} seconds")

        try:
            audio_concatenated = np.concatenate(audio_parts[6:])  # Slicing is done to cut out potential false positives on voice
            file_path = os.path.join(AUDIO_PATH, f"{name[:-4]}_autocut.wav")
            wav_write(file_path, audio_concatenated, sampling_rate)
            logging.info(f"Mosquito audio for {name[:-4]} saved to disk")
        except:
            logging.info(f"No mosquito found for {name[:-4]}")

        try:
            np.save(f"data/labels/{name[:-4]}", audio_labels[6:])  # Slicing is done to cut out potential false positives on voice
            logging.info(f"Labels for {name[:-4]} saved to disk")
        except:
            logging.info(f"Less than 0.6 seconds of audio for {name[:-4]}")
