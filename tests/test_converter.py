import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from converter import convert_folder


class ConvertFolderTests(unittest.TestCase):
    def test_converts_a_real_heic_image(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            heic_file = source / "photo.heic"
            Image.new("RGB", (32, 32), (220, 40, 10)).save(heic_file, format="HEIF")

            result = convert_folder(source, source / "PNG")

            with Image.open(source / "PNG" / "photo.png") as png:
                self.assertEqual(png.format, "PNG")
                self.assertEqual(png.size, (32, 32))
            self.assertEqual((result.total, result.converted, result.errors), (1, 1, []))

    def test_converts_heic_files_recursively_and_skips_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "photos"
            nested = source / "vacances"
            nested.mkdir(parents=True)
            (source / "photo.HEIC").touch()
            (nested / "plage.heic").touch()
            (source / "not-an-image.jpg").touch()
            output = source / "PNG"
            output.mkdir()
            (output / "already.heic").touch()

            image = MagicMock()
            image.__enter__.return_value = image
            progress = []
            with (
                patch("converter.Image.open", return_value=image) as open_image,
                patch("converter.ImageOps.exif_transpose", side_effect=lambda item: item),
            ):
                result = convert_folder(
                    source,
                    output,
                    lambda completed, total, path: progress.append(
                        (completed, total, path.name)
                    ),
                )

            self.assertEqual((result.total, result.converted, result.errors), (2, 2, []))
            self.assertEqual(open_image.call_count, 2)
            image.save.assert_any_call(output / "photo.png", format="PNG")
            image.save.assert_any_call(output / "vacances" / "plage.png", format="PNG")
            self.assertEqual(len(progress), 2)

    def test_records_a_failed_image_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            broken = source / "broken.heic"
            working = source / "working.heic"
            broken.touch()
            working.touch()

            image = MagicMock()
            image.__enter__.return_value = image

            def open_image(path: Path) -> MagicMock:
                if path == broken:
                    raise OSError("fichier illisible")
                return image

            with (
                patch("converter.Image.open", side_effect=open_image),
                patch("converter.ImageOps.exif_transpose", side_effect=lambda item: item),
            ):
                result = convert_folder(source, source / "PNG")

            self.assertEqual(result.total, 2)
            self.assertEqual(result.converted, 1)
            self.assertEqual(result.errors, [(broken, "fichier illisible")])

    def test_rejects_a_missing_source_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "missing"

            with self.assertRaises(ValueError):
                convert_folder(missing, missing / "PNG")


if __name__ == "__main__":
    unittest.main()
