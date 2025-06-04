import os
import sys
import re
from fpdf import FPDF
from PIL import Image

if getattr(sys, 'frozen', False):
    caminho_base = os.path.dirname(sys.executable)
else:
    caminho_base = os.path.dirname(os.path.abspath(__file__))

pasta_fotos = os.path.join(caminho_base, 'fotos')
saida_pdf_total = os.path.join(caminho_base, "BOOK.pdf")
saida_base_parte = os.path.join(caminho_base, "BOOK_parte_")

def extrair_chave(nome):
    numeros = re.findall(r'\d+', nome)
    return [int(n) for n in numeros] if numeros else [0]

extensoes_validas = ['.jpg', '.jpeg', '.png']
arquivos_imagem = [f for f in os.listdir(pasta_fotos)
                   if os.path.splitext(f)[1].lower() in extensoes_validas]
arquivos_imagem.sort(key=extrair_chave)

largura_pagina = 210
altura_pagina = 297
margem = 10
largura_coluna = (largura_pagina - 3 * margem) / 2
altura_linha = 130
imagens_por_pagina = 4
imagens_por_parte = 50

class PDFLayout(FPDF):
    def header(self):
        logo_path = os.path.join(caminho_base, "logo.png")
        if os.path.exists(logo_path):
            self.image(logo_path, x=10, y=8, w=30)
        self.set_font("Arial", "I", 10)
        self.set_text_color(180, 0, 0)
        self.set_xy(45, 12)
        self.cell(0, 8, "Locações, Projetos e Construções Elétricas")
        self.set_draw_color(180, 0, 0)
        self.set_line_width(0.8)
        self.line(10, 28, 200, 28)
        self.ln(14)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def gerar_pdf(imagens, nome_saida):
    pdf = PDFLayout()
    pdf.set_auto_page_break(auto=True, margin=15)
    for contador, nome_arquivo in enumerate(imagens):
        caminho_imagem = os.path.join(pasta_fotos, nome_arquivo)

        if contador % imagens_por_pagina == 0:
            pdf.add_page()

        posicao = contador % imagens_por_pagina
        linha = posicao // 2
        coluna = posicao % 2

        x = margem + coluna * (largura_coluna + margem)
        y = margem + linha * altura_linha + 30

        nome_base = os.path.splitext(nome_arquivo)[0]
        descricao = nome_base.split("_")[0].strip()

        pdf.set_xy(x, y)
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(largura_coluna, 8, descricao)

        y_imagem = pdf.get_y() + 2
        with Image.open(caminho_imagem) as img:
            iw, ih = img.size
            max_w, max_h = largura_coluna - 5, 85  # proporção ajustada
            ratio = min(max_w / iw, max_h / ih)
            w_img = iw * ratio
            h_img = ih * ratio

        pdf.image(caminho_imagem, x=x, y=y_imagem, w=w_img, h=h_img)
    pdf.output(nome_saida)

def gerar_pdf_total_e_partes():
    print("📦 Gerando PDF completo com layout profissional...")
    gerar_pdf(arquivos_imagem, saida_pdf_total)

    partes = [arquivos_imagem[i:i+imagens_por_parte] for i in range(0, len(arquivos_imagem), imagens_por_parte)]

    for idx, grupo in enumerate(partes, start=1):
        nome_saida = f"{saida_base_parte}{idx}.pdf"
        gerar_pdf(grupo, nome_saida)
        tamanho_mb = os.path.getsize(nome_saida) / (1024 * 1024)
        print(f"🗂 Parte {idx}: {tamanho_mb:.2f} MB -> {nome_saida}")

gerar_pdf_total_e_partes()
