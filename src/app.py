import logging
import signal
import sounddevice as sd
import soundfile as sf
import numpy
from gpiozero import Button
from queue import Queue
from datetime import datetime

def output_callback(outdata, frames, *_):
    global current_frame

    if current_frame == 0:
        logger.info('playing prompt')

    chunksize = min(len(data) - current_frame, frames)
    outdata[:chunksize] = data[current_frame:current_frame + chunksize]

    if chunksize < frames:
        outdata[chunksize:] = 0

        logger.info('audio stopping')
        input_stream.start()

        raise sd.CallbackStop()

    current_frame += chunksize

def input_callback(indata, *_):
    if input_queue.empty():
        logger.info('recording started')

    input_queue.put(indata.copy())

def save_recording():
    if input_queue.empty():
        logger.warning('input queue was empty when trying to save recording')
        return

    # write queue data to file via soundfile object
    file_name = f'../output/{ datetime.now().strftime("%Y%m%d_%H%M%S") }.wav'
    output_file = sf.SoundFile(file=file_name, mode='x', samplerate=int(input_stream.samplerate), channels=1)
    with output_file:
        logger.info('saving recording')
        while not input_queue.empty():
            data = input_queue.get()
            output_file.write(data)
        logger.info('recording saved')

def get_tone_samples(sample_rate):
    duration = 0.75
    amplitude = 0.2
    freq = 440.0
    sample_size = numpy.arange(sample_rate * duration)

    silent_samples = 0 * numpy.arange(sample_rate * 0.25)
    tone_samples = amplitude * numpy.sin(2 * numpy.pi * sample_size * freq / sample_rate)
    
    samples = numpy.append(silent_samples, tone_samples)

    # add a couple extra samples so that the very end of the tone doesn't make it into the recording
    return numpy.append(samples, 0 * numpy.arange(sample_rate * 0.075)).reshape(-1, 1)

def phone_picked_up():
    logger.info('phone picked up')

    sd.sleep(1000)
    output_stream.start()

def phone_hung_up():
    logger.info('phone hung up')

    output_stream.abort()
    input_stream.abort()

    if not input_queue.empty():
        save_recording()

    global current_frame
    current_frame = 0

    logger.info('waiting for handset to be lifted')

def main():
    try:
        hook_switch = Button(17, bounce_time=0.2)
        
        hook_switch.when_pressed = phone_picked_up
        hook_switch.when_released = phone_hung_up

        logger.info('waiting for handset to be lifted')

        signal.pause()
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    logging.basicConfig(filename='../app.log', format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger()

    logger.info('initializing audio streams')

    current_frame = 0
    data, sample_rate = sf.read('../audio/audio_prompt.wav', always_2d=True)

    # append the tone samples to the prompt audio
    data = numpy.append(data, get_tone_samples(sample_rate), axis=0)

    input_stream = sd.InputStream(device=1, channels=1, callback=input_callback)
    output_stream = sd.OutputStream(samplerate=sample_rate, device=0, channels=1, callback=output_callback, finished_callback=input_stream.start)

    input_queue = Queue()

    main()
