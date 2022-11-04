import threading
import logging
import signal
import sounddevice as sd
import soundfile as sf
import numpy
from gpiozero import Button

def callback(outdata, frames, *_):
    global current_frame

    chunksize = min(len(data) - current_frame, frames)
    outdata[:chunksize] = data[current_frame:current_frame + chunksize]

    if chunksize < frames:
        outdata[chunksize:] = 0

        logger.info('audio stopping')
        raise sd.CallbackStop()

    current_frame += chunksize

def get_tone_samples(sample_rate):
    duration = 0.75
    amplitude = 0.2
    freq = 440.0
    sample_size = numpy.arange(sample_rate * duration)

    silent_samples = 0 * numpy.arange(sample_rate * 0.25)
    tone_samples = amplitude * numpy.sin(2 * numpy.pi * sample_size * freq / sample_rate)
    
    return numpy.append(silent_samples, tone_samples).reshape(-1, 1)

def phone_picked_up():
    logger.info('phone picked up')

    stream.start()

def phone_hung_up():
    logger.info('phone hung up')

    stream.abort()

    global current_frame
    current_frame = 0

def main():
    try:
        hook_switch = Button(17, bounce_time=0.2)
        
        hook_switch.when_pressed = phone_picked_up
        hook_switch.when_released = phone_hung_up

        signal.pause()
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger()

    current_frame = 0
    data, sample_rate = sf.read('../audio/test_prompt.wav', always_2d=True)

    # append the tone samples to the prompt audio
    data = numpy.append(data, get_tone_samples(sample_rate), axis=0)

    stream = sd.OutputStream(samplerate=sample_rate, callback=callback)

    main()
