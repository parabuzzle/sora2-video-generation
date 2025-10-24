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
python3 generate.py --promptfile prompts/testing.md

# Or specify model via CLI (overrides prompt file)
python3 generate.py --promptfile prompts/testing.md --model sora-2-pro
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
   - Optional audio file path from `## Audio` section
   - Optional inspiration image from `## Inspiration Image` section

2. **get_resolution(orientation)**: Maps orientation strings to Sora resolution format:
   - landscape → 1280x720
   - portrait → 720x1280
   - square → 1080x1080

3. **map_duration_to_valid(duration, model)**: Maps requested duration to nearest valid value for the selected model:
   - sora-2: 4, 8, or 12 seconds
   - sora-2-pro: 10, 15, or 25 seconds

4. **generate_video(client, prompt, duration, resolution, model)**: Submits video generation request to Sora API using `client.videos.create()` with the specified model

5. **poll_job_status(client, job_id, poll_interval)**: Polls job status every 10 seconds until completion or failure. Recognizes valid statuses: 'pending', 'processing', 'queued', 'in_progress', 'completed', 'failed'

6. **download_video(client, job, output_dir)**: Downloads completed video to `output/` directory with timestamp

7. **overlay_audio(video_path, audio_path)**: Uses ffmpeg to overlay audio on generated video (optional)

8. **save_job_id(job_id, prompt_file)**: Saves job ID to `.sora_jobs` file with timestamp for recovery

9. **retrieve_video_by_id(job_id)**: Retrieves and downloads video by job ID, handling all statuses including in-progress jobs

10. **delete_video_by_id(job_id)**: Deletes video from OpenAI storage using `client.videos.delete()`

11. **list_videos()**: Lists all videos in OpenAI storage using `client.videos.list()`, displaying job ID, status, duration, resolution, creation timestamp, and progress for in-progress videos

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
- `## Prompt`: Video description text (required)
- `## Video Settings`: Table with model, duration, and orientation (required)
  - model: sora-2 or sora-2-pro (defaults to sora-2)
  - duration: requested duration in seconds
  - orientation: landscape, portrait, or square
- `## Audio (optional)`: Path to audio file or "None"
- `## Inspiration Image (optional)`: Path to reference image or "None"

Note: Audio and inspiration images are embedded in the prompt file, not passed as CLI arguments. Model can be overridden via `--model` CLI argument.

### API Models

**sora-2** (standard): 4, 8, or 12 seconds
**sora-2-pro** (professional): 10, 15, or 25 seconds

The `map_duration_to_valid()` function maps requested durations to the nearest valid value for the selected model.

### Important Limitations

- **No job cancellation**: Once submitted, jobs cannot be cancelled and will be billed
- **Video storage**: Videos are stored for 15 days before automatic deletion
- **Delete vs Cancel**: The delete operation removes completed videos from storage, but does not cancel in-progress jobs
