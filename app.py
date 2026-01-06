"""Streamlit UI for YouTube Notemake with all advanced features."""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.youtube_notemake.youtube_handler import YouTubeHandler
from src.youtube_notemake.transcript import TranscriptExtractor
from src.youtube_notemake.markdown_generator import MarkdownGenerator
from src.youtube_notemake.audio_transcriber import AudioTranscriber
from src.youtube_notemake.text_processor import TextProcessor
from src.youtube_notemake.ai_summarizer import AISummarizer
from src.youtube_notemake.exporter import Exporter
from src.youtube_notemake.cache_manager import CacheManager


def main():
    st.set_page_config(
        page_title="YouTube Notemake v0.2.0",
        page_icon="📝",
        layout="wide"
    )

    st.title("📝 YouTube Notemake v0.2.0")
    st.markdown("Extract transcripts from YouTube videos with AI-powered features!")

    # Initialize cache manager
    cache = CacheManager()

    # Check for AI capabilities
    has_claude = AISummarizer.check_api_key("claude")
    has_openai = AISummarizer.check_api_key("openai")
    has_ai = has_claude or has_openai

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # AI Status
        st.subheader("🤖 AI Features")
        if has_ai:
            provider = st.radio(
                "AI Provider",
                ["claude", "openai"] if has_claude and has_openai else
                (["claude"] if has_claude else ["openai"]),
                help="Choose which AI to use for summarization"
            )
            st.success(f"✅ {provider.title()} API available")
        else:
            st.warning("⚠️ No AI API keys found")
            st.info("Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env file for AI features")

        # Cache info
        st.subheader("💾 Cache")
        cache_stats = cache.get_cache_stats()
        st.text(f"Videos: {cache_stats['video_info_count']}")
        st.text(f"Transcripts: {cache_stats['transcript_count']}")
        st.text(f"Size: {cache_stats['total_size_mb']} MB")

        if st.button("Clear Cache"):
            deleted = cache.clear_cache("all")
            st.success(f"Deleted {deleted} files")
            st.rerun()

    # Main content
    st.header("1️⃣ Enter YouTube URL")
    url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    if url:
        if not YouTubeHandler.validate_url(url):
            st.error("❌ Invalid YouTube URL")
            return

        video_id = YouTubeHandler.extract_video_id(url)
        st.success(f"✅ Video ID: `{video_id}`")

        # Fetch video info (with caching)
        with st.spinner("Fetching video information..."):
            try:
                video_info = cache.get_cached_video_info(video_id)
                if not video_info:
                    video_info = YouTubeHandler.get_video_info(url)
                    cache.cache_video_info(video_id, video_info)
                else:
                    st.info("📦 Loaded from cache")

                st.session_state['video_info'] = video_info
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return

        # Display video info
        st.header("2️⃣ Video Information")

        col1, col2 = st.columns([1, 2])

        with col1:
            if video_info.get('thumbnail'):
                st.image(video_info['thumbnail'], use_container_width=True)

        with col2:
            st.markdown(f"**Title:** {video_info['title']}")
            st.markdown(f"**Channel:** {video_info['channel']}")
            st.markdown(f"**Upload Date:** {video_info.get('upload_date', 'Unknown')}")

            if video_info.get('duration'):
                duration_str = YouTubeHandler.format_duration(video_info['duration'])
                st.markdown(f"**Duration:** {duration_str}")

            if video_info.get('view_count'):
                st.markdown(f"**Views:** {video_info['view_count']:,}")

            if video_info.get('like_count'):
                st.markdown(f"**Likes:** {video_info['like_count']:,}")

            # Show tags if available
            if video_info.get('tags'):
                with st.expander("🏷️ Tags"):
                    st.write(", ".join(video_info['tags'][:20]))

            # Show chapters if available
            if video_info.get('chapters'):
                with st.expander(f"📑 Chapters ({len(video_info['chapters'])})"):
                    for chapter in video_info['chapters']:
                        timestamp = YouTubeHandler.format_duration(int(chapter['start_time']))
                        st.text(f"{timestamp} - {chapter['title']}")

        # Transcript Method Selection
        st.header("3️⃣ Select Transcript Method")

        with st.spinner("Checking available transcripts..."):
            try:
                available_transcripts, has_transcripts = TranscriptExtractor.get_available_transcripts(video_id)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return

        use_audio_extraction = False
        selected_lang_code = None
        whisper_model = "base"

        if has_transcripts:
            st.success(f"✅ Found {len(available_transcripts)} transcript(s)")

            transcript_options = []
            for t in available_transcripts:
                generated = " (Auto-generated)" if t['is_generated'] else ""
                transcript_options.append(f"{t['language']} ({t['language_code']}){generated}")

            transcript_options.append("🎤 Use Audio Extraction (Whisper AI)")

            selected_transcript = st.selectbox(
                "Select transcript source",
                range(len(transcript_options)),
                format_func=lambda x: transcript_options[x]
            )

            if selected_transcript == len(transcript_options) - 1:
                use_audio_extraction = True
            else:
                selected_lang_code = available_transcripts[selected_transcript]['language_code']
        else:
            st.warning("⚠️ No captions available")
            st.info("Using Audio Extraction with Whisper AI")
            use_audio_extraction = True

        # Audio extraction options
        if use_audio_extraction:
            st.markdown("### 🎤 Audio Extraction Settings")

            col1, col2 = st.columns(2)

            with col1:
                models = AudioTranscriber.get_available_models()
                model_names = [m['name'] for m in models]
                model_descriptions = [f"{m['name']}: {m['description']}" for m in models]

                selected_model_idx = st.selectbox(
                    "Whisper Model",
                    range(len(models)),
                    index=1,
                    format_func=lambda x: model_descriptions[x]
                )
                whisper_model = model_names[selected_model_idx]

            with col2:
                audio_language = st.text_input(
                    "Language code (optional)",
                    placeholder="Auto-detect if empty"
                )
                audio_task = st.radio("Task", ["transcribe", "translate"])

            st.warning("⏱️ Audio extraction may take several minutes")

        # Advanced Options
        st.header("4️⃣ Advanced Options")

        tab1, tab2, tab3, tab4 = st.tabs(["📝 Format", "🎯 AI Features", "📊 Export", "🔧 Processing"])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                include_timestamps = st.checkbox("Include timestamps", value=True)
                clickable_timestamps = st.checkbox(
                    "Clickable timestamps",
                    value=True,
                    disabled=not include_timestamps
                )
                include_thumbnail = st.checkbox("Include thumbnail", value=True)
                include_description = st.checkbox("Include video description", value=False)

            with col2:
                include_tags = st.checkbox("Include tags", value=False)
                include_statistics = st.checkbox("Include statistics", value=True)
                include_toc = st.checkbox("Include table of contents", value=True)
                clean_text = st.checkbox("Clean text", value=True)

            group_options = {
                "No grouping": 0,
                "Group by 30 seconds": 30,
                "Group by 1 minute": 60,
                "Group by 2 minutes": 120,
                "Group by 5 minutes": 300,
            }
            group_by = st.selectbox("Transcript grouping", list(group_options.keys()))
            group_by_time = group_options[group_by]

        with tab2:
            if has_ai:
                enable_ai_summary = st.checkbox("🤖 Generate AI Summary", value=True)

                if enable_ai_summary:
                    col1, col2 = st.columns(2)

                    with col1:
                        summary_length = st.slider("Summary length (words)", 100, 500, 300, 50)
                        num_key_points = st.slider("Number of key points", 3, 10, 5)

                    with col2:
                        generate_questions = st.checkbox("Generate discussion questions", value=False)
                        if generate_questions:
                            num_questions = st.slider("Number of questions", 3, 10, 5)
                        else:
                            num_questions = 0

                        analyze_sentiment = st.checkbox("Analyze sentiment & tone", value=False)
            else:
                st.info("💡 Add API keys to enable AI features (see sidebar)")
                enable_ai_summary = False
                generate_questions = False
                analyze_sentiment = False

        with tab3:
            export_formats = st.multiselect(
                "Export formats",
                ["Markdown", "PDF", "JSON"],
                default=["Markdown"]
            )

        with tab4:
            col1, col2 = st.columns(2)

            with col1:
                use_paragraph_detection = st.checkbox("Detect paragraphs", value=True)
                if use_paragraph_detection:
                    min_pause = st.slider("Min pause for paragraph (seconds)", 1.0, 5.0, 2.0, 0.5)
                else:
                    min_pause = 2.0

                remove_fillers = st.checkbox("Remove filler words", value=False)

            with col2:
                fix_capitalization = st.checkbox("Fix capitalization", value=False)
                improve_punctuation = st.checkbox("Improve punctuation", value=False)

        # Output Settings
        st.header("5️⃣ Output Settings")

        col1, col2 = st.columns(2)

        with col1:
            output_dir = st.text_input("Output directory", value="output")

        with col2:
            filename = st.text_input(
                "Filename (without extension)",
                value=MarkdownGenerator.sanitize_filename(video_info['title'])
            )

        # Generate Button
        st.header("6️⃣ Generate")

        if st.button("🚀 Generate Transcript", type="primary", use_container_width=True):
            # Create progress bar
            progress_text = st.empty()
            progress_bar = st.progress(0)

            total_steps = 6
            current_step = 0

            transcript = None

            # Step 1: Get transcript
            current_step += 1
            progress_bar.progress(current_step / total_steps)

            if use_audio_extraction:
                progress_text.text(f"⏳ Step {current_step}/{total_steps}: Transcribing with Whisper ({whisper_model})...")
                try:
                    transcriber = AudioTranscriber(model_size=whisper_model)
                    result = transcriber.transcribe_youtube_video(
                        url,
                        language=audio_language if audio_language else None,
                        task=audio_task,
                        keep_audio=False
                    )
                    transcript = AudioTranscriber.convert_whisper_to_transcript_format(result['segments'])
                    st.success(f"✅ Transcribed! Language: {result['language']}")
                except Exception as e:
                    progress_text.empty()
                    progress_bar.empty()
                    st.error(f"❌ Error: {str(e)}")
                    return
            else:
                progress_text.text(f"⏳ Step {current_step}/{total_steps}: Fetching transcript...")
                cached_transcript = cache.get_cached_transcript(video_id, selected_lang_code)

                if cached_transcript:
                    st.info("📦 Using cached transcript")
                    transcript = cached_transcript
                else:
                    try:
                        transcript = TranscriptExtractor.get_transcript(video_id, language=selected_lang_code)
                        cache.cache_transcript(video_id, selected_lang_code, transcript)
                    except Exception as e:
                        progress_text.empty()
                        progress_bar.empty()
                        st.error(f"❌ Error: {str(e)}")
                        return

            # Step 2: Process transcript
            current_step += 1
            progress_bar.progress(current_step / total_steps)
            progress_text.text(f"⏳ Step {current_step}/{total_steps}: Processing transcript...")

            # Paragraph detection
            if use_paragraph_detection:
                transcript = TextProcessor.detect_paragraphs(transcript, min_pause)

            # Get full text
            full_text = TranscriptExtractor.get_full_text(transcript)

            # Text cleaning
            if clean_text:
                full_text = TranscriptExtractor.clean_text(full_text)

            if remove_fillers:
                full_text = TextProcessor.remove_filler_words(full_text)

            if fix_capitalization:
                full_text = TextProcessor.fix_capitalization(full_text)

            if improve_punctuation:
                full_text = TextProcessor.add_punctuation_intelligence(full_text)

            # Calculate statistics
            statistics = TextProcessor.calculate_statistics(
                full_text,
                video_info.get('duration')
            )

            st.success(f"📊 {statistics['word_count']:,} words, ~{statistics['reading_time_minutes']['average']} min read")

            # Step 3: AI Processing
            current_step += 1
            progress_bar.progress(current_step / total_steps)

            ai_summary = None
            if enable_ai_summary and has_ai:
                progress_text.text(f"⏳ Step {current_step}/{total_steps}: Generating AI summary with {provider.title()}...")
                try:
                    summarizer = AISummarizer(provider=provider)

                    summary = summarizer.generate_summary(full_text, summary_length)
                    key_points = summarizer.extract_key_points(full_text, num_key_points)

                    ai_summary = {
                        'summary': summary,
                        'key_points': key_points
                    }

                    if generate_questions:
                        questions = summarizer.generate_questions(full_text, num_questions)
                        ai_summary['questions'] = questions

                    if analyze_sentiment:
                        sentiment = summarizer.analyze_sentiment_and_tone(full_text)
                        ai_summary['sentiment'] = sentiment

                    st.success("✅ AI analysis complete!")

                    # Show preview
                    with st.expander("👀 Preview AI Summary"):
                        st.markdown(f"**Summary:** {summary}")
                        st.markdown("**Key Points:**")
                        for point in key_points:
                            st.markdown(f"- {point}")

                except Exception as e:
                    st.error(f"⚠️ AI summary failed: {str(e)}")
                    ai_summary = None
            else:
                progress_text.text(f"⏳ Step {current_step}/{total_steps}: Skipping AI features...")

            # Step 4: Generate markdown
            current_step += 1
            progress_bar.progress(current_step / total_steps)
            progress_text.text(f"⏳ Step {current_step}/{total_steps}: Generating markdown...")

            options = {
                'include_timestamps': include_timestamps,
                'clickable_timestamps': clickable_timestamps,
                'group_by_time': group_by_time,
                'include_thumbnail': include_thumbnail,
                'include_description': include_description,
                'include_tags': include_tags,
                'include_statistics': include_statistics,
                'include_toc': include_toc,
                'clean_text': clean_text,
            }

            markdown_content = MarkdownGenerator.generate_markdown(
                video_info,
                transcript,
                options,
                statistics,
                ai_summary
            )

            # Step 5: Export to various formats
            current_step += 1
            progress_bar.progress(current_step / total_steps)
            progress_text.text(f"⏳ Step {current_step}/{total_steps}: Exporting files...")

            exported_files = []

            if "Markdown" in export_formats:
                md_path = MarkdownGenerator.save_markdown(markdown_content, output_dir, filename)
                exported_files.append(("Markdown", md_path))

            if "PDF" in export_formats:
                try:
                    pdf_path = Exporter.export_to_pdf(
                        video_info,
                        transcript,
                        statistics,
                        ai_summary,
                        f"{output_dir}/{filename}.pdf",
                        include_timestamps
                    )
                    exported_files.append(("PDF", pdf_path))
                except Exception as e:
                    st.warning(f"PDF export failed: {str(e)}")

            if "JSON" in export_formats:
                try:
                    json_path = Exporter.export_to_json(
                        video_info,
                        transcript,
                        statistics,
                        ai_summary,
                        f"{output_dir}/{filename}.json"
                    )
                    exported_files.append(("JSON", json_path))
                except Exception as e:
                    st.warning(f"JSON export failed: {str(e)}")

            # Step 6: Complete
            current_step += 1
            progress_bar.progress(1.0)
            progress_text.text(f"✅ Step {current_step}/{total_steps}: Complete!")

            import time
            time.sleep(0.5)
            progress_text.empty()
            progress_bar.empty()

            # Success message
            st.success("✅ Generation complete!")

            for format_name, file_path in exported_files:
                st.info(f"📁 {format_name}: `{file_path}`")

            # Preview & Download
            st.header("📄 Preview & Download")

            preview_tab, download_tab, stats_tab = st.tabs(["Preview", "Download", "Statistics"])

            with preview_tab:
                st.markdown(markdown_content)

            with download_tab:
                st.download_button(
                    label="⬇️ Download Markdown",
                    data=markdown_content,
                    file_name=f"{filename}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

                with st.expander("View raw markdown"):
                    st.code(markdown_content, language="markdown")

            with stats_tab:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Word Count", f"{statistics['word_count']:,}")
                    st.metric("Characters", f"{statistics['character_count']:,}")

                with col2:
                    st.metric("Sentences", statistics['sentence_count'])
                    st.metric("Reading Time", f"{statistics['reading_time_minutes']['average']} min")

                with col3:
                    if 'speaking_rate_wpm' in statistics:
                        st.metric("Speaking Rate", f"{statistics['speaking_rate_wpm']} wpm")

                    # Extract keywords
                    keywords = TextProcessor.extract_keywords(full_text, top_n=10)
                    st.markdown("**Top Keywords:**")
                    for word, count in keywords[:5]:
                        st.text(f"{word}: {count}")

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### YouTube Notemake v0.2.0")
    st.sidebar.markdown("**Features:**")
    st.sidebar.markdown("- Caption & Audio extraction")
    st.sidebar.markdown("- AI summarization")
    st.sidebar.markdown("- Multiple export formats")
    st.sidebar.markdown("- Smart caching")


if __name__ == "__main__":
    main()
