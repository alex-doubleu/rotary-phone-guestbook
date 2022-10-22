from time import sleep
import sounddevice as sd
import soundfile as sf
import numpy
import logging
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.INFO)

def play_prompt():
    data, sample_rate = sf.read('../audio/test_prompt.wav')
    sd.play(data, sample_rate)
    sd.wait()

def play_tone():
    duration = 0.75
    amplitude = 0.2
    freq = 440.0
    sample_rate = sd.query_devices(kind='output')['default_samplerate']
    sample_size = numpy.arange(sample_rate * duration)
    samples = amplitude * numpy.sin(2 * numpy.pi * sample_size * freq / sample_rate)

    sd.play(samples, sample_rate)
    sd.wait()

def main():
    logging.info('playing prompt')
    play_prompt()

    sleep(0.25)

    logging.info('playing tone')
    play_tone()

if __name__ == "__main__":
    main()
