from pathlib import Path
import cv2
import numpy as np
import pytest
from slidegen.cli import main


def test_cli_local_video_path(tmp_path: Path):
    video_file = tmp_path / "sample.mp4"
    output_dir = tmp_path / "cli_output"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_file), fourcc, 10.0, (320, 240))

    try:
        frame = np.ones((240, 320, 3), dtype=np.uint8) * 200
        for _ in range(20):
            out.write(frame)
    finally:
        out.release()

    # Pass local video path to CLI main function
    exit_code = main([str(video_file), "-o", str(output_dir)])

    assert exit_code == 0
    assert (output_dir / "slides" / "slide_001.jpg").exists()
    assert (output_dir / "sample.pdf").exists()
