import cv2
import numpy as np
import pytest
from pathlib import Path
from slidegen.extractor import SlideExtractor, difference_score, extract_slides, make_signature


def test_make_signature():
    # Create a synthetic 100x100 RGB image
    fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    fake_frame[20:80, 20:80] = 255

    sig = make_signature(fake_frame)
    assert sig.shape == (180, 320)
    assert sig.dtype == np.uint8


def test_difference_score_identical():
    sig1 = np.ones((180, 320), dtype=np.uint8) * 128
    sig2 = np.ones((180, 320), dtype=np.uint8) * 128

    score = difference_score(sig1, sig2)
    assert score == pytest.approx(0.0)


def test_difference_score_distinct():
    sig1 = np.zeros((180, 320), dtype=np.uint8)
    sig2 = np.ones((180, 320), dtype=np.uint8) * 255

    score = difference_score(sig1, sig2)
    assert score > 0.9


def test_extract_slides_from_local_video(tmp_path: Path):
    # Generate a temporary synthetic video with two distinct slides
    video_file = tmp_path / "test_video.mp4"
    output_dir = tmp_path / "output_slides"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_file), fourcc, 10.0, (640, 480))

    try:
        # Slide 1 (black background with white square)
        frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame1[100:380, 100:540] = (255, 255, 255)
        for _ in range(30):  # 3 seconds
            out.write(frame1)

        # Slide 2 (red background with blue square)
        frame2 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame2[:, :] = (0, 0, 255)
        frame2[100:380, 100:540] = (255, 0, 0)
        for _ in range(30):  # 3 seconds
            out.write(frame2)
    finally:
        out.release()

    slides = extract_slides(
        video_path=video_file,
        output_dir=output_dir,
        interval=0.1,
        threshold=0.05,
        stable_samples=3,
    )

    assert len(slides) == 2
    assert (output_dir / "slide_001.jpg").exists()
    assert (output_dir / "slide_002.jpg").exists()
    assert (output_dir / "slides.json").exists()
