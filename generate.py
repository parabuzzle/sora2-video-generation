#!/usr/bin/env python3
"""
Video generation script using OpenAI Sora API.
Parses markdown prompt files and generates videos.
"""

import argparse
import os
import re
import time
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Orientation to resolution mapping
ORIENTATION_MAP = {
    'landscape': '1280x720',
    'portrait': '720x1280',
    'square': '1080x1080'
}


def parse_markdown_prompt(file_path):
    """Parse the markdown prompt file and extract all relevant sections."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract sections using regex
    sections = {}

    # Extract prompt text (between ## Prompt and next ##)
    prompt_match = re.search(r'## Prompt\s*\n\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if prompt_match:
        sections['prompt'] = prompt_match.group(1).strip()
    else:
        raise ValueError("No '## Prompt' section found in the markdown file")

    # Extract video settings from table
    duration_match = re.search(r'\|\s*duration\s*\|\s*(\d+)\s*seconds?\s*\|', content, re.IGNORECASE)
    if duration_match:
        sections['duration'] = int(duration_match.group(1))
    else:
        sections['duration'] = 10  # Default duration

    orientation_match = re.search(r'\|\s*orientation\s*\|\s*(\w+)\s*\|', content, re.IGNORECASE)
    if orientation_match:
        sections['orientation'] = orientation_match.group(1).strip().lower()
    else:
        sections['orientation'] = 'landscape'  # Default orientation

    # Extract model (optional)
    model_match = re.search(r'\|\s*model\s*\|\s*([\w-]+)\s*\|', content, re.IGNORECASE)
    if model_match:
        sections['model'] = model_match.group(1).strip().lower()
    else:
        sections['model'] = 'sora-2'  # Default model

    # Extract audio file (optional)
    audio_match = re.search(r'## Audio.*?\n\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if audio_match:
        audio_text = audio_match.group(1).strip()
        sections['audio'] = None if audio_text.lower() == 'none' else audio_text
    else:
        sections['audio'] = None

    # Extract inspiration image (optional)
    image_match = re.search(r'## Inspiration Image.*?\n\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if image_match:
        image_text = image_match.group(1).strip()
        sections['inspiration_image'] = None if image_text.lower() == 'none' else image_text
    else:
        sections['inspiration_image'] = None

    return sections


def get_resolution(orientation):
    """Convert orientation to resolution string."""
    return ORIENTATION_MAP.get(orientation, '1280x720')


def map_duration_to_valid(duration, model='sora-2'):
    """
    Map requested duration to nearest valid Sora API duration.
    Valid durations depend on model:
    - sora-2: '4', '8', '12' seconds
    - sora-2-pro: '10', '15', '25' seconds
    """
    if model == 'sora-2-pro':
        valid_durations = [10, 15, 25]
    else:  # sora-2
        valid_durations = [4, 8, 12]

    # Find closest valid duration
    closest = min(valid_durations, key=lambda x: abs(x - duration))

    if closest != duration:
        print(f"  Note: Requested {duration}s, using closest valid duration for {model}: {closest}s")

    return str(closest)


def generate_video(client, prompt, duration, resolution, model='sora-2'):
    """
    Submit video generation request to Sora API.
    Returns the job response.
    """
    print(f"\nSubmitting video generation request...")
    print(f"  Model: {model}")
    print(f"  Duration: {duration} seconds")
    print(f"  Resolution: {resolution}")
    print(f"  Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"  Prompt: {prompt}")

    try:
        # Map duration to valid API value for the selected model
        valid_duration = map_duration_to_valid(duration, model)

        response = client.videos.create(
            model=model,
            prompt=prompt,
            seconds=valid_duration,
            size=resolution
        )
        return response
    except Exception as e:
        print(f"Error submitting video generation: {e}")
        sys.exit(1)


def poll_job_status(client, job_id, poll_interval=10):
    """
    Poll the job status until completion.
    Returns the completed job response.
    """
    print(f"\nPolling job status (ID: {job_id})...")

    while True:
        try:
            job = client.videos.retrieve(job_id)
            status = job.status

            print(f"  Status: {status}")

            if status == 'completed':
                print("  Video generation completed!")
                return job
            elif status == 'failed':
                print(f"  Video generation failed: {job.get('error', 'Unknown error')}")
                sys.exit(1)
            elif status in ['pending', 'processing', 'queued', 'in_progress']:
                # Valid processing states - continue waiting
                time.sleep(poll_interval)
            else:
                print(f"  Unknown status: {status}")
                time.sleep(poll_interval)

        except Exception as e:
            print(f"Error polling job status: {e}")
            time.sleep(poll_interval)


def download_video(client, job, output_dir='output'):
    """
    Download the generated video to the output directory.
    Returns the output file path.
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate output filename with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_filename = f"video_{timestamp}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    print(f"\nDownloading video to {output_path}...")

    try:
        # Download video content using OpenAI SDK method
        content = client.videos.download_content(job.id, variant="video")
        content.write_to_file(output_path)

        print(f"  Video saved successfully!")
        return output_path

    except Exception as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)


