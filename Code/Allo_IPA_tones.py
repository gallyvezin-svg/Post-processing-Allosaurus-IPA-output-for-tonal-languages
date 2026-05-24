import allosaurus
from allosaurus.app import read_recognizer
import parselmouth
import jiwer
import numpy as np
import unicodedata

LANGUAGE_SPECIFIC_VOWEL_SET = set("iɛauɒɔ")
LANGUAGE_SPECIFIC_CONFIGURATION = {
    "zulu": {
        "High": "\u0301",      # ◌́
        "Low": "\u0300",       # ◌̀
    },
    
    "example of 7-tone system": {
        # --- Levels ---
        "High": "\u0301",      # ◌́
        "Mid": "",             # sometimes, no symbol
        "Low": "\u0300",       # ◌̀
        
        # --- Contours ---
        "rising": "\u030C",            # ◌̌
        "rising_high": "\u1DC4",       # ◌᷄
        "rising_low": "\u1DC5",        # ◌᷅
        "rising_falling": "\u1DC8"     # ◌᷈
    }
}
ACTIVE_LANGUAGE = "zulu" 
actual_config = LANGUAGE_SPECIFIC_CONFIGURATION[ACTIVE_LANGUAGE]

audio_file = r"C:\Users\...\audios\test_zulu.wav"

# Allosaurus IPA transcription and timestamps clarification
model = read_recognizer()
text_output = model.recognize(audio_file, lang_id='zul')
timestamp_output = model.recognize(audio_file, lang_id='zul', timestamp=True)
def parser_timestamps_allosaurus(timestamp_output_str):
    segments = []
    for line in str(timestamp_output_str).strip().split('\n'):
        elements = line.split()
        if len(elements) == 3:
            start = float(elements[0])
            duration = float(elements[1])
            phone = elements[2]
            segments.append({"start": start, "end": start + duration, "phone": phone})
    return segments

# Extracting F0 from audio
sound = parselmouth.Sound(audio_file)
F0 = sound.to_pitch()
F0_values = F0.selected_array['frequency']
timestamps = F0.xs()

voiced_frequencies = F0_values[F0_values > 0]
F0_mean = np.mean(voiced_frequencies)
F0_STD = np.std(voiced_frequencies)

F0_real_data = []
for t, hz in zip(timestamps, F0_values):
    z = (hz - F0_mean) / F0_STD if hz > 0 else None
    F0_real_data.append({"time": t, "z_score": z})

# F0 to tone
def F0_to_tone(z_scores_list, config):
    valid_z = [z for z in z_scores_list if z is not None]
    if len(valid_z) == 0:
        return ""
    
    th_contour = config.get("threshold_contour", 0.4)
    th_level = config.get("threshold_level", 1.2)
    th_mid = config.get("threshold_mid", 0.4)
    
    mean_z = np.mean(valid_z)
    third = len(valid_z) // 3
    z_begin = np.mean(valid_z[:third]) if third > 0 else valid_z[0]
    z_end = np.mean(valid_z[-third:]) if third > 0 else valid_z[-1]
    global_delta = z_end - z_begin

    # Complex contour
    if "rising_falling" in config and len(valid_z) >= 3:
        z_mid = np.mean(valid_z[third:2*third]) if third > 0 else mean_z
        if (z_mid - z_begin > th_contour) and (z_mid - z_end > th_contour):
            return config["rising_falling"]

    # Simple contours
    if abs(global_delta) >= th_contour:
        if global_delta > 0: 
            if "rising_high" in config and z_begin > -0.2: 
                return config["rising_high"]
            if "rising_low" in config and z_end < 0.4: 
                return config["rising_low"]
            if "rising" in config: 
                return config["rising"]
        else:
            if "falling" in config: 
                return config["falling"]

    # Levels
    if "very_high" in config and mean_z > th_level: 
        return config["very_high"]
    if "very_low" in config and mean_z < -th_level: 
        return config["very_low"]
    if "Mid" in config:
        # 3 Levels
        if mean_z > th_mid and "High" in config: return config["High"]
        if mean_z < -th_mid and "Low" in config: return config["Low"]
        return config["Mid"]  
    else:
        # 2 Levels
        if mean_z > 0.0 and "High" in config: return config["High"]
        return config.get("Low", "")

# Syncronize Allosaurus timestamps with F0
def Allo_pitch(allosaurus_segments, F0_data, config, tolerance=0.03):
    final_transcription = []
    for segment in allosaurus_segments:
        start_large = segment["start"] - tolerance
        end_large = segment["end"] + tolerance
        phone = segment["phone"]
        
        if any(char in LANGUAGE_SPECIFIC_VOWEL_SET for char in phone):
            z_scores_vowel = [f["z_score"] for f in F0_data if start_large <= f["time"] <= end_large]
            diacritics = F0_to_tone(z_scores_vowel, config)
            final_transcription.append(phone + diacritics)
        else:
            final_transcription.append(phone)
    return " ".join(final_transcription)
allo_timestamps = parser_timestamps_allosaurus(timestamp_output)
transcription_with_tones = Allo_pitch(allo_timestamps, F0_real_data, actual_config)

# print
print(f"RESULTS for {ACTIVE_LANGUAGE.upper()}\n")
print(f"Allosaurus            : {text_output}")
print(f"Allosaurus with tones : {transcription_with_tones}\n")