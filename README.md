# Post-processing-Allosaurus-IPA-output-for-tonal-languages
This is a python script supposed to add correct tones on IPA symbols coming from Allosaurus transcriptions.

## Usage

### Libraries to install
To make this script work, you should install those libraries.

Allosaurus for the IPA transcription.

Parselmouth for the pitch (F0) extraction.

Jiwer in case you want to evaluate the transcription obtained (refer to the Evaluation part below).

and Numpy for F0 means and standard deviations.

```bash
pip install allosaurus praat-parselmouth jiwer numpy
```

### Language personnalization
First, to reduce the possibilities of the model to put tones on consonant, you may precise which on which phones it is possible to add tones in the language you want to test in "LANGUAGE_SPECIFIC_VOWEL_SET".

```python
LANGUAGE_SPECIFIC_VOWEL_SET = set("iɛauɒɔ")
```

Also, for the model to decide which and with how much tones it should deal, please precise the tones in the "LANGUAGE_SPECIFIC_CONFIGURATION" part. With "ACTIVE_LANGUAGE", you can choose the previsously built configuration.

This is why we need to import the unicodata library.

```python
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
```

### Directory
Put the access directory of the audio you want to use in "audio_file".

You can try the script with the zulu audio file in the "Audios" folder of the repository.

```python
audio_file = r"C:\Users\...\audios\test_zulu.wav"
```

### Allosaurus launch
To begin the basic IPA transcription with Allosaurus, we import its library and its read.recognizer.

To improve the quality of the results, only use languages from which Allosaurus has the allophonic inventory.
-> To verify if Allosaurus knows the allophonic inventory of a language use this command with the corresponding iso code in console : 

```bash
python -m allosaurus.bin.list_phone --lang zul
```

You should specify the iso code in "lang_id=" of the corresponding language so Allosaurus knows its allophonic inventory.

```python
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
```

### Output
After these steps, you can run the script and obtain two different outputs : 

The Allosaurus one provides the raw IPA transcription made by its library and the second one with tones adds suprasegmental tones where needed when the model detects their associated F0 schemes.

(Here, the example shows the output for the Zulu language, which needs a tone on every vowel, to adapt it, refer to the previous section "LANGUAGE_SPECIFIC_CONFIGURATION")

```python
Allosaurus            : l i m l i m l u n u z ɛ l u n
Allosaurus with tones : l í m l í m l ú n ù z ɛ́ l ú n
```

### Evaluation
If you want to evaluate the output obtained, you can download the "Code with Evaluation" in the "Evaluation" folder of the repository (and personnalize the script exactly as explained above) OR copy the following parts : 

You should add an expert IPA transcription of the audio you want to test and add this whole part containing PER (Phone Error Rate).

```python
# Evaluation
expert_ipa = "lìmá lìmá lùndùzɛ́là lùndùzɛ́là lálà lálà àsíséfì sɛ̀fá sɛ̀fá"
def PER (reference, hypothese):
    reference = reference.replace(" ", "")
    hypothese = hypothese.replace(" ", "")
    reference = unicodedata.normalize('NFC', reference)
    hypothese = unicodedata.normalize('NFC', hypothese)
    ref_phonemes = " ".join(list(reference))
    hyp_phonemes = " ".join(list(hypothese))
    resultats = jiwer.process_words(ref_phonemes, hyp_phonemes)
    return resultats.wer
per_allo = PER(expert_ipa, text_output)
per_allo_tones = PER(expert_ipa, transcription_with_tones)
```

Finally, replace the standart print section by this one, which includes the evaluation results.

```python
# print
print(f"RESULTS for {ACTIVE_LANGUAGE.upper()}\n")
print(f"Expert transcription  : {expert_ipa}")
print(f"Allosaurus            : {text_output}")
print(f"Allosaurus with tones : {transcription_with_tones}\n")
print("Evaluation:")
print(f"PER (Allosaurus)            : {per_allo * 100:.2f}%")
print(f"PER (Allosaurus with tones) : {per_allo_tones * 100:.2f}%")
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
