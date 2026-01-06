# YouTube Notemaker 

Extract transcripts from YouTube videos with AI-powered features, multiple export formats, and intelligent caching!
with AI summarization, advanced text processing, PDF/JSON export, and batch processing.

## 🌟 Key Features

### Core Capabilities
- ✅ **Dual Extraction Modes**: Captions (instant) or Audio (Whisper AI for any video)
- ✅ **99 Languages**: Auto-detect or choose from available languages
- ✅ **AI Summarization**: Claude or GPT-4 powered summaries and key points
- ✅ **Multiple Exports**: Markdown, PDF, and JSON
- ✅ **Smart Caching**: Avoid re-downloading with intelligent cache system
- ✅ **Progress Tracking**: Real-time progress bars in the UI
- ✅ **Batch Processing**: Process multiple videos or entire playlists

### 🎯 AI Features (Optional - Requires API Key)
- **AI Summarization**: Generate concise summaries (100-500 words)
- **Key Points Extraction**: Extract 3-10 main takeaways
- **Discussion Questions**: Auto-generate study questions
- **Sentiment Analysis**: Analyze tone, audience type, and content style
- **Provider Choice**: Use Claude (Anthropic) or GPT-4 (OpenAI)

### 📝 Advanced Text Processing
- **Paragraph Detection**: Smart break detection based on speech pauses
- **Filler Word Removal**: Remove "um", "uh", "like", etc.
- **Capitalization Fix**: Automatic sentence capitalization
- **Punctuation Intelligence**: Smart punctuation placement
- **Keyword Extraction**: Identify top keywords and frequency

### 📊 Rich Metadata & Statistics
- **Extended Metadata**: Title, channel, date, duration, views, likes, tags, chapters
- **Chapter Support**: Auto-generate table of contents from video chapters
- **Statistics**: Word count, character count, reading time, speaking rate
- **Keyword Analysis**: Extract and display most common words

### 🎨 Flexible Formatting
- **Timestamps**: Toggle on/off, clickable links to exact video moments
- **Time Grouping**: Group by 30s, 1min, 2min, 5min, or by chapters
- **Custom Templates**: Include/exclude thumbnail, description, tags, TOC
- **Clean Text**: Remove [Music], [Applause], and other artifacts

### 📤 Export Formats
- **Markdown** (.md): Enhanced with all features, AI summaries, statistics
- **PDF** (.pdf): Professional documents with proper formatting
- **JSON** (.json): Complete data export for further processing

### 🚀 Performance Features
- **Intelligent Caching**: 30-day cache for video info and transcripts
- **Cache Management**: View stats, clear cache from UI
- **Error Recovery**: Robust error handling with helpful messages
- **Progress Bars**: Step-by-step visual progress tracking

## 📦 Installation

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- **FFmpeg** (for audio extraction)
  - Windows: `winget install ffmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### Quick Setup
```bash
# 1. Clone repository
git clone https://github.com/yourusername/YouTube-Notemake.git
cd YouTube-Notemake

# 2. Install dependencies
uv sync

# 3. (Optional) Add API keys for AI features
# Create .env file:
echo "OPENAI_API_KEY=sk-proj-your-key" > .env
# or
echo "ANTHROPIC_API_KEY=sk-ant-your-key" > .env

# 4. Run the app
uv run streamlit run app.py
```

## 🚀 Usage

### Basic Workflow
1. **Enter YouTube URL**
2. **Choose extraction method** (captions or audio)
3. **Configure options** (AI, formatting, export)
4. **Generate** and download

### With AI Features
1. Add API key to `.env` file
2. Enable AI features in the UI
3. Choose summary length and key points
4. Optionally add questions and sentiment analysis

### Example Commands
```bash
# Run the app
uv run streamlit run app.py

