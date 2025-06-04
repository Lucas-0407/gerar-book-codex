import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path

from PIL import Image

from src.pdf_generator import extract_key, generate_book


def test_extract_key_sorting():
    names = ["img10.jpg", "img2.jpg", "img1.jpg"]
    assert sorted(names, key=extract_key) == ["img1.jpg", "img2.jpg", "img10.jpg"]


def test_generate_book(tmp_path: Path):
    folder = tmp_path / "images"
    folder.mkdir()
    for i in range(3):
        img = Image.new("RGB", (100, 100), color=(i * 30, i * 30, i * 30))
        img.save(folder / f"img{i}.jpg")

    output = tmp_path / "out.pdf"
    generate_book(str(folder), str(output), columns=2)
    assert output.exists()


