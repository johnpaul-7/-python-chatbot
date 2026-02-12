import streamlit as st
from gtts import gTTS
import os

# Streamlit page configuration
st.title("Text-to-Speech Application")
st.write("Convert your text to speech using this simple application!")

# User Input
text_input = st.text_area("Enter the text you want to convert to speech:")

# Language selection (friendly names and codes)
languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de"
   
}
language_choice = st.selectbox("Select Language:", list(languages.keys()))
language_code = languages[language_choice]

# Generate Speech Button
if st.button("Convert to Speech"):
    if text_input.strip():  # Check if the input text is not empty
        try:
            # Generate TTS audio file
            tts = gTTS(text=text_input, lang=language_code, slow=False)
            tts.save("output.mp3")

            # Play the audio in Streamlit
            with open("output.mp3", "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3", start_time=0)

            st.success("Speech generated successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            # Clean up the temporary file
            if os.path.exists("output.mp3"):
                os.remove("output.mp3")
    else:
        st.warning("Please enter some text to convert.")

# Footer
st.write("Developed with ❤️ using Streamlit and gTTS.")