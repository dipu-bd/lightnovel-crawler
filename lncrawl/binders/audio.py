import logging
import os
import asyncio
import time
import re
from typing import Dict, List
from pathlib import Path

from ..models.chapter import Chapter
from ..core.taskman import TaskManager

logger = logging.getLogger(__name__)

try:
    import edge_tts
except ImportError:
    logging.fatal("Failed to import edge-tts")

async def list_available_voices(language: str):
    """Get a list of available voices from edge-tts"""

    voices = await edge_tts.list_voices()
    filtered_voices = [voice for voice in voices if voice["Locale"].startswith(language)]
    
    if not filtered_voices:
        logger.warning(f"No voices found for language '{language}', defaulting to English")
        filtered_voices = [voice for voice in voices if voice["Locale"].startswith("en")]
    
    return filtered_voices

async def monitor_audio_progress(output_file: str, total_chars: int, bar, rate: str) -> None:
    """
    Monitor the audio generation progress by checking file size.

    To be honest, this is not very (at all) accurate, its more just to 
    show the user that the audio is being generated. and that it's not frozen.

    If you know a better way to do this, feel free to improve this.
    """

    # Convert rate string (e.g. "+25%", "-50%") to multiplier
    rate_multiplier = 1.0
    if rate:
        try:
            rate_value = float(rate.strip('%+'))
            if rate.startswith('-'):
                rate_multiplier = 1 - (rate_value / 100)
            else:
                rate_multiplier = 1 + (rate_value / 100)
        except ValueError:
            logger.warning("Invalid rate format: %s, using default rate", rate)

    base_size = total_chars * 400
    estimated_size = base_size / rate_multiplier
    
    while True:
        if os.path.exists(output_file):
            current_size = os.path.getsize(output_file)
            progress = min(100, (current_size / estimated_size) * 100)
            bar.n = int(progress)
            bar.refresh()
            
            # Check if file size has stopped growing for 2 seconds, if it has, we can assume the audio is done.
            last_size = current_size
            await asyncio.sleep(2)
            if os.path.exists(output_file):
                current_size = os.path.getsize(output_file)
                if current_size == last_size:
                    bar.n = 100
                    bar.refresh()
                    break
        await asyncio.sleep(0.5)

async def generate_audio(
    chapter_groups: List[List[Chapter]],  # chapters grouped by volumes
    images: List[str],  # full path of images to add
    book_title: str,
    novel_author: str,
    output_path: str,
    book_cover: str,
    novel_title: str,
    novel_url: str,
    novel_synopsis: str,
    novel_tags: list,
    good_file_name: str,
    suffix: str,  # suffix to the file name
    no_suffix_after_filename: bool = False,
    is_rtl: bool = False,
    language: str = "en",
    voice: str = "en-US-GuyNeural",  # default voice
    rate: str = "+0%",  # default rate
):
    """Generate audio from text using edge-tts"""

    logger.info("Generating audio for %s", book_title)
    logger.debug("Using voice: %s at rate: %s", voice, rate)
    
    # Create output directory
    mp3_path = os.path.join(output_path, "mp3")
    os.makedirs(mp3_path, exist_ok=True)
    
    # Generate filename
    file_name = good_file_name
    if not no_suffix_after_filename:
        file_name += " " + suffix
    output_file = os.path.join(mp3_path, f"{file_name}.mp3")
    
    # Combine all chapter text
    logger.debug("Generating audio")
    all_text = []
    total_chapters = sum(len(chapters) for chapters in chapter_groups)
    
    # Create a task manager for progress bar
    taskman = TaskManager()
    bar = taskman.progress_bar(
        total=100,  # We'll use percentage for audio generation
        desc="Generating audio",
        unit="%"
    )
    
    for chapters in chapter_groups:
        for chapter in chapters:
            logger.debug("Processing chapter: %s", chapter.title)
            
            text = chapter.body.replace("</p><p", "</p>\n<p")
            text = text.replace("<p>", "").replace("</p>", "\n")
            text = text.replace("<br>", "\n").replace("<br/>", "\n")
            
            # Additional cleaning for text-to-speech
            text = re.sub(r'<[^>]+>', '', text)  # Remove any remaining HTML tags
            text = re.sub(r'&[^;]+;', '', text)  # Remove HTML entities
            text = text.strip()
            
            all_text.append(f"Chapter {chapter.id}: {chapter.title}\n{text}\n")
    
    full_text = "\n".join(all_text)
    total_chars = len(full_text)
    
    logger.info("Starting audio generation")
    communicate = edge_tts.Communicate(full_text, voice, rate=rate)
    
    # Start progress monitoring in background
    monitor_task = asyncio.create_task(
        monitor_audio_progress(output_file, total_chars, bar, rate)
    )
    
    logger.debug("Saving audio file to %s", output_file)
    await communicate.save(output_file)
    
    # Wait for monitoring to complete
    await monitor_task
    
    bar.n = 100
    bar.refresh()
    bar.close()
    
    logger.info("Created: %s", output_file)
    print("Created: %s.mp3" % file_name)
    return output_file