# Or use shortcuts
./run.sh      # Mac/Linux
run.bat       # Windows
```

✨ **AI-Powered Summarization**
- Claude (Sonnet 3.5) and GPT-4 support
- Customizable summary length
- Key points extraction
- Discussion questions
- Sentiment analysis

✨ **Advanced Export Options**
- PDF generation with proper formatting
- JSON export for data processing
- Enhanced Markdown with all features

✨ **Text Processing**
- Paragraph detection based on pauses
- Filler word removal
- Capitalization and punctuation fixes
- Keyword extraction

✨ **Performance & Organization**
- Intelligent caching system
- Batch processing support
- Playlist extraction
- Progress bars in UI

✨ **Enhanced Metadata**
- Video tags and categories
- Chapter detection and TOC
- Like count and extended stats
- Speaking rate calculation

### Improvements
- Real-time progress tracking
- Better error messages
- Cache management in UI
- Sidebar with AI status
- Statistics tab in preview

## 📝 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Architecture and design

## 💡 Usage Tips

### Without API Keys (Free)
All features work except AI summarization:
- ✅ Caption extraction
- ✅ Audio transcription (Whisper)
- ✅ All export formats
- ✅ Statistics and analysis
- ✅ Caching and batch processing

### With API Keys (AI Features)
- ✅ Everything above, plus:
- ✅ AI summaries
- ✅ Key points extraction
- ✅ Discussion questions
- ✅ Sentiment analysis

**Cost**: ~$0.01-0.05 per 10-minute video

## 🎯 Use Cases

- **Students**: Convert lectures to searchable notes
- **Researchers**: Extract insights from educational videos
- **Content Creators**: Repurpose video content as blog posts
- **Accessibility**: Create text versions of video content
- **Language Learning**: Get transcripts in multiple languages

## 📚 Project Structure

```
YouTube-Notemake/
├── src/youtube_notemake/
│   ├── youtube_handler.py       # Video metadata & URL parsing
│   ├── transcript.py            # Caption extraction
│   ├── audio_transcriber.py    # Whisper AI transcription
│   ├── text_processor.py       # Text analysis & cleaning
│   ├── ai_summarizer.py        # AI-powered summarization
│   ├── markdown_generator.py   # Markdown formatting
│   ├── exporter.py             # PDF & JSON export
│   ├── cache_manager.py        # Intelligent caching
│   └── batch_processor.py      # Batch & playlist processing
├── app.py                       # Streamlit UI
├── .env.example                 # API key template
├── pyproject.toml              # Dependencies
└── Documentation files
```

## 🔧 Dependencies

- **streamlit**: Web UI framework
- **yt-dlp**: Video metadata & audio download
- **youtube-transcript-api**: Caption extraction
- **openai-whisper**: Speech-to-text (99 languages)
- **torch & torchaudio**: Deep learning for Whisper
- **anthropic**: Claude API (optional)
- **openai**: GPT-4 API (optional)
- **reportlab**: PDF generation
- **python-dotenv**: Environment variable management

## 🐛 Troubleshooting

### Common Issues

**No transcripts available**
- Solution: App automatically switches to audio extraction mode

**FFmpeg not found**
- Install FFmpeg: See installation instructions above
- Verify: `ffmpeg -version`

**Out of memory (Whisper)**
- Use smaller model (tiny or base)
- Close other applications
- Process shorter videos

**AI features not working**
- Check API key in `.env` file
- Verify correct format: `OPENAI_API_KEY=sk-proj-...`
- See [API_SETUP.md](API_SETUP.md) for help

**PDF export fails**
- Install reportlab: `uv sync`
- Check permissions in output directory

## 📈 Performance

### Caption Mode
- Speed: < 5 seconds
- Cost: Free
- Accuracy: Depends on YouTube captions

### Audio Mode (Whisper)
| Model | Speed (10min video) | RAM | Accuracy |
|-------|---------------------|-----|----------|
| tiny | ~20s | 1GB | 85% |
| base | ~40s | 1GB | 92% ⭐ |
| small | ~2min | 2GB | 95% |
| medium | ~5min | 5GB | 97% |
| large | ~10min | 10GB | 99% |

### AI Summarization
- Claude Sonnet 3.5: ~$0.01-0.03 per video
- GPT-4 Turbo: ~$0.01-0.05 per video
- Processing time: 5-15 seconds



## 📄 License

MIT License - Free to use, modify, and distribute

## Acknowledgments

- OpenAI Whisper for speech-to-text
- yt-dlp for video handling
- Streamlit for the amazing UI framework
- Anthropic & OpenAI for AI capabilities

---