def overlay_audio(video_path, audio_path):
    """
    Overlay audio on the generated video using ffmpeg.
    Requires ffmpeg to be installed.
    """
    print(f"\nOverlaying audio: {audio_path}")

    # Check if ffmpeg is available
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  Warning: ffmpeg not found. Skipping audio overlay.")
        print("  Install ffmpeg to enable audio overlay: https://ffmpeg.org/download.html")
        return video_path

    # Generate output filename
    video_dir = os.path.dirname(video_path)
    video_name = os.path.basename(video_path)
    name_without_ext = os.path.splitext(video_name)[0]
    output_path = os.path.join(video_dir, f"{name_without_ext}_with_audio.mp4")

    try:
        # Run ffmpeg to overlay audio
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            output_path
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  Audio overlaid successfully!")
        print(f"  Output: {output_path}")

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"  Error overlaying audio: {e.stderr.decode()}")
        return video_path


def save_job_id(job_id, prompt_file=None):
    """Save job ID to a file for recovery."""
    jobs_file = '.sora_jobs'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(jobs_file, 'a') as f:
        f.write(f"{timestamp} | {job_id}")
        if prompt_file:
            f.write(f" | {prompt_file}")
        f.write("\n")

    print(f"\n  Job ID saved to {jobs_file}: {job_id}")


def retrieve_video_by_id(job_id):
    """Retrieve and download a video by job ID."""
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print(f"Retrieving video for job ID: {job_id}")

    # Check job status
    try:
        job = client.videos.retrieve(job_id)
        status = job.status
        print(f"  Current status: {status}")

        if status == 'completed':
            # Download video
            video_path = download_video(client, job)
            print(f"\n{'='*60}")
            print(f"Video retrieved successfully!")
            print(f"Output: {video_path}")
            print(f"{'='*60}")
        elif status == 'failed':
            print(f"  Video generation failed: {job.get('error', 'Unknown error')}")
            sys.exit(1)
        elif status in ['pending', 'processing', 'queued', 'in_progress']:
            print(f"  Video is still processing. Waiting for completion...")
            completed_job = poll_job_status(client, job_id)
            video_path = download_video(client, completed_job)
            print(f"\n{'='*60}")
            print(f"Video retrieved successfully!")
            print(f"Output: {video_path}")
            print(f"{'='*60}")
        else:
            print(f"  Unknown status: {status}")
            sys.exit(1)

    except Exception as e:
        print(f"Error retrieving video: {e}")
        sys.exit(1)


def delete_video_by_id(job_id):
    """Delete a video from OpenAI storage by job ID."""
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print(f"Deleting video with job ID: {job_id}")

    try:
        # Check if video exists first
        job = client.videos.retrieve(job_id)
        print(f"  Current status: {job.status}")

        # Delete the video
        client.videos.delete(job_id)

        print(f"\n{'='*60}")
        print(f"Video deleted successfully!")
        print(f"Job ID: {job_id}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error deleting video: {e}")
        sys.exit(1)


