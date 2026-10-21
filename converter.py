from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()

ProgressCallback = Callable[[int, int, Path], None]


@dataclass
class ConversionResult:
    total: int
    converted: int
    errors: list[tuple[Path, str]]


def convert_folder(
    source_folder: Path,
    output_folder: Path,
    progress_callback: ProgressCallback | None = None,
) -> ConversionResult:
    source_folder = source_folder.resolve()
    output_folder = output_folder.resolve()

    if not source_folder.is_dir():
        raise ValueError(f"Le dossier source n'existe pas : {source_folder}")

    heic_files = [
        path
        for path in source_folder.rglob("*")
        if path.is_file()
        and path.suffix.casefold() == ".heic"
        and output_folder not in path.parents
    ]
    errors = []
    converted = 0
    output_folder.mkdir(parents=True, exist_ok=True)

    for index, source_file in enumerate(heic_files, start=1):
        destination = output_folder / source_file.relative_to(source_folder).with_suffix(
            ".png"
        )
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(source_file) as image:
                ImageOps.exif_transpose(image).save(destination, format="PNG")
            converted += 1
        except Exception as error:
            errors.append((source_file, str(error)))

        if progress_callback is not None:
            progress_callback(index, len(heic_files), source_file)

    return ConversionResult(len(heic_files), converted, errors)
