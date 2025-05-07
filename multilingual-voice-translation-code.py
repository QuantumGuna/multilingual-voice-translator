#!/home/gunab/marianmt_env/bin/python3
import os
import subprocess
import sys
import argparse
import time
from pathlib import Path

# First, import hardware libraries globally
try:
    import RPi.GPIO as GPIO
    from RPLCD.i2c import CharLCD
except ImportError as e:
    print(f"Error: Required hardware libraries not installed: {e}")
    print("Please install them with:")
    print("pip install RPi.GPIO RPLCD")
    sys.exit(1)

# Initialize global LCD and GPIO
# LCD configuration (I2C)
LCD_I2C_ADDRESS = 0x27  # Change if necessary
LCD_COLUMNS = 16
LCD_ROWS = 2
lcd = CharLCD(i2c_expander='PCF8574', address=LCD_I2C_ADDRESS, port=1, cols=LCD_COLUMNS, rows=LCD_ROWS)

# Display welcome message
def display_welcome_sequence():
    lcd.clear()
    lcd.write_string("WELCOME")
    time.sleep(3)  # 3-second delay
    lcd.clear()
    lcd.write_string("Created By GUNA")
    time.sleep(2)  # 2-second delay

# Show welcome sequence first
display_welcome_sequence()

# Show gathering libraries message
lcd.clear()
lcd.write_string("Gathering")
lcd.crlf()
lcd.write_string("Libraries...")

# Now import remaining libraries
print("Initializing libraries...")
# Existing libraries for speech translation pipeline
try:
    from transformers import MarianMTModel, MarianTokenizer
except ImportError:
    print("Error: transformers library not installed. Please install it with:")
    print("pip install transformers torch")
    sys.exit(1)

# ----------------------------
# Configuration for Hardware
# ----------------------------

# GPIO pin configuration (using BCM numbering)
BUTTON_UP_PIN     = 17
BUTTON_DOWN_PIN   = 27
BUTTON_OK_PIN     = 22
BUTTON_RECORD_PIN = 23
BUTTON_RESET_PIN  = 24

LED_RECORD_PIN    = 5  # RED LED
LED_TRANSLATE_PIN = 6  # BLUE LED
LED_TTS_PIN       = 13 # GREEN LED

