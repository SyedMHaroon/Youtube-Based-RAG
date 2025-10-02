## YouTube Transcription + Q&A (Streamlit)

A simple Streamlit app that:

- Transcribes audio from a YouTube video using Faster-Whisper
- Saves a timestamped transcript to `transcript.json`
- Lets you ask questions about the transcript using a lightweight RAG pipeline (FAISS + embeddings + Groq LLM)

### Features

- **YouTube audio download** via `yt-dlp`
- **Accurate transcription** with `faster-whisper`
- **Timestamped segments** stored in `transcript.json`
- **Ask questions** about the transcript content powered by embeddings and an LLM

---

## Prerequisites

- **Python** 3.9–3.11
- **ffmpeg** installed and available on PATH (required for `yt-dlp -x` audio extraction)
  - Windows: download from `https://www.gyan.dev/ffmpeg/builds/` and add the `bin` folder to PATH
  - macOS (Homebrew): `brew install ffmpeg`
  - Linux (Debian/Ubuntu): `sudo apt-get install ffmpeg`
- **Groq API key** (for the Q&A step)
  - Get one from `https://console.groq.com/`
  - Set environment variable `GROQ_API_KEY`

Note: This repo includes a Windows `yt-dlp.exe`. On other platforms, install `yt-dlp` as shown below.

---

## Getting the Project (Download/Clone)

Choose one:

- Download the folder as a ZIP and extract anywhere on your machine
- Or clone your repository copy:

```bash
git clone <your-repo-url> yt
cd yt
```

If you downloaded as ZIP, ensure the files `app.py`, `requirements.txt`, and (on Windows) `yt-dlp.exe` are present in the same directory.

---

## Installation

1) Create and activate a virtual environment (recommended)

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

2) Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3) Ensure `ffmpeg` is installed and on PATH (see Prerequisites)

4) Provide your Groq API key

You can set it via environment variable or a `.env` file.

```bash
# Windows (PowerShell)
$env:GROQ_API_KEY = "your_groq_api_key_here"

# macOS/Linux (bash/zsh)
export GROQ_API_KEY="your_groq_api_key_here"
```

Alternatively, create a `.env` file next to `app.py`:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

---

## Using the Tool

1) Start the Streamlit app

```bash
streamlit run app.py
```

2) In your browser (auto-opens), paste a YouTube URL and click "Transcribe"

- The app downloads audio using `yt-dlp` and extracts to `temp_audio.mp3`
- The audio is transcribed via Faster-Whisper
- A `transcript.json` file is created containing the full text and timestamped segments
- The transcript is also rendered on the page

3) Ask questions about the transcript

- Use the text input labeled "Ask a question about your PDF" (this is actually for the video transcript)
- The app builds a small FAISS vector store from the transcript chunks
- Your question is answered by a Groq-hosted model (configured in code) using those retrieved chunks

---

## Platform Notes

- Windows: This folder includes `yt-dlp.exe`. The app calls `yt-dlp` via `subprocess`; on Windows, `yt-dlp.exe` in the working directory is typically discovered. If not, either add the folder to PATH, rename the command to `./yt-dlp.exe` in `app.py`, or install via `pip install yt-dlp` so `yt-dlp` is on PATH.
- macOS/Linux: Install `yt-dlp` using `pipx install yt-dlp` or `pip install yt-dlp` (or your package manager) so the `yt-dlp` command is available.

---

## Configuration

Some knobs can be tweaked directly in `app.py`:

- Whisper model size in `transcribe_audio(..., model_size="base")`. Valid sizes include `tiny`, `base`, `small`, `medium`, `large`.
- Output file name for the transcript (`output_file="transcript.json"`).
- Groq model in `ChatGroq(model="llama-3.1-8b-instant", ...)`.
- Embedding model in `HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")`.

---

## Troubleshooting

- "ffmpeg not found" when extracting audio:
  - Install ffmpeg and ensure it is on PATH; restart your terminal/IDE.

- `yt-dlp` command not found:
  - Windows: ensure `yt-dlp.exe` is in the same folder you run the app from, or install `yt-dlp` and add to PATH.
  - macOS/Linux: `pip install yt-dlp` or `pipx install yt-dlp`.

- Slow first run:
  - Models (Whisper and embeddings) are downloaded on first use; subsequent runs are faster.

- Empty or partial `transcript.json`:
  - Check the YouTube URL is accessible and not geo/age-restricted, and that audio was downloaded.

- Q&A returns empty or irrelevant answers:
  - Ensure `GROQ_API_KEY` is set and valid; confirm the chosen model is available for your account.

---

## How to Update or Replace yt-dlp

- Windows: replace the included `yt-dlp.exe` with the latest release from `https://github.com/yt-dlp/yt-dlp/releases`. Keep the filename as `yt-dlp.exe`.
- Cross-platform alternative: install via Python

```bash
pip install -U yt-dlp
```

---

## License

This project is provided as-is for educational and personal use. Check licenses of dependencies (`yt-dlp`, `faster-whisper`, `faiss`, `sentence-transformers`, `langchain`, `streamlit`, and Groq API terms) before commercial use.


