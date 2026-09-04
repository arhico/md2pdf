from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from md2pdf.pdf import PdfOptions, build_pdf


def select_root_directory() -> Path | None:
    """Show a directory picker and return the selected directory."""
    window = tk.Tk()
    window.withdraw()

    selected_directory = filedialog.askdirectory(
        title="Select the root directory containing Markdown files"
    )

    window.destroy()

    if not selected_directory:
        return None

    return Path(selected_directory).resolve()


def find_markdown_files(root_directory: Path) -> list[Path]:
    """Recursively find Markdown files below the selected directory."""
    return sorted(
        path
        for path in root_directory.rglob("*")
        if path.is_file() and path.suffix.lower() == ".md"
    )


def convert_markdown_files(root_directory: Path) -> tuple[int, int, list[str]]:
    """
    Convert all Markdown files to PDFs.

    PDFs are written next to their source Markdown files.
    Returns:
        successful_count, failed_count, errors
    """
    markdown_files = find_markdown_files(root_directory)

    if not markdown_files:
        return 0, 0, []

    # These options match the repository defaults.
    options = PdfOptions(
        font_size=14,
        line_height=1.5,
        diagram_max_height_mm=135,
        margins_mm=(30, 10, 20, 20),
    )

    successful_count = 0
    failed_count = 0
    errors: list[str] = []

    for index, markdown_path in enumerate(markdown_files, start=1):
        pdf_path = markdown_path.with_suffix(".pdf")

        print(
            f"[{index}/{len(markdown_files)}] "
            f"{markdown_path} -> {pdf_path}"
        )

        try:
            build_pdf(
                input_path=markdown_path,
                output_path=pdf_path,
                options=options,
            )
            successful_count += 1

        except Exception as error:
            failed_count += 1
            error_message = f"{markdown_path}: {error}"
            errors.append(error_message)
            print(f"ERROR: {error_message}", file=sys.stderr)

    return successful_count, failed_count, errors


def main() -> None:
    root_directory = select_root_directory()

    if root_directory is None:
        print("No directory selected.")
        return

    print(f"Searching for Markdown files in: {root_directory}")

    successful, failed, errors = convert_markdown_files(root_directory)

    summary = (
        f"Conversion complete.\n\n"
        f"Converted: {successful}\n"
        f"Failed: {failed}"
    )

    if errors:
        summary += "\n\nFailed files:\n" + "\n".join(errors)

    print("\n" + summary)

    window = tk.Tk()
    window.withdraw()

    if failed:
        messagebox.showwarning("Markdown to PDF conversion", summary)
    else:
        messagebox.showinfo("Markdown to PDF conversion", summary)

    window.destroy()


if __name__ == "__main__":
    main(font_size=12)