def make_mp3s(app, data: Dict[str, List[Chapter]]) -> List[str]:
    from ..core.app import App
    assert isinstance(app, App)
    mp3_files = []

    # Get voice and rate selection first
    logger.info("Fetching available voices")
    voices = asyncio.run(list_available_voices(app.crawler.language))
    voice_choices = [f"{v['ShortName']} ({v['Gender']})" for v in voices]
    
    from questionary import prompt
    answer = prompt([
        {
            'type': 'list',
            'name': 'voice',
            'message': 'Select a voice for the audio:',
            'choices': voice_choices,
        },
        {
            'type': 'list',
            'name': 'rate',
            'message': 'Select speaking rate:',
            'choices': [
                'Very Slow (-50%)',
                'Slow (-25%)',
                'Normal (0%)',
                'Fast (+25%)',
                'Very Fast (+50%)'
            ],
        }
    ])
    
    selected_voice = voices[voice_choices.index(answer['voice'])]['Name']
    rate_map = {
        'Very Slow (-50%)': '-50%',
        'Slow (-25%)': '-25%',
        'Normal (0%)': '+0%',
        'Fast (+25%)': '+25%',
        'Very Fast (+50%)': '+50%'
    }
    selected_rate = rate_map[answer['rate']]

    # Process each volume
    total_volumes = len(data)
    for i, (volume, chapters) in enumerate(data.items(), 1):
        if not chapters:
            continue

        logger.info("Processing volume %d/%d: %s", i, total_volumes, volume)
        app.progress = (i - 1) * 100 / total_volumes

        book_title = (app.crawler.novel_title + " " + volume).strip()
        volumes: Dict[int, List[Chapter]] = {}
        for chapter in chapters:
            suffix = chapter.volume or 1
            volumes.setdefault(suffix, []).append(chapter)
        
        images = []
        image_path = os.path.join(app.output_path, "images")
        if os.path.isdir(image_path):
            images = {
                os.path.join(image_path, filename)
                for filename in os.listdir(image_path)
                if filename.endswith(".jpg")
            }
        # Display warning about long processing time
        print("\n⚠️  WARNING: ⚠️")
        print("  MP3 generation can take a VERY long time. Please be")
        print("  patient as the process cannot be paused once started.\n")

        output = asyncio.run(generate_audio(
            chapter_groups=list(volumes.values()),
            images=images,
            suffix=volume,
            book_title=book_title,
            novel_title=app.crawler.novel_title,
            novel_author=app.crawler.novel_author or app.crawler.home_url,
            novel_url=app.crawler.novel_url,
            novel_synopsis=app.crawler.novel_synopsis,
            language=app.crawler.language,
            novel_tags=app.crawler.novel_tags,
            output_path=app.output_path,
            book_cover=app.book_cover,
            good_file_name=app.good_file_name,
            no_suffix_after_filename=app.no_suffix_after_filename,
            voice=selected_voice,
            rate=selected_rate,
        ))
        if output:
            mp3_files.append(output)

    app.progress = 100
    logger.info("Audio generation completed")
    return mp3_files