# Set up GPIO
GPIO.setmode(GPIO.BCM)
# Set push buttons as input with internal pull-up resistors
for pin in [BUTTON_UP_PIN, BUTTON_DOWN_PIN, BUTTON_OK_PIN, BUTTON_RECORD_PIN, BUTTON_RESET_PIN]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set LED pins as outputs
for pin in [LED_RECORD_PIN, LED_TRANSLATE_PIN, LED_TTS_PIN]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# ----------------------------
# Your Existing Pipeline Data
# ----------------------------
LANGUAGES = {
    1: {"name": "Arabic",     "mt_code": "ar", "piper_folder": "ar_JO", "piper_model": "ar_JO-kareem-low.onnx", "piper_config": "ar_JO-kareem-low.onnx.json"},
    2: {"name": "German",     "mt_code": "de", "piper_folder": "de_DE", "piper_model": "de_DE-eva_k-x_low.onnx", "piper_config": "de_DE-eva_k-x_low.onnx.json"},
    3: {"name": "Greek",      "mt_code": "el", "piper_folder": "el_GR", "piper_model": "el_GR-rapunzelina-low.onnx", "piper_config": "el_GR-rapunzelina-low.onnx.json"},
    4: {"name": "Spanish",    "mt_code": "es", "piper_folder": "es_ES", "piper_model": "es_ES-carlfm-x_low.onnx", "piper_config": "es_ES-carlfm-x_low.onnx.json"},
    5: {"name": "Finnish",    "mt_code": "fi", "piper_folder": "fi_FI", "piper_model": "fi_FI-harri-low.onnx", "piper_config": "fi_FI-harri-low.onnx.json"},
    6: {"name": "Icelandic",  "mt_code": "is", "piper_folder": "is_IS", "piper_model": "is_IS-bui-medium.onnx", "piper_config": "is_IS-bui-medium.onnx.json"},
    7: {"name": "Italian",    "mt_code": "it", "piper_folder": "it_IT", "piper_model": "it_IT-riccardo-x_low.onnx", "piper_config": "it_IT-riccardo-x_low.onnx.json"},
    8: {"name": "Romanian",   "mt_code": "ro", "piper_folder": "ro_RO", "piper_model": "ro_RO-mihai-medium.onnx", "piper_config": "ro_RO-mihai-medium.onnx.json"},
    9: {"name": "Russian",    "mt_code": "ru", "piper_folder": "ru_RU", "piper_model": "ru_RU-denis-medium.onnx", "piper_config": "ru_RU-denis-medium.onnx.json"},
    10: {"name": "Swedish",   "mt_code": "sv", "piper_folder": "sv_SE", "piper_model": "sv_SE-nst-medium.onnx", "piper_config": "sv_SE-nst-medium.onnx.json"},
    11: {"name": "Turkish",   "mt_code": "tr", "piper_folder": "tr_TR", "piper_model": "tr_TR-dfki-medium.onnx", "piper_config": "tr_TR-dfki-medium.onnx.json"},
    12: {"name": "Ukrainian", "mt_code": "uk", "piper_folder": "uk_UA", "piper_model": "uk_UA-lada-x_low.onnx", "piper_config": "uk_UA-lada-x_low.onnx.json"},
    13: {"name": "Vietnamese","mt_code": "vi", "piper_folder": "vi_VN", "piper_model": "vi_VN-vivos-x_low.onnx", "piper_config": "vi_VN-vivos-x_low.onnx.json"},
    14: {"name": "Chinese",   "mt_code": "zh", "piper_folder": "zh_CN", "piper_model": "zh_CN-huayan-x_low.onnx", "piper_config": "zh_CN-huayan-x_low.onnx.json"},
    15: {"name": "French",    "mt_code": "fr", "piper_folder": "fr_FR", "piper_model": "fr_FR-gilles-low.onnx", "piper_config": "fr_FR-gilles-low.onnx.json"},
}

DEFAULT_CONFIGS = {
    "device": "plughw:3,0",
    "duration": 5,
    "whisper_bin": "/home/gunab/whisper.cpp/build/bin/whisper-cli",
    "model_file": "/home/gunab/whisper.cpp/models/ggml-tiny.en.bin",
    "audio_file": "/home/gunab/whisper.cpp/audio_files/recorded_audio.wav",
    "piper_bin": "/home/gunab/piper/build/piper/piper",
    "piper_voices_base": "/home/gunab/piper/build/piper/piper_voices"
}

# ----------------------------
# Utility Functions for Buttons and LCD
# ----------------------------
def update_lcd(line1, line2="", scroll_delay=0.3):
    """Display text on the LCD with automatic scrolling for long messages."""
    lcd.clear()
    
    # Display normally if both lines fit within 16 characters
    if len(line1) <= LCD_COLUMNS and len(line2) <= LCD_COLUMNS:
        lcd.write_string(line1)
        if line2:
            lcd.crlf()  # Move to the second line
            lcd.write_string(line2)
        return

    # Scroll first line if too long
    if len(line1) > LCD_COLUMNS:
        for i in range(len(line1) - LCD_COLUMNS + 1):
            lcd.clear()
            lcd.write_string(line1[i:i+LCD_COLUMNS])
            if line2:
                lcd.crlf()
                lcd.write_string(line2[:LCD_COLUMNS])
            time.sleep(scroll_delay)
    
    # Scroll second line if too long
    if len(line2) > LCD_COLUMNS:
        for i in range(len(line2) - LCD_COLUMNS + 1):
            lcd.clear()
            lcd.write_string(line1[:LCD_COLUMNS])
            lcd.crlf()
            lcd.write_string(line2[i:i+LCD_COLUMNS])
            time.sleep(scroll_delay)


