"""
cli.py – exposes the `smartqr` console command
"""

from pathlib import Path
import argparse
from urllib.parse import quote

from .core import make_qr


def build_upi_uri(vpa: str, name: str, amount: str | None, note: str | None) -> str:
    params = [("pa", vpa), ("pn", name), ("cu", "INR")]
    if amount:
        params.append(("am", f"{float(amount):.2f}"))
    if note:
        params.append(("tn", note))
    return "upi://pay?" + "&".join(f"{k}={quote(v)}" for k, v in params)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="smartqr",
        description="Create text or UPI QR codes (PNG or SVG)",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Plain text, URL, Wi-Fi string …")
    g.add_argument("--upi", nargs=2, metavar=("VPA", "NAME"),
                   help="Generate a UPI payment QR")

    p.add_argument("--amount", help="Amount for UPI QR (e.g., 499.00)")
    p.add_argument("--note",   help="Message for UPI QR")
    p.add_argument("--outfile", default="qr.png", help="Output filename")
    p.add_argument("--logo", help="Path to centre logo (PNG only)")
    p.add_argument("-e", "--error", default="M", choices=list("LMQH"),
                   help="Error-correction level (default M)")

    opts = p.parse_args(argv)

    # Decide what to encode
    if opts.upi:
        data = build_upi_uri(opts.upi[0], opts.upi[1], opts.amount, opts.note)
    else:
        data = opts.text

    path = make_qr(
        data,
        Path(opts.outfile),
        error=opts.error,
        logo_path=Path(opts.logo) if opts.logo else None,
        svg=opts.outfile.lower().endswith(".svg"),
    )
    print(f"✅  QR saved to {path.resolve()}")


if __name__ == "__main__":
    main()
