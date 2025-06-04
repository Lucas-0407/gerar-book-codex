import os
import re
import logging
from datetime import datetime
from typing import Iterable, List, Callable, Optional

from fpdf import FPDF
from PIL import Image


def extract_key(name: str) -> List[int | str]:
    """Return a sortable key extracted from a filename.

    Parameters
    ----------
    name: str
        Filename to parse.

    Returns
    -------
    list[int | str]
        List containing integers found in the filename. If none are
        found, returns the lowercase filename for alphabetical sort.
    """
    numbers = re.findall(r"\d+", name)
    if numbers:
        return [int(n) for n in numbers]
    return [name.lower()]


def discover_images(folder: str) -> List[str]:
    """Return a sorted list of image file paths from a folder."""
    valid_ext = {".jpg", ".jpeg", ".png"}
    files = [os.path.join(folder, f) for f in os.listdir(folder)
             if os.path.splitext(f)[1].lower() in valid_ext]
    files.sort(key=lambda p: extract_key(os.path.basename(p)))
    return files


class BookPDF(FPDF):
    """Custom PDF layout with title, header and footer."""

    def __init__(self, title: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.title = title

    def header(self) -> None:  # type: ignore[override]
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, self.title, align="C", ln=1)
        self.ln(3)

    def footer(self) -> None:  # type: ignore[override]
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        date = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f"Página {self.page_no()} - {date}", align="C")


def generate_book(
    image_folder: str,
    output_pdf: str,
    columns: int = 3,
    add_cover: bool = False,
    title: str = "Locações, Projetos e Construções Elétricas",
    log_file: Optional[str] = None,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Generate a PDF book from images in *image_folder*.

    Parameters
    ----------
    image_folder : str
        Directory containing the images.
    output_pdf : str
        Path of the resulting PDF file.
    columns : int, optional
        Number of columns per page (between 2 and 4), by default 3.
    add_cover : bool, optional
        If ``True``, use the first image as the cover, by default False.
    title : str, optional
        Document title, by default "Locações, Projetos e Construções Elétricas".
    log_file : str, optional
        Path to a log file. If provided, execution details are stored there.
    progress_cb : callable, optional
        Callback receiving ``current`` and ``total`` image counts to report
        progress.
    """

    assert 2 <= columns <= 4, "Número de colunas deve ser entre 2 e 4"

    images = discover_images(image_folder)
    total = len(images)

    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")
    logging.info("Gerando PDF %s com %d imagens", output_pdf, total)

    pdf = BookPDF(title=title)
    pdf.set_auto_page_break(auto=True, margin=15)

    width, height = 210, 297  # tamanho A4 em mm
    margin = 10
    col_width = (width - margin * (columns + 1)) / columns
    row_height = 90 - (columns - 2) * 10  # ajuste simples para 3 ou 4 colunas
    max_img_height = row_height - 20
    images_per_page = columns * int((height - 40) // row_height)

    idx = 0
    if add_cover and images:
        pdf.add_page()
        with Image.open(images[0]) as img:
            iw, ih = img.size
            ratio = min((width - 2 * margin) / iw, (height - 2 * margin) / ih)
            w_img, h_img = iw * ratio, ih * ratio
            x_img = (width - w_img) / 2
            y_img = (height - h_img) / 2
            pdf.image(images[0], x=x_img, y=y_img, w=w_img, h=h_img)
        idx = 1

    for count, img_path in enumerate(images[idx:], start=idx):
        if count % images_per_page == 0:
            pdf.add_page()
        position = count % images_per_page
        row = position // columns
        col = position % columns
        x = margin + col * (col_width + margin)
        y = margin + row * row_height

        desc = os.path.splitext(os.path.basename(img_path))[0]
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "B", 8)
        pdf.multi_cell(col_width, 5, desc, align="C")

        y_img = pdf.get_y() + 1
        with Image.open(img_path) as im:
            iw, ih = im.size
            ratio = min(col_width / iw, max_img_height / ih)
            w_img = iw * ratio
            h_img = ih * ratio
        x_img = x + (col_width - w_img) / 2
        pdf.image(img_path, x=x_img, y=y_img, w=w_img, h=h_img)

        logging.info("Imagem adicionada: %s", img_path)
        if progress_cb:
            progress_cb(count + 1, total)

    pdf.output(output_pdf)
    logging.info("PDF salvo em %s", output_pdf)