def wait_for_button_press(pin, debounce=0.2):
    """Wait until the specified button is pressed (active low)."""
    while GPIO.input(pin):
        time.sleep(0.01)
    time.sleep(debounce)  # debounce delay

def check_reset_button():
    """Check if reset button is pressed and handle accordingly."""
    if not GPIO.input(BUTTON_RESET_PIN):
        wait_for_button_press(BUTTON_RESET_PIN)
        update_lcd("Process Reset", "")
        time.sleep(1)
        return True
    return False

def language_selection_menu():
    """Display language selection on LCD using up/down/OK buttons."""
    lang_keys = sorted(LANGUAGES.keys())
    index = 0
    while True:
        current_lang = LANGUAGES[lang_keys[index]]
        update_lcd("Select Language:", f"{lang_keys[index]}. {current_lang['name']}")
        
        # Check button states (polling)
        if not GPIO.input(BUTTON_UP_PIN):
            index = (index - 1) % len(lang_keys)
            wait_for_button_press(BUTTON_UP_PIN)
        elif not GPIO.input(BUTTON_DOWN_PIN):
            index = (index + 1) % len(lang_keys)
            wait_for_button_press(BUTTON_DOWN_PIN)
        elif not GPIO.input(BUTTON_OK_PIN):
            wait_for_button_press(BUTTON_OK_PIN)
            update_lcd("Selected:", current_lang["name"])
            time.sleep(1)
            # Update LCD to show translation direction
            update_lcd(f"ENG --> {current_lang['name']}")
            time.sleep(1.5)
            return current_lang
        
        # Check reset button
        if check_reset_button():
            # If reset is pressed, we just continue the language selection
            # which effectively restarts this phase
            continue
            
        time.sleep(0.1)

def wait_for_record_trigger():
    """Wait until the record button is pressed."""
    update_lcd("Press RECORD to", "Start Record")
    
    while True:
        # Check for record button
        if not GPIO.input(BUTTON_RECORD_PIN):
            wait_for_button_press(BUTTON_RECORD_PIN)
            update_lcd("Recording...", "")
            return True
            
        # Check for reset button
        if check_reset_button():
            return False
            
        time.sleep(0.01)

# ----------------------------
# Existing Pipeline Functions (modified)
# ----------------------------

def check_dependencies():
    """Check if required external programs are installed"""
    dependencies = ["arecord", "aplay"]
    missing = []
    
    for cmd in dependencies:
        if subprocess.run(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
            missing.append(cmd)
    
    if missing:
        print(f"Error: Missing required dependencies: {', '.join(missing)}")
        sys.exit(1)
    
    for path_key in ["whisper_bin", "piper_bin"]:
        if not os.path.isfile(DEFAULT_CONFIGS[path_key]):
            print(f"Error: {path_key} not found at {DEFAULT_CONFIGS[path_key]}")
            sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Speech translation pipeline")
    parser.add_argument("--device", help=f"Audio input device (default: {DEFAULT_CONFIGS['device']})")
    parser.add_argument("--duration", type=int, help=f"Recording duration in seconds (default: {DEFAULT_CONFIGS['duration']})")
    parser.add_argument("--text", help="Use this text instead of recording and transcribing")
    parser.add_argument("--language", type=int, choices=LANGUAGES.keys(), help="Language code to translate to")
    args = parser.parse_args()
    return args


def record_audio(device, duration, audio_file):
    """Record audio using arecord with LED indicator for recording."""
    print(f"\nRecording audio for {duration} seconds...")
    GPIO.output(LED_RECORD_PIN, GPIO.HIGH)  # Turn on RED LED for recording
    record_cmd = f'arecord -D "{device}" -f S16_LE -r 16000 -c 1 -d {duration} "{audio_file}"'
    ret = subprocess.run(record_cmd, shell=True)
    GPIO.output(LED_RECORD_PIN, GPIO.LOW)  # Turn off recording LED
    if ret.returncode != 0:
        print("Error recording audio. Check your microphone and audio device settings.")
        sys.exit(1)
    print("Recording complete.")
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
        print("Error: Audio file is empty or wasn't created.")
        sys.exit(1)

def transcribe_audio(whisper_bin, model_file, audio_file):
    """Transcribe audio using whisper.cpp with a status update."""
    update_lcd("Transcribing...", "")
    print("\nTranscribing audio with Whisper...")
    whisper_cmd = f'{whisper_bin} -m "{model_file}" -f "{audio_file}"'
    try:
        result = subprocess.run(whisper_cmd, shell=True, capture_output=True, text=True, check=True)
        output_lines = result.stdout.strip().split('\n')
        transcription_lines = []
        for line in output_lines:
            if "-->" in line:
                continue
            if line.strip() and not line.startswith("["):
                transcription_lines.append(line.strip())
        if not transcription_lines:
            for line in reversed(output_lines):
                if line.strip():
                    transcription_lines.append(line.strip())
                    break
        transcription = " ".join(transcription_lines)
        if not transcription:
            print("Warning: No transcription detected.")
            return "No speech detected"
        return transcription
    except subprocess.CalledProcessError as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)


