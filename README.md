# SlideGen 📸🎞️

**SlideGen** is a Python command-line tool and library designed to automatically download YouTube videos (or playlists) and extract unique presentation slides as high-quality images and PDF documents using computer vision.

---

## Features

- 🎥 **YouTube & Local Videos**: Download and extract slides directly from YouTube URLs (single videos or full playlists) or local video files (`.mp4`, `.mkv`, etc.).
- 🧠 **Smart Visual Change Detection**: Uses OpenCV image signatures, Gaussian blur filtering, and pixel-difference thresholding to accurately detect slide transitions while ignoring minor video noise.
- 📄 **Automatic PDF Compilation**: Automatically compile extracted slide images into a single `presentation.pdf` document.
- 📊 **JSON Metadata Output**: Saves a structured `slides.json` file with exact timestamps, formatted timecodes, and slide image filenames.
- ⚡ **Library & CLI**: Use it as a CLI tool (`slidegen`) or import it into Python code (`import slidegen`).

---

## Installation

### Prerequisites
- Python 3.9 or higher
- `ffmpeg` (recommended for video remuxing with `yt-dlp`)

### Install from Source
```bash
# Clone repository
git clone https://github.com/your-username/slidegen.git
cd slidegen


# Install package in editable mode
pip install -e .
```

---

## Usage

### Command Line Interface (CLI)

#### 1. Download YouTube Video & Extract Slides + PDF
```bash
slidegen "https://www.youtube.com/watch?v=EXAMPLE_ID"
```

#### 2. Process a Local Video File
```bash
slidegen path/to/lecture.mp4 -o output_dir
```

#### 3. Process a YouTube Playlist
```bash
slidegen "https://www.youtube.com/playlist?list=EXAMPLE_PLAYLIST" -o my_playlist_slides
```

#### 4. Custom Detection Parameters
```bash
slidegen "https://www.youtube.com/watch?v=EXAMPLE_ID" \
  --interval 0.1 \
  --threshold 0.05 \
  --stable-samples 3 \
  --keep-video \
  --no-pdf
```

### Options

| Flag | Short | Default | Description |
|---|---|---|---|
| `input` | | *Required* | YouTube video/playlist URL or local video file path |
| `--output` | `-o` | `output` | Output directory destination |
| `--interval` | | `0.1` | Sampling interval in seconds between frame checks |
| `--threshold` | | `0.05` | Visual change threshold ratio (0.0 to 1.0) |
| `--stable-samples` | | `3` | Consecutive sample count required to confirm slide change |
| `--keep-video` | | `False` | Keep downloaded video file after processing |
| `--no-pdf` | | `False` | Disable automatic PDF compilation |

---

## Python API Usage

SlideGen can be imported and integrated directly into Python applications:

```python
from pathlib import Path
from slidegen import download_video, extract_slides, create_pdf

# 1. Download video
video_path = download_video(
    "https://www.youtube.com/watch?v=EXAMPLE_ID",
    output_dir=Path("./work_dir")
)

# 2. Extract slides
slides = extract_slides(
    video_path=video_path,
    output_dir=Path("./slides_output"),
    interval=0.1,
    threshold=0.05,
    stable_samples=3,
)


# 3. Create PDF presentation
pdf_path = create_pdf(
    slides_dir=Path("./slides_output"),
    output_pdf_path=Path("./slides_output/presentation.pdf")
)

print(f"Extracted {len(slides)} slides to {pdf_path}")
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
# SlideGen
