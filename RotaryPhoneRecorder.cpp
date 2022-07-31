// #define MINIAUDIO_IMPLEMENTATION
#include "miniaudio.h"

#include <chrono>
#include <iostream>
#include <thread>

void logResult(const ma_result& inResult, const std::string& inMessage)
{
    std::cout << inMessage << " - " << ma_result_description(inResult) << std::endl;
}

ma_result playPrompt(ma_engine* inEngine, const char* inPromptFile)
{
    ma_sound promptSound;
    ma_result result = ma_sound_init_from_file(inEngine, inPromptFile, 0, NULL, NULL, &promptSound);
    if (result != MA_SUCCESS)
    {
        return result;
    }

    ma_sound_set_looping(&promptSound, MA_FALSE);

    result = ma_sound_start(&promptSound);
    if (result != MA_SUCCESS)
    {
        ma_sound_uninit(&promptSound);
        return result;
    }

    while (!ma_sound_at_end(&promptSound))
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    ma_sound_uninit(&promptSound);
    return MA_SUCCESS;
}

ma_result playBeep(ma_engine* inEngine)
{
    ma_waveform_config beepConfig = ma_waveform_config_init(inEngine->pDevice->playback.format,
                                                            ma_engine_get_channels(inEngine),
                                                            ma_engine_get_sample_rate(inEngine),
                                                            ma_waveform_type_sine,
                                                            0.2,
                                                            440);

    ma_waveform beepWaveform;
    ma_result result = ma_waveform_init(&beepConfig, &beepWaveform);
    if (result != MA_SUCCESS)
    {
        return result;
    }

    ma_sound beepSound;
    result = ma_sound_init_from_data_source(inEngine, &beepWaveform, 0, NULL, &beepSound);
    if (result != MA_SUCCESS)
    {
        ma_waveform_uninit(&beepWaveform);
        return result;
    }

    ma_sound_set_looping(&beepSound, MA_FALSE);
    ma_sound_set_stop_time_in_pcm_frames(&beepSound, ma_engine_get_time(inEngine) + (ma_engine_get_sample_rate(inEngine) * .75));

    result = ma_sound_start(&beepSound);
    if (result != MA_SUCCESS)
    {
        ma_waveform_uninit(&beepWaveform);
        ma_sound_uninit(&beepSound);
        return result;
    }

    while (ma_sound_is_playing(&beepSound))
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    ma_sound_uninit(&beepSound);
    ma_waveform_uninit(&beepWaveform);
    return MA_SUCCESS;
}

int main()
{
    ma_engine engine;
    ma_result result = ma_engine_init(NULL, &engine);
    if (result != MA_SUCCESS)
    {
        logResult(result, "Failed to initialize engine");
        return result;
    }

    std::cout << "Playing prompt..." << std::endl;

    result = playPrompt(&engine, "test_prompt.wav");
    if (result != MA_SUCCESS)
    {
        logResult(result, "Failed to play prompt audio");
        ma_engine_uninit(&engine);
        return result;
    }

    std::cout << "Playing beep..." << std::endl;

    result = playBeep(&engine);
    if (result != MA_SUCCESS)
    {
        logResult(result, "Failed to play beep sound");
        ma_engine_uninit(&engine);
        return result;
    }

    ma_engine_uninit(&engine);
    return MA_SUCCESS;
}