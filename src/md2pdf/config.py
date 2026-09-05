from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path.cwd()
DEFAULT_INPUT = ROOT / "README.md"
DEFAULT_OUTPUT = ROOT / "README.pdf"
VERSION = "1.0.6"

FONT_REGULAR = ""
FONT_BOLD = ""

FONT_CANDIDATES = {
    # Existing/default fonts
    "default": {
        "regular": [
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            str(Path.home() / "Library/Fonts/Times New Roman.ttf"),
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/liberation/LiberationSerif-Regular.ttf",
        ],
        "bold": [
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
            str(Path.home() / "Library/Fonts/Times New Roman Bold.ttf"),
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/liberation/LiberationSerif-Bold.ttf",
        ],
        "names": ("GostTimes", "GostTimesBold"),
    },

#     # Unicode fonts with Armenian support
#     "utf8": {
#         "regular": [
#             # macOS
#             "/Library/Fonts/NotoSerifArmenian-Regular.ttf",
#             "/Library/Fonts/NotoSansArmenian-Regular.ttf",
#             str(Path.home() / "Library/Fonts/NotoSerifArmenian-Regular.ttf"),
#             str(Path.home() / "Library/Fonts/NotoSansArmenian-Regular.ttf"),

#             # Linux
#             "/usr/share/fonts/truetype/noto/NotoSerifArmenian-Regular.ttf",
#             "/usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf",
#             "/usr/share/fonts/opentype/noto/NotoSerifArmenian-Regular.ttf",
#             "/usr/share/fonts/opentype/noto/NotoSansArmenian-Regular.ttf",

#             # Fallbacks
#             "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
#             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
#         ],
#         "bold": [
#             # macOS
#             "/Library/Fonts/NotoSerifArmenian-Bold.ttf",
#             "/Library/Fonts/NotoSansArmenian-Bold.ttf",
#             str(Path.home() / "Library/Fonts/NotoSerifArmenian-Bold.ttf"),
#             str(Path.home() / "Library/Fonts/NotoSansArmenian-Bold.ttf"),

#             # Linux
#             "/usr/share/fonts/truetype/noto/NotoSerifArmenian-Bold.ttf",
#             "/usr/share/fonts/truetype/noto/NotoSansArmenian-Bold.ttf",
#             "/usr/share/fonts/opentype/noto/NotoSerifArmenian-Bold.ttf",
#             "/usr/share/fonts/opentype/noto/NotoSansArmenian-Bold.ttf",

#             # Fallbacks
#             "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
#             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
#         ],
#         "names": ("GostUnicode", "GostUnicodeBold"),
#     },
    "utf8": {
        "regular": [
            # These should be tried first
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/TTF/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",

            # macOS/Linux Noto fonts
            "/Library/Fonts/NotoSerifArmenian-Regular.ttf",
            str(Path.home() / "Library/Fonts/NotoSerifArmenian-Regular.ttf"),
            "/usr/share/fonts/truetype/noto/NotoSerifArmenian-Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSerifArmenian-Regular.ttf",
            "/usr/share/fonts/noto/NotoSansArmenian-Regular.ttf",
        ],
        "bold": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf",

            "/Library/Fonts/NotoSerifArmenian-Bold.ttf",
            str(Path.home() / "Library/Fonts/NotoSerifArmenian-Bold.ttf"),
            "/usr/share/fonts/truetype/noto/NotoSerifArmenian-Bold.ttf",
            "/usr/share/fonts/opentype/noto/NotoSerifArmenian-Bold.ttf",
            "/usr/share/fonts/noto/NotoSansArmenian-Bold.ttf",
        ],
        "names": ("GostUnicode", "GostUnicodeBold"),
    },

}

MERMAID_DIR = ROOT / ".md2pdf" / "mermaid"
MERMAID_COUNTER = 0
PARAGRAPH_INDENT = 12.5 * mm
QUIET = False


def normalize_font_mode(mode: str | None) -> str:
    """
    Normalize user-facing values such as:
        None, "default", "normal" -> "default"
        "utf8", "utf-8", "unicode", "armenian" -> "utf8"
    """
    if mode is None:
        return "default"

    normalized = mode.strip().lower().replace("_", "-")

    if normalized in {"default", "normal", "standard", "times"}:
        return "default"

    if normalized in {"utf8", "utf-8", "unicode", "armenian"}:
        return "utf8"

    raise ValueError(
        f"Unknown font mode: {mode!r}. "
        "Expected 'default' or 'utf-8'."
    )


def pick_font(mode: str, kind: str) -> str:
    candidates = FONT_CANDIDATES[mode][kind]

    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)

    raise RuntimeError(
        f"No suitable {kind} font found for font mode {mode!r}. "
        f"Install the required font or add its path to FONT_CANDIDATES."
    )


def register_fonts(mode: str | None = None) -> tuple[str, str]:
    """
    Register fonts and return (regular_font_name, bold_font_name).

    Examples:
        register_fonts()              # Existing/default behavior
        register_fonts("default")     # Existing/default behavior
        register_fonts("utf-8")       # Unicode/Armenian-compatible fonts
        register_fonts("armenian")    # Alias for utf-8 mode
    """
    global FONT_REGULAR, FONT_BOLD

    mode = normalize_font_mode(mode)
    profile = FONT_CANDIDATES[mode]

    FONT_REGULAR = pick_font(mode, "regular")
    FONT_BOLD = pick_font(mode, "bold")

    regular_name, bold_name = profile["names"]

    if regular_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(regular_name, FONT_REGULAR))

    if bold_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(bold_name, FONT_BOLD))
    print(f"\n\tFonts registered: {FONT_REGULAR}, {FONT_BOLD}\n")
    return regular_name, bold_name


def set_mermaid_dir(path: Path) -> None:
    global MERMAID_DIR
    MERMAID_DIR = path


def set_quiet(value: bool) -> None:
    global QUIET
    QUIET = value
