# Multilingual Voice Translator with Speech Recognition and Synthesis

🎓 **Final-Year Engineering Project by Guna**

This project is a **Raspberry Pi–based multilingual voice translator** designed to work offline. It records English speech, translates it into a selected target language, and outputs the translated speech — all controlled through physical buttons, LEDs, and an LCD interface.

---

## 💡 Features

✅ Offline **speech-to-text** using `whisper.cpp`  
✅ Offline **translation** using MarianMT (Helsinki-NLP models)  
✅ Offline **text-to-speech synthesis** using Piper TTS  
✅ **Hardware control** with push buttons, status LEDs (red, blue, green), and a 16x2 I2C LCD display  
✅ Configurable and modular Python code for Raspberry Pi  

---

## 🛠 Hardware Components

| Component          | Purpose                                |
|---------------------|---------------------------------------|
| Raspberry Pi 4B    | Main controller                        |
| Push Buttons       | Navigate language selection, record, reset |
| Red LED           | Indicates recording                    |
| Blue LED          | Indicates translation                  |
| Green LED         | Indicates audio playback               |
| 16x2 I2C LCD      | Displays system status and selections  |
| Microphone + Speaker | Captures input and plays output      |

---

## 📦 Software Requirements

- Python 3
- `RPi.GPIO`, `RPLCD` for hardware interaction
- `transformers`, `torch` for translation
- `arecord`, `aplay` (Linux audio tools)
- `whisper.cpp` (speech-to-text engine)
- `piper` (text-to-speech engine)

---

## 🚀 How to Run

1️⃣ Clone the repository:
```bash
git clone https://github.com/yourusername/multilingual-voice-translator.git
cd multilingual-voice-translator
```
2️⃣ Install Python dependencies:
```
pip install RPi.GPIO RPLCD transformers torch
```
3️⃣ Make sure arecord, aplay, whisper-cli, and piper are installed and properly configured on your Raspberry Pi.

4️⃣ Connect all hardware components as described in the wiring diagram (if provided).

5️⃣ Run the main script:
```
python multilingual-voiceotranslation-code.py
```
## 🌍 Supported Languages

- Arabic
- German
- Greek
- Spanish
- Finnish
- Icelandic
- Italian
- Romanian
- Russian
- Swedish
- Turkish
- Ukrainian
- Vietnamese
- Chinese
- French

*(More can be added by extending the language configuration in the code.)*

---

## 📸 Demo / Screenshots

![Wiring Diagram](https://github.com/QuantumGuna/multilingual-voice-translator/main/wiring-diagram.png)

---

## 👤 Author

**Guna**  
Final-Year B.Tech Engineering Student

🔗 [LinkedIn](https://www.linkedin.com/in/gunasekharbathula/)  
🔗 [GitHub](https://github.com/QuantumGuna)
🔗 [Instagram](https://www.instagram.com/mystery_mind_9_?igsh=OWlxNXk5aDljcmNk)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 💬 Acknowledgments

- Whisper by OpenAI  
- MarianMT by Helsinki-NLP  
- Piper TTS by Rhasspy Team

---
