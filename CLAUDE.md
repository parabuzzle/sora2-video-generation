# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a video generation project that uses OpenAI's Sora 2 API to generate videos from markdown prompt files with optional audio overlay.

## Environment Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Configure `.env` with:
- `OPENAI_API_KEY`: OpenAI API key for Sora 2 API access

Optional: Install `ffmpeg` for audio overlay functionality

## Usage

Generate a new video:
```bash
python3 generate.py --promptfile prompts/simple_example.md

# Optionally override model from prompt file
python3 generate.py --promptfile prompts/simple_example.md --model sora-2-pro
```

Retrieve an existing video by job ID (if interrupted or failed):
```bash
python3 generate.py --retrieve <job_id>
```

Delete a video from OpenAI storage:
```bash
python3 generate.py --delete <job_id>
```

List all videos in OpenAI storage:
```bash
python3 generate.py --list
```

Job IDs are saved to `.sora_jobs` file automatically. Videos are stored for 15 days before automatic deletion.

## Architecture

### Core Components

**generate.py** - Main script with these key functions:

1. **parse_markdown_prompt(file_path)**: Parses markdown files to extract:
   - Prompt text from `## Prompt` section
   - Model, duration, and orientation from `## Video Settings` table
   - Optional input reference image from `## Input Reference` section (for image-to-video)
   - Optional camera/shot metadata from `## Camera` section
   - Optional lighting/palette from `## Lighting` section
   - Optional dialogue from `## Dialogue` section
   - Optional audio file path from `## Audio` section

2. **get_resolution(orientation)**: Maps orientation strings to Sora resolution format:
   - landscape → 1280x720
   - portrait → 720x1280
   - square → 1080x1080

3. **build_enhanced_prompt(base_prompt, camera, lighting, dialogue)**: Builds enhanced prompt following Sora's recommended structure:
   - Combines base prompt with camera metadata
   - Adds lighting and palette information
   - Separates dialogue block from visual description

4. **map_duration_to_valid(duration, model)**: Maps requested duration to nearest valid value:
   - Both models: 4, 8, or 12 seconds

5. **generate_video(client, prompt, duration, resolution, model, input_reference)**: Submits video generation request to Sora API using `client.videos.create()`. Supports image-to-video mode via input_reference parameter

6. **poll_job_status(client, job_id, poll_interval)**: Polls job status every 10 seconds until completion or failure. Recognizes valid statuses: 'pending', 'processing', 'queued', 'in_progress', 'completed', 'failed'

7. **download_video(client, job, output_dir)**: Downloads completed video to `output/` directory with timestamp

8. **overlay_audio(video_path, audio_path)**: Uses ffmpeg to overlay audio on generated video (optional)

9. **save_job_id(job_id, prompt_file)**: Saves job ID to `.sora_jobs` file with timestamp for recovery

10. **retrieve_video_by_id(job_id)**: Retrieves and downloads video by job ID, handling all statuses including in-progress jobs

11. **delete_video_by_id(job_id)**: Deletes video from OpenAI storage using `client.videos.delete()`

12. **list_videos()**: Lists all videos in OpenAI storage using `client.videos.list()`, displaying job ID, status, duration, resolution, creation timestamp, and progress for in-progress videos

### Data Flow

**Generate Mode:**
1. Parse markdown prompt file → extract metadata
2. Initialize OpenAI client with API key
3. Submit video generation job to Sora 2 API
4. Save job ID to `.sora_jobs` file for recovery
5. Poll job status until completed
6. Download video from returned URL
7. If audio specified: overlay using ffmpeg
8. Save final output to `output/` directory

**Retrieve Mode:**
1. Initialize OpenAI client with API key
2. Retrieve job status by ID
3. If completed: download immediately
4. If in-progress: poll until completion, then download
5. Save video to `output/` directory

**Delete Mode:**
1. Initialize OpenAI client with API key
2. Retrieve job to verify it exists
3. Delete video from OpenAI storage
4. Videos cannot be recovered after deletion

**List Mode:**
1. Initialize OpenAI client with API key
2. Retrieve all videos using `client.videos.list()`
3. Display formatted table with video details
4. Show progress for in-progress videos
5. Display total count of videos

### Prompt File Structure

Markdown files in `prompts/` directory contain:

**Required Sections:**
- `## Prompt`: Video description text
- `## Video Settings`: Table with model, duration, and orientation
  - model: sora-2 or sora-2-pro (defaults to sora-2)
  - duration: requested duration in seconds
  - orientation: landscape, portrait, or square

**Optional Advanced Sections:**
- `## Input Reference (optional)`: Path to single image file for image-to-video mode (anchors first frame, must match target resolution)
- `## Camera (optional)`: Shot type, lens specs (e.g., 85mm), aperture (f-stop), camera movement
- `## Lighting (optional)`: Time of day, lighting style, color palette description
- `## Dialogue (optional)`: Spoken lines (separated from visual description for better results)
- `## Audio (optional)`: Path to audio file for post-processing overlay

**Notes:**
- Model can be overridden via `--model` CLI argument
- Input Reference enables image-to-video generation
- Camera, Lighting, and Dialogue are automatically formatted into enhanced prompt structure
- See `prompts/advanced_example.md` for full example

### API Models

**sora-2** (standard): 4, 8, or 12 seconds
**sora-2-pro** (professional): 4, 8, or 12 seconds (higher quality, same duration options)

The `map_duration_to_valid()` function maps requested durations to the nearest valid value. Despite web app supporting longer durations, the API currently limits both models to 4/8/12 seconds.

### Important Limitations

- **No job cancellation**: Once submitted, jobs cannot be cancelled and will be billed
- **Video storage**: Videos are stored for 15 days before automatic deletion
- **Delete vs Cancel**: The delete operation removes completed videos from storage, but does not cancel in-progress jobs
