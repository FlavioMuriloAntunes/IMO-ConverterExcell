import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import math
from datetime import datetime
import os

print("Iniciando o sistema de Carrossel...")

# --- VARIÁVEIS GLOBAIS ---
caminhos = {
    "SEM_EXP": "",
    "COM_EXP": "",
    "PCD": "",
    "APRENDIZ": "",
    "ESTAGIO": ""  # <-- Nova categoria adicionada
}

LARGURA_TV = 1920
ALTURA_TV = 1080  
MARGEM_X = 50           
MARGEM_Y_TOPO = 160    
MARGEM_Y_RODAPE = 160  
ALTURA_CABECHALHO = 80 

def get_font(tamanho, negrito=False):
    try:
        nome_fonte = "arialbd.ttf" if negrito else "arial.ttf"
        return ImageFont.truetype(nome_fonte, tamanho)
    except IOError:
        return ImageFont.load_default()

def abreviar_nome_vaga(texto):
    if not texto: return texto
    palavras = texto.split()
    if len(palavras) > 0:
        primeira = palavras[0].upper()
        abrevs = {
            "TÉCNICO": "Téc.", "TECNICO": "Téc.", "TÉCNICA": "Téc.", "TECNICA": "Téc.",
            "OPERADOR": "Op.", "OPERADORA": "Op.",
            "ASSISTENTE": "Ass.", "ASSIST.": "Ass.",
            "AUXILIAR": "Aux.", "AJUDANTE": "Ajud.", "ATENDENTE": "Atend.",
            "ENCARREGADO": "Enc.", "ENCARREGADA": "Enc.",
            "COORDENADOR": "Coord.", "COORDENADORA": "Coord.",
            "ADMINISTRATIVO": "Adm.", "ADMINISTRATIVA": "Adm.", "ADMINISTRADOR": "Adm.",
            "MECÂNICO": "Mec.", "MECANICO": "Mec.", "MOTORISTA": "Mot.",
            "ANALISTA": "Anal.", "CONSULTOR": "Cons.", "CONSULTORA": "Cons.",
            "VENDEDOR": "Vend.", "VENDEDORA": "Vend.",
            "SUPERVISOR": "Sup.", "SUPERVISORA": "Sup.", "ESPECIALISTA": "Esp.",
            "INSPETOR": "Insp.", "INSPETORA": "Insp.", "REPOSITOR": "Rep.",
            "GERENTE": "Ger.", "EMPREGADO": "Emp.", "EMPREGADA": "Emp.",
            "CONFERENTE": "Conf.", "MONTADOR": "Mont.", "MARCENEIRO": "Marc.",
            "ELETRICISTA": "Elet."
        }
        if primeira in abrevs:
            palavras[0] = abrevs[primeira]
    return " ".join(palavras)

def truncar_texto_para_caber(texto, font, draw, largura_maxima):
    try: largura_atual = draw.textbbox((0, 0), texto, font=font)[2]
    except: largura_atual = font.getlength(texto)
    if largura_atual <= largura_maxima: return texto
        
    texto_cortado = texto
    while len(texto_cortado) > 0:
        texto_cortado = texto_cortado[:-1]
        teste_texto = texto_cortado + "..."
        try: largura_teste = draw.textbbox((0, 0), teste_texto, font=font)[2]
        except: largura_teste = font.getlength(teste_texto)
        if largura_teste <= largura_maxima: return teste_texto
    return "..."

def extrair_vagas(caminho):
    if not caminho: return []
    palavras_ignoradas = ['cargo', 'vaga', 'função', 'vagas', 'ocupação', 'descrição', 'descricao', 'cbo', 'nan']
    lista_limpa = []
    try: df = pd.read_excel(caminho, header=None)
    except Exception:
        try: df = pd.read_html(caminho)[0]
        except Exception: return []

    if len(df.columns) < 4: return []
    vagas_brutas = df.iloc[:, 3].dropna().tolist()
    
    for v in vagas_brutas:
        texto_bruto = str(v).strip()
        if texto_bruto.lower() not in palavras_ignoradas and texto_bruto != "":
            texto_padronizado = texto_bruto.title()
            if texto_padronizado not in lista_limpa:
                lista_limpa.append(texto_padronizado)
    return lista_limpa

