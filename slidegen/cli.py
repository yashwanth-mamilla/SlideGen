import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional, Sequence

from slidegen.downloader import download_video, get_youtube_entries
from slidegen.extractor import (
    DEFAULT_INTERVAL,
    DEFAULT_STABLE_SAMPLES,
    DEFAULT_THRESHOLD,
    extract_slides,
)
from slidegen.pdf import create_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slidegen",
        description="Download YouTube videos/playlists and extract presentation slides.",
    )

    parser.add_argument(
        "input",
        help="YouTube video/playlist URL or local video file path",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output directory (default: output)",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"Seconds between slide sampling checks (default: {DEFAULT_INTERVAL})",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Visual difference threshold (default: {DEFAULT_THRESHOLD})",
    )

    parser.add_argument(
        "--stable-samples",
        type=int,
        default=DEFAULT_STABLE_SAMPLES,
        help=f"Consecutive sample count required for slide change (default: {DEFAULT_STABLE_SAMPLES})",
    )

    parser.add_argument(
        "--keep-video",
        action="store_true",
        help="Keep downloaded video files after processing",
    )

    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Disable automatic generation of presentation PDF document",
    )

    return parser


from slidegen.utils import sanitize_filename


def process_video_file(
    video_path: Path,
    output_dir: Path,
    args: argparse.Namespace,
    title: Optional[str] = None,
) -> None:
    """Extract slides and compile PDF for a single video file."""
    slides_dir = output_dir / "slides"

    slides = extract_slides(
        video_path=video_path,
        output_dir=slides_dir,
        interval=args.interval,
        threshold=args.threshold,
        stable_samples=args.stable_samples,
    )

    print(f"\nExtracted {len(slides)} slides.")

    if not args.no_pdf and slides:
        try:
            pdf_name = sanitize_filename(title or video_path.stem) + ".pdf"
            pdf_path = output_dir / pdf_name
            create_pdf(slides_dir=slides_dir, output_pdf_path=pdf_path)
        except Exception as exc:
            print(f"Warning: Could not create PDF presentation: {exc}", file=sys.stderr)



def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = Path(args.output)

    try:
        input_path = Path(args.input)

        # ---------------------------------------------------------------
        # Case 1: Input is a Local Video File
        # ---------------------------------------------------------------
        if input_path.exists() and input_path.is_file():
            print(f"Processing local video file: {input_path}")
            process_video_file(input_path, output_dir, args)
            print("\nAll done.")
            return 0

        # ---------------------------------------------------------------
        # Case 2: Input is YouTube URL (Video or Playlist)
        # ---------------------------------------------------------------
        print("Inspecting YouTube URL...")
        entries = get_youtube_entries(args.input)

        if len(entries) == 1:
            print(f"Found video: {entries[0]['title']}")
        else:
            print(f"Found playlist containing {len(entries)} videos.")
        print()

        for position, entry in enumerate(entries, start=1):
            video_id = entry["id"]
            title = entry["title"]

            print("=" * 70)
            print(f"[{position}/{len(entries)}] {title}")
            print("=" * 70)

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            if len(entries) == 1:
                video_dir = output_dir
            else:
                video_dir = output_dir / f"{position:03d}_{video_id}"

            try:
                downloaded_video = download_video(video_url, video_dir)
                process_video_file(downloaded_video, video_dir, args, title=title)

            finally:
                if not args.keep_video:
                    video_file = video_dir / "video.mp4"
                    if video_file.exists():
                        video_file.unlink()

        print("\nAll done.")
        return 0

    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 130

    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
