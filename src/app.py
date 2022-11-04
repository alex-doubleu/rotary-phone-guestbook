import time
import threading
import logging
import signal
import sounddevice as sd
import soundfile as sf
import numpy
from gpiozero import Button

def callback(outdata, frames, time, status):
    global current_frame

    chunksize = min(len(data) - current_frame, frames)
    outdata[:chunksize] = data[current_frame:current_frame + chunksize]

    if chunksize < frames:
        outdata[chunksize:] = 0
        event.set()

    current_frame += chunksize

def play_prompt(event):
    logger.info('playing prompt')

    with sd.OutputStream(callback=callback):
        event.wait()
        logger.info('event set, prompt audio stopping')

    global current_frame
    current_frame = 0

def get_tone_samples():
    duration = 0.75
    amplitude = 0.2
    freq = 440.0
    sample_rate = sd.default.samplerate
    sample_size = numpy.arange(sample_rate * duration)

    silent_samples = 0 * numpy.arange(sample_rate * 0.25)
    tone_samples = amplitude * numpy.sin(2 * numpy.pi * sample_size * freq / sample_rate)
    
    return numpy.append(silent_samples, tone_samples).reshape(-1, 1)

def record_message():
    logger.info('recording message')

    # data = sd.rec()
    # sd.wait()

    # sf.write('../output/test_recording.wav', data, int(sample_rate))

def phone_hung_up():
    logger.info('phone hung up')

    event.set()
    event.clear()

def phone_picked_up():
    logger.info('phone picked up')

    thread = threading.Thread(target=play_prompt_and_rec, args=[event])
    thread.start()
    # thread.join()

def play_prompt_and_rec(event):
    play_prompt(event)
    # record_message()

def main():
    try:
        hook_switch = Button(17, bounce_time=0.2)
        
        hook_switch.when_pressed = phone_picked_up
        hook_switch.when_released = phone_hung_up

        signal.pause()
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', level=logging.INFO)
    logger = logging.getLogger()

    data, sample_rate = sf.read('../audio/test_prompt.wav', always_2d=True)

    input_device = sd.query_devices(kind='input')
    output_device = sd.query_devices(kind='output')

    sd.default.device = input_device['index'], output_device['index']
    sd.default.samplerate = sample_rate

    event = threading.Event()
    current_frame = 0
    data = numpy.append(data, get_tone_samples(), axis=0)

    main()
