"""
core.py – low-level helpers for Smart QR Tools
"""

from pathlib import Path
from typing import Optional

import qrcode
from qrcode.image.svg import SvgImage
from PIL import Image


def make_qr(
    data: str,
    outfile: Path,
    *,
    error: str = "M",
    box_size: int = 10,
    svg: bool = False,
    logo_path: Optional[Path] = None,
) -> Path:
    """
    Generate a QR code from *data* and save it to *outfile*.

    Parameters
    ----------
    data : str
        The text/URI to encode.
    outfile : pathlib.Path
        Output path (extension will be changed to .png or .svg automatically).
    error : str
        Error-correction level: one of 'L', 'M', 'Q', 'H'.  Default = 'M'.
    box_size : int
        Pixel size of each QR module.  Larger ⇒ higher resolution.  Default = 10.
    svg : bool
        If True, produce SVG instead of PNG.
    logo_path : Path | None
        Optional PNG logo to embed at the centre (PNG output only).

    Returns
    -------
    pathlib.Path
        Final path of the written file.
    """
    # Choose factory class for SVG or default PIL image
    factory = SvgImage if svg else None

    qr = qrcode.QRCode(
        error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error}"),
        box_size=box_size,
        border=4,
        image_factory=factory,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Normalise extension
    outfile = outfile.with_suffix(".svg" if svg else ".png")

    # ------- Optional logo embedding (PNG only) -------
    if logo_path and not svg:
        base = img.convert("RGBA")          # Ensure RGBA
        logo = Image.open(logo_path).convert("RGBA")

        # Scale logo to 20 % of QR width
        target = int(base.size[0] * 0.20)
        logo = logo.resize((target, target), Image.LANCZOS)

        # Paste centred
        pos = ((base.size[0] - target) // 2, (base.size[1] - target) // 2)
        base.paste(logo, pos, mask=logo)
        base.save(outfile)
    else:
        img.save(outfile)

    return outfile
