from pathlib import Path
from typing import List, Optional, Union

from PIL import Image


def create_pdf(
    slides_dir: Union[str, Path],
    output_pdf_path: Optional[Union[str, Path]] = None,
) -> Path:
    """Compile JPG slide images in slides_dir into a single PDF document.

    Returns the Path to the generated PDF file.
    """
    slides_dir = Path(slides_dir)

    if output_pdf_path is None:
        output_pdf_path = slides_dir / "presentation.pdf"
    else:
        output_pdf_path = Path(output_pdf_path)

    # Find slide images sorted by filename (e.g. slide_001.jpg, slide_002.jpg)
    image_paths: List[Path] = sorted(slides_dir.glob("slide_*.jpg"))

    if not image_paths:
        # Fallback to any jpg or png files
        image_paths = sorted(list(slides_dir.glob("*.jpg")) + list(slides_dir.glob("*.png")))

    if not image_paths:
        raise FileNotFoundError(f"No slide images found in {slides_dir} to compile into PDF.")

    images: List[Image.Image] = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    first_image = images[0]
    rest_images = images[1:]

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    first_image.save(
        output_pdf_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=rest_images,
    )

    print(f"Generated presentation PDF with {len(images)} slides: {output_pdf_path}")
    return output_pdf_path
