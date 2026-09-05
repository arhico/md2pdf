from __future__ import annotations

import sys
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from md2pdf.pdf import PdfOptions, build_pdf


DEFAULT_PDF_OPTIONS: dict[str, object] = {
    "font_size": 14,
    "line_height": 1.5,
    "diagram_max_height_mm": 135,
    "margins_mm": (30, 10, 20, 20),
}

DEFAULT_SETTINGS: dict[str, object] = {
    "last_directory": None,
    "window_width": 800,
    "window_height": 600,
}

SETTINGS_FILE = Path("./md_to_pdf_batch.cfg")


def load_settings() -> dict[str, object]:
    """Load saved settings, falling back to defaults if necessary."""
    try:
        if SETTINGS_FILE.is_file():
            saved_settings = json.loads(
                SETTINGS_FILE.read_text(encoding="utf-8")
            )
            if isinstance(saved_settings, dict):
                return DEFAULT_SETTINGS | saved_settings
    except (OSError, json.JSONDecodeError):
        pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict[str, object]) -> None:
    """Save settings to the local settings file."""
    try:
        SETTINGS_FILE.write_text(
            json.dumps(settings, indent=2),
            encoding="utf-8",
        )
    except OSError as error:
        print(f"WARNING: Could not save settings: {error}", file=sys.stderr)


def get_last_directory(settings: dict[str, object]) -> Path | None:
    """Return the saved directory if it still exists."""
    saved_directory = settings.get("last_directory")
    if not isinstance(saved_directory, str) or not saved_directory:
        return None
    directory = Path(saved_directory)
    if directory.is_dir():
        return directory.resolve()
    return None


def save_window_dimensions(window: tk.Tk) -> None:
    """Save the current Tk window dimensions, handling withdrawn state."""
    try:
        # To get actual dimensions, the window MUST be mapped/visible
        # We momentarily deiconify to get real measurements from the OS
        was_withdrawn = window.state() == 'withdrawn'
        if was_withdrawn:
            window.deiconify()
        
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        
        if was_withdrawn:
            window.withdraw()

        # Prevent saving the '1x1' fallback if mapping failed
        if width > 1 and height > 1:
            settings = load_settings()
            settings["window_width"] = width
            settings["window_height"] = height
            save_settings(settings)
    except tk.TclError:
        pass


def restore_window_dimensions(window: tk.Tk) -> None:
    """Restore the previously saved Tk window dimensions."""
    settings = load_settings()
    width = settings.get("window_width", 800)
    height = settings.get("window_height", 600)

    if not isinstance(width, int) or width < 200:
        width = 800
    if not isinstance(height, int) or height < 150:
        height = 600

    window.geometry(f"{width}x{height}")


def select_root_directory(root: tk.Tk) -> Path | None:
    """Show a directory picker starting in the previously selected directory."""
    settings = load_settings()
    last_directory = get_last_directory(settings)

    # Restore size before showing dialog
    restore_window_dimensions(root)
    root.update_idletasks()

    dialog_options: dict[str, object] = {
        "title": "Select the root directory containing Markdown files",
        "mustexist": True,
    }

    if last_directory is not None:
        dialog_options["initialdir"] = str(last_directory)

    try:
        selected_directory = filedialog.askdirectory(parent=root, **dialog_options)
    finally:
        # Save the size the user had (or the restored size)
        save_window_dimensions(root)

    if not selected_directory:
        return None

    directory = Path(selected_directory).resolve()
    settings["last_directory"] = str(directory)
    save_settings(settings)

    return directory


def find_markdown_files(root_directory: Path) -> list[Path]:
    """Recursively find Markdown files below the selected directory."""
    return sorted(
        path
        for path in root_directory.rglob("*")
        if path.is_file() and path.suffix.lower() == ".md"
    )


def convert_markdown_files(
    root_directory: Path,
    **pdf_options: object,
) -> tuple[int, int, list[str]]:
    """Convert all Markdown files to PDFs."""
    markdown_files = find_markdown_files(root_directory)
    if not markdown_files:
        return 0, 0, []

    options = PdfOptions(**pdf_options)
    successful_count = 0
    failed_count = 0
    errors: list[str] = []

    for index, markdown_path in enumerate(markdown_files, start=1):
        pdf_path = markdown_path.with_suffix(".pdf")
        print(f"[{index}/{len(markdown_files)}] {markdown_path} -> {pdf_path}")
        try:
            build_pdf(input_path=markdown_path, output_path=pdf_path, options=options)
            successful_count += 1
        except Exception as error:
            failed_count += 1
            error_message = f"{markdown_path}: {error}"
            errors.append(error_message)
            print(f"ERROR: {error_message}", file=sys.stderr)

    return successful_count, failed_count, errors


def main(**pdf_options: object) -> None:
    options = DEFAULT_PDF_OPTIONS | pdf_options

    root = tk.Tk()
    root.withdraw()  # Hide main window, but keep it as the parent

    try:
        root_directory = select_root_directory(root)
        if root_directory is None:
            print("No directory selected.")
            return

        print(f"Searching for Markdown files in: {root_directory}")
        successful, failed, errors = convert_markdown_files(root_directory, **options)

        summary = f"Conversion complete.\n\nConverted: {successful}\nFailed: {failed}"
        if errors:
            summary += "\n\nFailed files:\n" + "\n".join(errors)

        print("\n" + summary)

        if failed:
            messagebox.showwarning("Markdown to PDF conversion", summary, parent=root)
        else:
            messagebox.showinfo("Markdown to PDF conversion", summary, parent=root)
    finally:
        root.destroy()


if __name__ == "__main__":
    main(
        font_size=12,
        line_height=1.3,
        diagram_max_height_mm=135,
        margins_mm=(15, 10, 20, 20),
    )