def list_videos():
    """List all videos in OpenAI storage."""
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print("Listing all videos in OpenAI storage...\n")

    try:
        # List videos using the API
        videos = client.videos.list()

        if not videos.data:
            print("No videos found.")
            return

        print(f"{'='*100}")
        print(f"{'Job ID':<50} {'Status':<15} {'Duration':<10} {'Size':<15} {'Created':<20}")
        print(f"{'='*100}")

        for video in videos.data:
            # Format creation timestamp
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video.created_at))

            # Get expiration info if available
            expires_info = ""
            if hasattr(video, 'expires_at') and video.expires_at:
                days_left = (video.expires_at - time.time()) / 86400
                expires_info = f" (expires in {int(days_left)}d)"

            print(f"{video.id:<50} {video.status:<15} {video.seconds}s{'':<7} {video.size:<15} {created_at}")

            # Show progress for in-progress videos
            if hasattr(video, 'progress') and video.progress is not None and video.status in ['queued', 'in_progress']:
                print(f"  └─ Progress: {video.progress}%")

        print(f"{'='*100}")
        print(f"\nTotal videos: {len(videos.data)}")

    except Exception as e:
        print(f"Error listing videos: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate videos using OpenAI Sora API from markdown prompt files.'
    )
    parser.add_argument(
        '--promptfile',
        help='Path to the markdown prompt file'
    )
    parser.add_argument(
        '--retrieve',
        help='Retrieve and download a video by job ID'
    )
    parser.add_argument(
        '--delete',
        help='Delete a video from OpenAI storage by job ID'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all videos in OpenAI storage'
    )
    parser.add_argument(
        '--model',
        choices=['sora-2', 'sora-2-pro'],
        default=None,
        help='Sora model to use (overrides model in prompt file). sora-2: 4/8/12s, sora-2-pro: 10/15/25s'
    )

    args = parser.parse_args()

    # Mode 1: List all videos
    if args.list:
        list_videos()
        return

    # Mode 2: Delete video by job ID
    if args.delete:
        delete_video_by_id(args.delete)
        return

    # Mode 3: Retrieve existing video by job ID
    if args.retrieve:
        retrieve_video_by_id(args.retrieve)
        return

    # Mode 4: Generate new video from prompt file
    if not args.promptfile:
        print("Error: One of --promptfile, --retrieve, --delete, or --list must be specified")
        parser.print_help()
        sys.exit(1)

    # Validate prompt file exists
    if not os.path.exists(args.promptfile):
        print(f"Error: Prompt file not found: {args.promptfile}")
        sys.exit(1)

    # Parse the markdown prompt file
    print(f"Parsing prompt file: {args.promptfile}")
    try:
        sections = parse_markdown_prompt(args.promptfile)
    except Exception as e:
        print(f"Error parsing prompt file: {e}")
        sys.exit(1)

    # Allow CLI --model to override prompt file model
    model = args.model if args.model else sections['model']

    # Display parsed information
    print("\nParsed prompt information:")
    print(f"  Model: {model}")
    print(f"  Duration: {sections['duration']} seconds")
    print(f"  Orientation: {sections['orientation']}")
    print(f"  Audio: {sections['audio'] or 'None'}")
    print(f"  Inspiration Image: {sections['inspiration_image'] or 'None'}")

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Convert orientation to resolution
    resolution = get_resolution(sections['orientation'])

    # Generate video
    job = generate_video(
        client,
        sections['prompt'],
        sections['duration'],
        resolution,
        model
    )

    # Save job ID for recovery
    save_job_id(job.id, args.promptfile)

    # Poll for completion
    completed_job = poll_job_status(client, job.id)

    # Download video
    video_path = download_video(client, completed_job)

    # Overlay audio if specified
    if sections['audio']:
        audio_path = sections['audio']
        if os.path.exists(audio_path):
            video_path = overlay_audio(video_path, audio_path)
        else:
            print(f"\nWarning: Audio file not found: {audio_path}")

    # Log inspiration image (for reference)
    if sections['inspiration_image']:
        print(f"\nNote: Inspiration image referenced: {sections['inspiration_image']}")
        print("  (Logged for reference - not directly used in this generation)")

    print(f"\n{'='*60}")
    print(f"Video generation complete!")
    print(f"Output: {video_path}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
