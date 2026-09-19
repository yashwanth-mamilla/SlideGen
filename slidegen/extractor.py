import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np

from slidegen.utils import format_timestamp

DEFAULT_INTERVAL = 0.1
DEFAULT_THRESHOLD = 0.05
DEFAULT_STABLE_SAMPLES = 3


def make_signature(frame: np.ndarray) -> np.ndarray:
    """Create a small cropped, resized, grayscale signature of a video frame."""
    height, width = frame.shape[:2]

    margin_x = int(width * 0.02)
    margin_y = int(height * 0.02)

    cropped = frame[
        margin_y : height - margin_y,
        margin_x : width - margin_x,
    ]

    resized = cv2.resize(cropped, (320, 180))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    return blurred


def difference_score(
    reference: np.ndarray,
    current: np.ndarray,
) -> float:
    """Calculate normalized visual difference score between reference and current signatures."""
    diff = cv2.absdiff(reference, current)
    mean_difference = float(diff.mean()) / 255.0
    changed_pixels = float(np.mean(diff > 25))

    return 0.60 * mean_difference + 0.40 * changed_pixels


class SlideExtractor:
    """Slide extraction engine configurable with detection thresholds and intervals."""

    def __init__(
        self,
        interval: float = DEFAULT_INTERVAL,
        threshold: float = DEFAULT_THRESHOLD,
        stable_samples: int = DEFAULT_STABLE_SAMPLES,
    ):
        self.interval = interval
        self.threshold = threshold
        self.stable_samples = stable_samples

    def extract(
        self,
        video_path: Union[str, Path],
        output_dir: Union[str, Path],
    ) -> List[Dict[str, Any]]:
        """Extract slide frames from video and write output slide JPG images and metadata JSON."""
        video_path = Path(video_path)
        output_dir = Path(output_dir)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            cap.release()
            raise RuntimeError(f"Invalid video FPS ({fps}) for file: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0.0

        print(f"Video     : {video_path.name}")
        print(f"FPS       : {fps:.2f}")
        print(f"Duration  : {format_timestamp(duration)}")
        print(f"Interval  : {self.interval}s")
        print(f"Threshold : {self.threshold}")
        print()

        reference_signature: Optional[np.ndarray] = None
        candidate_count = 0
        slide_number = 0
        frame_index = 0
        last_slide_time = -float("inf")

        sample_every = max(1, int(self.interval * fps))
        slides: List[Dict[str, Any]] = []

        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                if frame_index % sample_every != 0:
                    frame_index += 1
                    continue

                timestamp = frame_index / fps
                signature = make_signature(frame)

                # First valid frame becomes slide 1
                if reference_signature is None:
                    slide_number += 1
                    slide_path = output_dir / f"slide_{slide_number:03d}.jpg"

                    cv2.imwrite(
                        str(slide_path),
                        frame,
                        [cv2.IMWRITE_JPEG_QUALITY, 95],
                    )

                    slides.append(
                        {
                            "slide": slide_number,
                            "timestamp": timestamp,
                            "timestamp_formatted": format_timestamp(timestamp),
                            "file": slide_path.name,
                        }
                    )

                    reference_signature = signature
                    last_slide_time = timestamp
                    print(
                        f"[{format_timestamp(timestamp)}] Slide {slide_number}"
                    )

                    frame_index += 1
                    continue

                score = difference_score(reference_signature, signature)

                if score >= self.threshold:
                    candidate_count += 1
                else:
                    candidate_count = 0

                if candidate_count >= self.stable_samples:
                    if timestamp - last_slide_time >= self.interval:
                        slide_number += 1
                        slide_path = output_dir / f"slide_{slide_number:03d}.jpg"

                        cv2.imwrite(
                            str(slide_path),
                            frame,
                            [cv2.IMWRITE_JPEG_QUALITY, 95],
                        )

                        slides.append(
                            {
                                "slide": slide_number,
                                "timestamp": timestamp,
                                "timestamp_formatted": format_timestamp(timestamp),
                                "file": slide_path.name,
                                "difference": round(score, 4),
                            }
                        )

                        print(
                            f"[{format_timestamp(timestamp)}] Slide {slide_number} "
                            f"(diff={score:.3f})"
                        )

                        reference_signature = signature
                        last_slide_time = timestamp

                    candidate_count = 0

                frame_index += 1

        finally:
            cap.release()

        # Save slides.json metadata
        metadata_path = output_dir / "slides.json"
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "video": str(video_path),
                    "interval": self.interval,
                    "threshold": self.threshold,
                    "stable_samples": self.stable_samples,
                    "slides": slides,
                },
                f,
                indent=2,
            )

        return slides


def extract_slides(
    video_path: Union[str, Path],
    output_dir: Union[str, Path],
    interval: float = DEFAULT_INTERVAL,
    threshold: float = DEFAULT_THRESHOLD,
    stable_samples: int = DEFAULT_STABLE_SAMPLES,
) -> List[Dict[str, Any]]:
    """Functional helper to extract slides using default or custom parameters."""
    extractor = SlideExtractor(
        interval=interval,
        threshold=threshold,
        stable_samples=stable_samples,
    )
    return extractor.extract(video_path, output_dir)