def translate_text(text, target_lang):
    """Translate text using MarianMT with LED indicator."""
    GPIO.output(LED_TRANSLATE_PIN, GPIO.HIGH)  # Turn on BLUE LED for translation
    mt_code = target_lang["mt_code"]
    model_name = f"Helsinki-NLP/opus-mt-en-{mt_code}"
    update_lcd("Translating...", "")
    print(f"\nTranslating text using model {model_name}...")
    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        translated_tokens = model.generate(**inputs)
        translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        GPIO.output(LED_TRANSLATE_PIN, GPIO.LOW)  # Turn off translation LED
        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        GPIO.output(LED_TRANSLATE_PIN, GPIO.LOW)
        return text

def synthesize_speech(text, lang_data, piper_bin, piper_voices_base):
    """Synthesize speech using Piper TTS."""
    update_lcd("Synthesizing...", "")
    print("\nGenerating translated speech with Piper TTS...")
    piper_folder = lang_data["piper_folder"]
    voice_model_path = os.path.join(piper_voices_base, piper_folder, lang_data["piper_model"])
    voice_config_path = os.path.join(piper_voices_base, piper_folder, lang_data["piper_config"])
    output_dir = os.path.join(piper_voices_base, piper_folder)
    os.makedirs(output_dir, exist_ok=True)
    output_wav = os.path.join(output_dir, "translated_speech.wav")
    if not os.path.exists(voice_model_path):
        print(f"Error: Voice model not found at {voice_model_path}")
        return None
    if not os.path.exists(voice_config_path):
        print(f"Error: Voice config not found at {voice_config_path}")
        return None
    try:
        safe_text = text.replace('"', '\\"')
        piper_cmd = f'echo "{safe_text}" | {piper_bin} --model "{voice_model_path}" --config "{voice_config_path}" --output-file "{output_wav}"'
        print(f"Executing command: {piper_cmd}")
        process = subprocess.run(piper_cmd, shell=True, capture_output=True, text=True)
        if os.path.exists(output_wav):
            file_size = os.path.getsize(output_wav)
            print(f"Output audio file created: {output_wav} (size: {file_size} bytes)")
            if file_size == 0:
                print("Warning: Created file has zero size")
                return None
            return output_wav
        else:
            print(f"Error: Output audio file was not created at {output_wav}")
            return None
    except Exception as e:
        print(f"Error in speech synthesis: {e}")
        return None
        
