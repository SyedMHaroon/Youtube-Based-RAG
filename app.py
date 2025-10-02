from faster_whisper import WhisperModel
import json
import subprocess
import streamlit as st
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
#langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
load_dotenv()

def main():
    st.title("Youtube Transcription")
    st.write("Enter the URL of the Youtube video to transcribe")
    url = st.text_input("Youtube URL")
    if st.button("Transcribe"):
        audio_path = download_audio_from_youtube(url)
        transcript = transcribe_audio(
            audio_path=audio_path,
            model_size="base",
            output_file="transcript.json"
        )
        with open('transcript.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for segment in data['segments']:
            start_time = segment['start_time']
            end_time = segment['end_time']
            text = segment['text']
            
            st.write(f"[{start_time} - {end_time}] {text}")

    userQuestions = st.text_input("Ask a question about your PDF")
    if userQuestions:
        ragModel(userQuestions, 'transcript.json')
    

def download_audio_from_youtube(url, output_path="temp_audio.mp3"):
    command = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "-o", output_path,
        url
    ]
    subprocess.run(command, check=True)
    return output_path



def transcribe_audio(audio_path, model_size="base", output_file=None):
    """
    Transcribe video with timestamps
    
    Args:
        audio_path: Path to your video file
        model_size: tiny, base, small, medium, large
        output_file: Optional JSON file to save results
    """
    
    print(f"Loading {model_size} model...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print(f"Transcribing {audio_path}...")
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True  # Get word-level timestamps
    )
    
    print(f"Language: {info.language} (probability: {info.language_probability:.2f})")
    
    # Collect results
    transcript_data = []
    full_text = []
   
    for segment in segments:
        # Format timestamps
        start_time = f"{int(segment.start//60):02d}:{int(segment.start%60):02d}"
        end_time = f"{int(segment.end//60):02d}:{int(segment.end%60):02d}"
        
        # Print to console
        print(f"[{start_time} - {end_time}] {segment.text}")
        
        # Store data
        segment_data = {
            'start': segment.start,
            'end': segment.end,
            'start_time': start_time,
            'end_time': end_time,
            'text': segment.text.strip()
        }
        
        # # Add word-level timestamps if available
        # if hasattr(segment, 'words'):
        #     segment_data['words'] = [
        #         {
        #             'word': word.word,
        #             'start': word.start,
        #             'end': word.end
        #         }
        #         for word in segment.words
        #     ]
        
        transcript_data.append(segment_data)
        full_text.append(segment.text.strip())
    
    # Save to file if requested
    if output_file:
        result = {
            'language': info.language,
            'full_text': ' '.join(full_text),
            'segments': transcript_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved to {output_file}")
    
    return transcript_data


def ragModel(question, json_file):
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    full_text = data['full_text']
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 200,
        chunk_overlap = 50,
        length_function = len
        )

    chunks = text_splitter.split_text(full_text)
    # print(chunks)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    knowledgeBase = FAISS.from_texts(chunks, embeddings)
    userQuestions = question
    if userQuestions:
        docs = knowledgeBase.similarity_search(userQuestions)
        llm = ChatGroq(
                model="llama-3.1-8b-instant",
                groq_api_key = os.environ.get("GROQ_API_KEY")
            )
        chain = load_qa_chain(llm, chain_type="stuff")
        response = chain.run(input_documents=docs, question=userQuestions)
        

        st.write(response)


if __name__ == "__main__":
    main()


