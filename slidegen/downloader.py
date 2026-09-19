import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Union


def get_youtube_entries(url: str) -> List[Dict[str, Any]]:
    """Determine whether a YouTube URL points to a single video or playlist.

    Returns:
        List of dicts containing keys: 'id', 'title', 'index'
    """
    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--no-warnings",
        url,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Could not inspect YouTube URL: {url}\n{result.stderr.strip()}"
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Failed to parse yt-dlp metadata for {url}: {exc}"
        ) from exc

    # Playlist URL handling
    if data.get("_type") == "playlist":
        entries = []
        for index, entry in enumerate(data.get("entries", []), start=1):
            if not entry:
                continue
            entries.append(
                {
                    "id": entry["id"],
                    "title": entry.get("title", entry["id"]),
                    "index": index,
                }
            )
        return entries

    # Single video URL handling
    return [
        {
            "id": data.get("id", ""),
            "title": data.get("title", data.get("id", "video")),
            "index": 1,
        }
    ]


def download_video(
    video_url: str,
    output_dir: Union[str, Path],
) -> Path:
    """Download a video using yt-dlp and return the Path to the downloaded video file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = output_dir / "video.%(ext)s"

    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "-f",
        "bv*[ext=mp4]/bv*",
        "--remux-video",
        "mp4",
        "-o",
        str(output_template),
        video_url,
    ]

    print(f"Downloading video from {video_url}...")
    result = subprocess.run(command)

    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed to download video from {video_url}.")

    mp4_path = output_dir / "video.mp4"
    if mp4_path.exists():
        return mp4_path

    # Fallback to any downloaded video file
    candidates = list(output_dir.glob("video.*"))
    if not candidates:
        raise RuntimeError(
            f"Download completed, but no video file was found in {output_dir}."
        )

    return candidates[0]
