"""SlideGen - Download YouTube videos and extract presentation slides."""

from slidegen.downloader import download_video, get_youtube_entries
from slidegen.extractor import SlideExtractor, difference_score, extract_slides, make_signature
from slidegen.pdf import create_pdf

__version__ = "0.1.0"

__all__ = [
    "download_video",
    "get_youtube_entries",
    "extract_slides",
    "SlideExtractor",
    "make_signature",
    "difference_score",
    "create_pdf",
    "__version__",
]
