# Sora Video Generator

A Python CLI tool for generating videos using OpenAI's Sora 2 API. Define your video prompts in simple markdown files and let AI bring them to life.

## Features

- 🎬 Generate videos from markdown prompt files
- 📝 Simple prompt file format with video settings
- 💾 Job recovery system (retrieve videos if interrupted)
- 📊 List and manage all generated videos
- 🔊 Optional audio overlay support (requires ffmpeg)
- ⚡ Supports multiple resolutions and durations

## But Why?

I know, I know, you can just use the sora app or the sora website to generate videos. I also know using the sora app is "free" or if you have a chatGPT paid account you get pro features for "free".

The problem I'm solving here is multi faceted.

1. The Sora app adds watermarks, and sometimes.. you don't want watermarks.
1. The prompts are kinda ephemeral and sometimes you want to save them and all the settings.. why not just codify it?
1. If you want to crate a cohesive sequence, its better to plan it with markdown files
1. more context!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key with Sora 2 API access
- ffmpeg (optional, for audio overlay)

**Cost Warning:** Sora 2 API calls cost approximately $3 per 10-second video. Be mindful of costs when generating videos.

## Setup

1. Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/halloween.git
cd halloween
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:

```bash
cp .env.example .env
```

4. Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

5. (Optional) Install ffmpeg for audio overlay functionality:
   - **macOS:** `brew install ffmpeg`
   - **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

### Generate a new video

Generate a video from a prompt file:

```bash
python3 generate.py --promptfile prompts/simple_example.md
```

You can optionally override the model from the command-line:

```bash
# Override to use sora-2-pro (higher quality)
python3 generate.py --promptfile prompts/simple_example.md --model sora-2-pro
```

The script will:

1. Parse the markdown prompt file
2. Submit video generation request to Sora 2 API
3. Save the job ID to `.sora_jobs` file for recovery
4. Poll for completion
5. Download the generated video to `output/` directory
6. Overlay audio if specified in the prompt file (requires ffmpeg)

### Retrieve an existing video

If the script is interrupted or fails, you can retrieve the video using the job ID:

```bash
python3 generate.py --retrieve video_68fb838b22408193bc2fed30cbe4509903e1d733e5684a85
```

Job IDs are automatically saved to `.sora_jobs` file. The retrieve command will:

- Check the current status of the job
- Wait for completion if still processing
- Download the video when ready

### Delete a video

Delete a video from OpenAI's storage (videos are stored for 15 days by default):

```bash
python3 generate.py --delete video_68fb838b22408193bc2fed30cbe4509903e1d733e5684a85
```

**Note:** You cannot cancel in-progress jobs, but you can delete completed videos to clean up storage.

### List all videos

View all videos in your OpenAI storage:

```bash
python3 generate.py --list
```

This will display a table with:

- Job ID
- Status (queued, in_progress, completed, failed)
- Duration and resolution
- Creation timestamp
- Progress percentage (for in-progress videos)

## Prompt File Format

Create markdown files in the `prompts/` directory. See `prompts/advanced_example.md` for a complete example.

### Basic Structure

```markdown
# Video Title

## Prompt
Your video description here...

## Video Settings
| model | sora-2 |
| duration | 12 seconds |
| orientation | landscape |

## Audio (optional)
path/to/audio.mp3
```

### Advanced Features (Optional)

```markdown
## Camera (optional)
Wide shot, 85mm lens, f/2.8, slow dolly-in

## Lighting (optional)
Golden hour, soft diffused. Palette: amber, forest green, warm grey

## Dialogue (optional)
"Your spoken lines here"

## Input Reference (optional)
images/reference.jpg
```

**Model Options:**
- `sora-2` (default): Standard model
- `sora-2-pro`: Pro model (higher quality, higher cost)

Both models currently support: 4, 8, or 12 second videos

**Supported orientations:** landscape (1280x720), portrait (720x1280), square (1080x1080)

**Duration mapping:** The script automatically maps your requested duration to the nearest valid value for the selected model

### Advanced Prompting Tips

- **Camera**: Describe shot type, lens (e.g., 85mm), aperture (f-stop), and camera movement
- **Lighting**: Specify time of day, lighting style, and color palette
- **Dialogue**: Separate spoken lines from visual description for better results
- **Input Reference**: Single image used as first frame for image-to-video generation (must match target resolution)

## API Limitations

- **No job cancellation:** Once a video generation job is submitted, it cannot be cancelled
- **Video storage:** Generated videos are stored for 15 days before automatic deletion
- **Fixed durations:** Both models support 4, 8, or 12 seconds only
- **Cost:** Approximately $3 per 10-second video (costs vary by model and duration)
- **Note:** Despite web app supporting longer durations, the API currently limits both models to 4/8/12 seconds

## Project Structure

```
sora2-video-generation/
├── generate.py           # Main CLI script
├── prompts/             # Markdown prompt files
│   ├── simple_example.md    # Basic example
│   └── advanced_example.md  # Advanced features example
├── output/              # Generated videos (created automatically)
├── audio/               # Audio files for overlay (optional)
├── images/              # Reference images (optional)
├── .env                 # Your API key (not in git)
├── .env.example         # Template for .env
├── .sora_jobs           # Job ID history (not in git)
├── requirements.txt     # Python dependencies
├── CONTRIBUTING.md      # Contribution guidelines
└── README.md           # This file
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [OpenAI's Sora 2 API](https://platform.openai.com/docs/guides/video-generation)
- Uses the official [OpenAI Python SDK](https://github.com/openai/openai-python)

## Support

If you encounter issues or have questions:

- Check the [Issues](https://github.com/YOUR-USERNAME/halloween/issues) page
- Read the [CONTRIBUTING.md](CONTRIBUTING.md) guide
- Review the OpenAI [Sora 2 documentation](https://platform.openai.com/docs/guides/video-generation)