def play_audio(audio_file):
    """Play the generated audio file with GREEN LED indicator."""
    if not os.path.exists(audio_file):
        print(f"Error: Audio file {audio_file} not found")
        return False
    update_lcd("Playing audio...", "")
    print("\nPlaying translated speech...")
    
    # Turn on GREEN LED for audio playback
    GPIO.output(LED_TTS_PIN, GPIO.HIGH)
    
    play_cmd = f"aplay {audio_file}"
    ret = subprocess.run(play_cmd, shell=True)
    
    # Turn off GREEN LED after playback
    GPIO.output(LED_TTS_PIN, GPIO.LOW)
    
    return ret.returncode == 0

def select_language(preset_lang=None):
    """Select target language using push buttons and LCD."""
    if preset_lang and preset_lang in LANGUAGES:
        update_lcd("Preset Lang:", LANGUAGES[preset_lang]["name"])
        # Show translation direction
        time.sleep(1)
        update_lcd(f"ENG --> {LANGUAGES[preset_lang]['name']}")
        time.sleep(1.5)
        return LANGUAGES[preset_lang]
    return language_selection_menu()

# ----------------------------
# Main Process Integration with Workflow Loop
# ----------------------------
def run_translation_workflow(config, lang_data, input_text=None):
    """Run a complete translation workflow cycle."""
    # Get text either from direct input or by recording
    if input_text:
        original_text = input_text
        update_lcd("Using provided", "text")
        print(f"\nUsing provided text: {original_text}")
    else:
        # Wait for record button press and check for reset
        if not wait_for_record_trigger():
            # Reset was pressed
            return False
            
        # Start recording with RED LED
        record_audio(config["device"], config["duration"], config["audio_file"])
        
        # Check for reset button during/after recording
        if check_reset_button():
            return False
            
        # Transcribe the audio
        original_text = transcribe_audio(config["whisper_bin"], config["model_file"], config["audio_file"])
        update_lcd("Detected Speech:", original_text)
        print(f"\nDetected speech: {original_text}")
        
        # Check for reset button after transcription
        if check_reset_button():
            return False

    # Translate text with BLUE LED
    translated_text = translate_text(original_text, lang_data)
    update_lcd("Translated:", translated_text)
    print(f"Translated Text ({lang_data['name']}): {translated_text}")
    
    # Check for reset after translation
    if check_reset_button():
        return False
    
    # Synthesize speech
    output_wav = synthesize_speech(translated_text, lang_data, config["piper_bin"], config["piper_voices_base"])
    
    # Check for reset after synthesis
    if check_reset_button():
        return False
    
    # Play audio if synthesis was successful with GREEN LED
    if output_wav:
        if not play_audio(output_wav):
            print("Error playing audio. Check your audio playback settings.")
    
    # Print summary
    print("\n--- Summary ---")
    print(f"Selected Language: {lang_data['name']}")
    print(f"Original Text: {original_text}")
    print(f"Translated Text: {translated_text}")
    if output_wav:
        print(f"Translated Speech saved at: {output_wav}")
    print("Process complete!")
    
    # Workflow completed successfully
    return True

def main():
    args = parse_arguments()
    config = DEFAULT_CONFIGS.copy()
    if args.device:
        config["device"] = args.device
    if args.duration:
        config["duration"] = args.duration
    
    check_dependencies()
    
    # Main workflow loop
    while True:
        # Language selection phase
        lang_data = select_language(args.language)
        print(f"\nSelected Language: {lang_data['name']}")
        
        while True:
            # Run translation workflow
            workflow_success = run_translation_workflow(config, lang_data, args.text)
            
            # If a reset occurred during the workflow, break to language selection
            if not workflow_success:
                break
                
            # For command-line text input (args.text), only run once
            if args.text:
                return
                
            # After a successful workflow, return to "Press RECORD" state
            # The workflow will handle reset button checks
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        update_lcd("Operation", "Cancelled")
        print("\nOperation cancelled by user.")
    except Exception as e:
        update_lcd("Error occurred", "")
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # Clean up all resources
        for pin in [LED_RECORD_PIN, LED_TRANSLATE_PIN, LED_TTS_PIN]:
            GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()
        lcd.clear()