def desenhar_slide(titulo_secao, lista_vagas, cor_tema):
    lista_vagas = [abreviar_nome_vaga(v) for v in lista_vagas]
    if not lista_vagas:
        lista_vagas = ["NENHUMA VAGA DISPONÍVEL NO MOMENTO"]

    img = Image.new('RGB', (LARGURA_TV, ALTURA_TV), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    area_util_y = ALTURA_TV - MARGEM_Y_TOPO - ALTURA_CABECHALHO - MARGEM_Y_RODAPE
    largura_tabela = LARGURA_TV - (MARGEM_X * 2)

    ALTURA_MINIMA_CELULA = 55 
    TAMANHO_MINIMO_FONTE = 28 
    
    linhas_maximas = int(area_util_y / ALTURA_MINIMA_CELULA)
    cols_necessarias = math.ceil(len(lista_vagas) / linhas_maximas)
    if cols_necessarias == 0: cols_necessarias = 1
    if cols_necessarias > 5: cols_necessarias = 5 
    
    largura_col_global = largura_tabela / cols_necessarias
    altura_lin_global = area_util_y / linhas_maximas
    tamanho_fonte_global = min(50, max(TAMANHO_MINIMO_FONTE, int(altura_lin_global * 0.55)))

    limite_vagas = cols_necessarias * linhas_maximas
    vagas_finais = lista_vagas[:limite_vagas]

    fonte_titulo = get_font(52, negrito=True)
    fonte_data = get_font(32, negrito=True)
    fonte_cabecalho = get_font(42, negrito=True)
    fonte_vaga = get_font(tamanho_fonte_global, negrito=False)
    fonte_aviso = get_font(26, negrito=False)

    meses_pt = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL', 5: 'MAIO', 6: 'JUNHO',
        7: 'JULHO', 8: 'AGOSTO', 9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    agora = datetime.now()
    texto_titulo = "VAGAS DE TRABALHO DISPONÍVEIS - AGÊNCIA DO TRABALHADOR"
    texto_data = f"HOJE: {agora.day} DE {meses_pt[agora.month]} DE {agora.year}"

    # Topo
    try: bbox_titulo = draw.textbbox((0, 0), texto_titulo, font=fonte_titulo)
    except: bbox_titulo = [0, 0, fonte_titulo.getlength(texto_titulo), 52]
    draw.text(((LARGURA_TV - (bbox_titulo[2] - bbox_titulo[0])) / 2, 25), texto_titulo, font=fonte_titulo, fill=cor_tema)

    try: bbox_data = draw.textbbox((0, 0), texto_data, font=fonte_data)
    except: bbox_data = [0, 0, fonte_data.getlength(texto_data), 32]
    draw.text(((LARGURA_TV - (bbox_data[2] - bbox_data[0])) / 2, 90), texto_data, font=fonte_data, fill='#333333')

    # Cabeçalho da Categoria 
    y_atual = MARGEM_Y_TOPO
    draw.rectangle([MARGEM_X, y_atual, LARGURA_TV - MARGEM_X, y_atual + ALTURA_CABECHALHO], fill=cor_tema, outline='white', width=2)
    try: bbox = draw.textbbox((0, 0), titulo_secao, font=fonte_cabecalho)
    except: bbox = [0, 0, fonte_cabecalho.getlength(titulo_secao), 42]
    draw.text((MARGEM_X + (largura_tabela - (bbox[2] - bbox[0]))/2, y_atual + 15), titulo_secao, font=fonte_cabecalho, fill='white')
    
    y_atual += ALTURA_CABECHALHO

    # Preenchendo as Vagas
    respiro_lateral = 15 
    for idx, vaga in enumerate(vagas_finais):
        col = idx // linhas_maximas
        lin = idx % linhas_maximas
        
        x_esq = MARGEM_X + (col * largura_col_global)
        y_linha = y_atual + (lin * altura_lin_global)
        x_dir = x_esq + largura_col_global
        y_baixo = y_linha + altura_lin_global
        
        cor_fundo = '#FFFFFF' if lin % 2 == 0 else '#F4F4F4'
        draw.rectangle([x_esq, y_linha, x_dir, y_baixo], fill=cor_fundo, outline='#DDDDDD', width=1)
        
        texto_seguro = truncar_texto_para_caber(vaga, fonte_vaga, draw, largura_col_global - respiro_lateral)
        
        try:
            bbox = draw.textbbox((0, 0), texto_seguro, font=fonte_vaga)
            offset_y = (altura_lin_global - (bbox[3] - bbox[1])) / 2
            largura_txt = bbox[2] - bbox[0]
        except:
            offset_y = altura_lin_global * 0.2
            largura_txt = fonte_vaga.getlength(texto_seguro)
            
        draw.text((x_esq + (largura_col_global - largura_txt)/2, y_linha + offset_y - 6), texto_seguro, font=fonte_vaga, fill='black')

    # Logos no Rodapé
    try:
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_logo_pref = os.path.join(diretorio_atual, 'assets', 'giphy.webp')
        caminho_logo_agencia = os.path.join(diretorio_atual, 'assets', 'logo_agencia.png')
        
        logo_pref = Image.open(caminho_logo_pref).convert("RGBA")
        logo_agencia = Image.open(caminho_logo_agencia).convert("RGBA")
        
        altura_logo = 110 
        
        prop_pref = altura_logo / float(logo_pref.size[1])
        largura_pref = int(float(logo_pref.size[0]) * float(prop_pref))
        logo_pref = logo_pref.resize((largura_pref, altura_logo), Image.Resampling.LANCZOS)
        
        prop_agencia = altura_logo / float(logo_agencia.size[1])
        largura_agencia = int(float(logo_agencia.size[0]) * float(prop_agencia))
        logo_agencia = logo_agencia.resize((largura_agencia, altura_logo), Image.Resampling.LANCZOS)
        
        espacamento = 60
        largura_total_logos = largura_pref + espacamento + largura_agencia
        pos_x_inicial = (LARGURA_TV - largura_total_logos) // 2
        pos_y_logos = ALTURA_TV - altura_logo - 45
        
        img.paste(logo_agencia, (pos_x_inicial, pos_y_logos), logo_agencia)
        img.paste(logo_pref, (pos_x_inicial + largura_agencia + espacamento, pos_y_logos), logo_pref)
    except Exception:
        pass

    # Aviso final
    texto_aviso = "* As vagas estão sujeitas a limite de encaminhamentos e podem ser encerradas a qualquer momento."
    try: bbox_aviso = draw.textbbox((0, 0), texto_aviso, font=fonte_aviso)
    except: bbox_aviso = [0, 0, fonte_aviso.getlength(texto_aviso), 26]
    draw.text(((LARGURA_TV - (bbox_aviso[2] - bbox_aviso[0])) / 2, ALTURA_TV - 35), texto_aviso, font=fonte_aviso, fill='#555555')

    return img

def iniciar_conversao():
    if not any(caminhos.values()):
        messagebox.showwarning("Atenção", "Selecione pelo menos uma planilha para gerar a apresentação!")
        return
    
    try:
        pasta_base = ""
        for caminho in caminhos.values():
            if caminho:
                pasta_base = os.path.dirname(caminho)
                break
        
        pasta_destino = os.path.join(pasta_base, "Slides_TV")
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        slides_gerados = []
        
        # 1. Slide SEM Experiência (Azul Padrão)
        if caminhos["SEM_EXP"]:
            vagas = extrair_vagas(caminhos["SEM_EXP"])
            if vagas:
                img = desenhar_slide("VAGAS SEM EXPERIÊNCIA", vagas, '#103560')
                img.save(os.path.join(pasta_destino, "1_Sem_Experiencia.png"))
                slides_gerados.append(img)

        # 2. Slide COM Experiência (Laranja/Dourado Escuro)
        if caminhos["COM_EXP"]:
            vagas = extrair_vagas(caminhos["COM_EXP"])
            if vagas:
                img = desenhar_slide("VAGAS COM EXPERIÊNCIA", vagas, '#b35900')
                img.save(os.path.join(pasta_destino, "2_Com_Experiencia.png"))
                slides_gerados.append(img)

        # 3. Slide PCD (Verde Escuro)
        if caminhos["PCD"]:
            vagas = extrair_vagas(caminhos["PCD"])
            if vagas:
                img = desenhar_slide("VAGAS EXCLUSIVAS PARA PCD", vagas, '#006622')
                img.save(os.path.join(pasta_destino, "3_PCD.png"))
                slides_gerados.append(img)

        # 4. Slide JOVEM APRENDIZ (Roxo/Vinho)
        if caminhos["APRENDIZ"]:
            vagas = extrair_vagas(caminhos["APRENDIZ"])
            if vagas:
                img = desenhar_slide("VAGAS PARA JOVEM APRENDIZ", vagas, '#4d004d')
                img.save(os.path.join(pasta_destino, "4_Jovem_Aprendiz.png"))
                slides_gerados.append(img)
                
        # 5. Slide ESTÁGIO (Verde-Água / Teal) <-- Novo Slide Gerado
        if caminhos["ESTAGIO"]:
            vagas = extrair_vagas(caminhos["ESTAGIO"])
            if vagas:
                img = desenhar_slide("VAGAS PARA ESTÁGIO", vagas, '#008080')
                img.save(os.path.join(pasta_destino, "5_Estagio.png"))
                slides_gerados.append(img)

        if not slides_gerados:
            messagebox.showwarning("Atenção", "Nenhuma vaga válida foi encontrada nas planilhas selecionadas.")
            return

        caminho_gif = os.path.join(pasta_base, "Apresentacao_Vagas.gif")
        if len(slides_gerados) > 1:
            slides_gerados[0].save(
                caminho_gif,
                save_all=True,
                append_images=slides_gerados[1:],
                duration=8000, 
                loop=0 
            )
        else:
            slides_gerados[0].save(os.path.join(pasta_base, "Apresentacao_Unica.png"))

        msg_sucesso = f"Apresentação gerada com sucesso!\n\n"
        msg_sucesso += f"📁 Imagens separadas salvas na pasta:\n{pasta_destino}\n\n"
        if len(slides_gerados) > 1:
            msg_sucesso += f"🎬 Arquivo Animado gerado:\n{caminho_gif}"
            
        messagebox.showinfo("Sucesso", msg_sucesso)
        
    except Exception as e:
        messagebox.showerror("Erro na Extração", f"Ocorreu um erro ao processar as planilhas:\n{str(e)}")

def selecionar_arquivo(categoria, label):
    caminho = filedialog.askopenfilename(title=f"Selecione a Planilha", filetypes=[("Excel", "*.xls *.xlsx")])
    if caminho:
        caminhos[categoria] = caminho
        label.config(text=f"📁 {os.path.basename(caminho)}", fg="green")

# --- INTERFACE GRÁFICA (GUI) ---
janela = tk.Tk()
janela.title("Gerador de Carrossel para TV")
janela.geometry("550x500") # <-- Aumentado para caber o 5º botão
janela.eval('tk::PlaceWindow . center')
janela.configure(bg="#ffffff")

label_titulo = tk.Label(janela, text="Gerador de Apresentação (Slides)", font=("Arial", 14, "bold"), bg="#ffffff")
label_titulo.pack(pady=10)

frame_botoes = tk.Frame(janela, bg="#ffffff")
frame_botoes.pack(pady=10)

# Sem Exp
btn_sem = tk.Button(frame_botoes, text="Planilha SEM Experiência", command=lambda: selecionar_arquivo("SEM_EXP", lbl_sem), font=("Arial", 10), bg="#F0F4F8", width=25)
btn_sem.grid(row=0, column=0, pady=5, padx=5)
lbl_sem = tk.Label(frame_botoes, text="Nenhum", font=("Arial", 8), bg="#ffffff", fg="gray")
lbl_sem.grid(row=0, column=1, pady=5, sticky="w")

# Com Exp
btn_com = tk.Button(frame_botoes, text="Planilha COM Experiência", command=lambda: selecionar_arquivo("COM_EXP", lbl_com), font=("Arial", 10), bg="#F0F4F8", width=25)
btn_com.grid(row=1, column=0, pady=5, padx=5)
lbl_com = tk.Label(frame_botoes, text="Nenhum", font=("Arial", 8), bg="#ffffff", fg="gray")
lbl_com.grid(row=1, column=1, pady=5, sticky="w")

# PCD
btn_pcd = tk.Button(frame_botoes, text="Planilha PCD", command=lambda: selecionar_arquivo("PCD", lbl_pcd), font=("Arial", 10), bg="#F0F4F8", width=25)
btn_pcd.grid(row=2, column=0, pady=5, padx=5)
lbl_pcd = tk.Label(frame_botoes, text="Nenhum", font=("Arial", 8), bg="#ffffff", fg="gray")
lbl_pcd.grid(row=2, column=1, pady=5, sticky="w")

# Aprendiz
btn_aprendiz = tk.Button(frame_botoes, text="Planilha Jovem Aprendiz", command=lambda: selecionar_arquivo("APRENDIZ", lbl_aprendiz), font=("Arial", 10), bg="#F0F4F8", width=25)
btn_aprendiz.grid(row=3, column=0, pady=5, padx=5)
lbl_aprendiz = tk.Label(frame_botoes, text="Nenhum", font=("Arial", 8), bg="#ffffff", fg="gray")
lbl_aprendiz.grid(row=3, column=1, pady=5, sticky="w")

# Estágio <-- Novo Botão
btn_estagio = tk.Button(frame_botoes, text="Planilha Estágio", command=lambda: selecionar_arquivo("ESTAGIO", lbl_estagio), font=("Arial", 10), bg="#F0F4F8", width=25)
btn_estagio.grid(row=4, column=0, pady=5, padx=5)
lbl_estagio = tk.Label(frame_botoes, text="Nenhum", font=("Arial", 8), bg="#ffffff", fg="gray")
lbl_estagio.grid(row=4, column=1, pady=5, sticky="w")

lbl_aviso = tk.Label(janela, text="*Deixe em branco as categorias que não tiverem vagas hoje.", font=("Arial", 8, "italic"), bg="#ffffff", fg="gray")
lbl_aviso.pack(pady=5)

btn_converter = tk.Button(janela, text="🎬 Gerar Apresentação / GIF", command=iniciar_conversao, font=("Arial", 11, "bold"), bg="#103560", fg="white", height=2)
btn_converter.pack(pady=15)

janela.mainloop()