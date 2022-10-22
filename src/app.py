import time
import logging

import RPi.GPIO
import simpleaudio as sa

wave_obj = sa.WaveObject.from_wave_file("../audio/test_prompt.wav")
play_obj = wave_obj.play()
play_obj.wait_done()
