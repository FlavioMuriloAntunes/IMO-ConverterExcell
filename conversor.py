import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import math
from datetime import datetime
import os

print("Iniciando o sistema...")

# --- VARIÁVEIS GLOBAIS E CONFIGURAÇÕES DA TV ---
caminho_com_exp = ""
caminho_sem_exp = ""

LARGURA_TV = 1920
ALTURA_TV = 1080  
MARGEM_X = 0           
MARGEM_Y_TOPO = 135    
MARGEM_Y_RODAPE = 140  
ALTURA_CABECHALHO = 55 

def get_font(tamanho, negrito=False):
    try:
        nome_fonte = "arialbd.ttf" if negrito else "arial.ttf"
        return ImageFont.truetype(nome_fonte, tamanho)
    except IOError:
        return ImageFont.load_default()

def abreviar_nome_vaga(texto):
    if not texto:
        return texto
        
    palavras = texto.split()
    if len(palavras) > 0:
        primeira = palavras[0].upper()
        
        abrevs = {
            "TÉCNICO": "Téc.", "TECNICO": "Téc.", "TÉCNICA": "Téc.", "TECNICA": "Téc.",
            "OPERADOR": "Op.", "OPERADORA": "Op.",
            "ASSISTENTE": "Ass.", "ASSIST.": "Ass.",
            "AUXILIAR": "Aux.", 
            "AJUDANTE": "Ajud.",
            "ATENDENTE": "Atend.",
            "ENCARREGADO": "Enc.", "ENCARREGADA": "Enc.",
            "COORDENADOR": "Coord.", "COORDENADORA": "Coord.",
            "ADMINISTRATIVO": "Adm.", "ADMINISTRATIVA": "Adm.", "ADMINISTRADOR": "Adm.",
            "MECÂNICO": "Mec.", "MECANICO": "Mec.",
            "MOTORISTA": "Mot.",
            "ANALISTA": "Anal.",
            "CONSULTOR": "Cons.", "CONSULTORA": "Cons.",
            "VENDEDOR": "Vend.", "VENDEDORA": "Vend.",
            "SUPERVISOR": "Sup.", "SUPERVISORA": "Sup.",
            "ESPECIALISTA": "Esp.",
            "INSPETOR": "Insp.", "INSPETORA": "Insp.",
            "REPOSITOR": "Rep.",
            "GERENTE": "Ger.",
            "EMPREGADO": "Emp.", "EMPREGADA": "Emp.",
            "CONFERENTE": "Conf.",
            "MONTADOR": "Mont.",
            "MARCENEIRO": "Marc.",
            "ELETRICISTA": "Elet."
        }
        
        if primeira in abrevs:
            palavras[0] = abrevs[primeira]
            
    return " ".join(palavras)

def truncar_texto_para_caber(texto, font, draw, largura_maxima):
    try:
        largura_atual = draw.textbbox((0, 0), texto, font=font)[2]
    except:
        largura_atual = font.getlength(texto)
        
    if largura_atual <= largura_maxima:
        return texto
        
    texto_cortado = texto
    while len(texto_cortado) > 0:
        texto_cortado = texto_cortado[:-1]
        teste_texto = texto_cortado + "..."
        try:
            largura_teste = draw.textbbox((0, 0), teste_texto, font=font)[2]
        except:
            largura_teste = font.getlength(teste_texto)
            
        if largura_teste <= largura_maxima:
            return teste_texto
            
    return "..."

def extrair_vagas(caminho):
    if not caminho: return []
    palavras_ignoradas = ['cargo', 'vaga', 'função', 'vagas', 'ocupação', 'descrição', 'descricao', 'cbo', 'nan']
    lista_limpa = []
    
    try:
        df = pd.read_excel(caminho, header=None)
    except Exception:
        try:
            df = pd.read_html(caminho)[0]
        except Exception:
            raise ValueError(f"O arquivo '{os.path.basename(caminho)}' está corrompido.")

    if len(df.columns) < 4:
        raise ValueError(f"O arquivo '{os.path.basename(caminho)}' possui menos de 4 colunas.")

    vagas_brutas = df.iloc[:, 3].dropna().tolist()
    
    for v in vagas_brutas:
        texto_bruto = str(v).strip()
        if texto_bruto.lower() not in palavras_ignoradas and texto_bruto != "":
            texto_padronizado = texto_bruto.title()
            if texto_padronizado not in lista_limpa:
                lista_limpa.append(texto_padronizado)
                
    return lista_limpa

def gerar_imagem_tv(lista_com_exp, lista_sem_exp, pasta_destino):
    
    lista_com_exp = [abreviar_nome_vaga(v) for v in lista_com_exp]
    lista_sem_exp = [abreviar_nome_vaga(v) for v in lista_sem_exp]

    tem_com = len(lista_com_exp) > 0
    tem_sem = len(lista_sem_exp) > 0
    if not tem_com and not tem_sem:
        lista_sem_exp = ["NENHUMA VAGA ENCONTRADA HOJE"]
        tem_sem = True

    area_util_y = ALTURA_TV - MARGEM_Y_TOPO - ALTURA_CABECHALHO - MARGEM_Y_RODAPE
    largura_tabela = LARGURA_TV - (MARGEM_X * 2)

    # Travas Fixas de Layout (Garantindo que fique Legível)
    ALTURA_MINIMA_CELULA = 42 
    TAMANHO_MINIMO_FONTE = 20 
    
    # O máximo de linhas que cabem de forma confortável e espaçada
    linhas_maximas = int(area_util_y / ALTURA_MINIMA_CELULA)
    
    # FORÇAMOS O LIMITE MÁXIMO DE COLUNAS AQUI (Deixando as colunas Com Experiência mais largas)
    if tem_com and tem_sem:
        cols_s = math.ceil(len(lista_sem_exp) / linhas_maximas)
        if cols_s > 6: cols_s = 6 # Trava SEM EXPERIENCIA em no máximo 6 colunas
        
        cols_c = math.ceil(len(lista_com_exp) / linhas_maximas)
        if cols_c > 4: cols_c = 4 # Trava COM EXPERIENCIA em no máximo 4 colunas
        
        total_cols = cols_c + cols_s
    else:
        total_cols = math.ceil(max(len(lista_com_exp), len(lista_sem_exp)) / linhas_maximas)
        if total_cols > 8: total_cols = 8
        cols_c = total_cols if tem_com else 0
        cols_s = total_cols if tem_sem else 0

    largura_col_global = largura_tabela / total_cols
    altura_lin_global = area_util_y / linhas_maximas
    tamanho_fonte_global = min(42, max(TAMANHO_MINIMO_FONTE, int(altura_lin_global * 0.55)))

    # Corte silencioso das vagas que ultrapassam as colunas/linhas permitidas
    limite_vagas_com = cols_c * linhas_maximas
    limite_vagas_sem = cols_s * linhas_maximas
    
    vagas_com_finais = lista_com_exp[:limite_vagas_com]
    vagas_sem_finais = lista_sem_exp[:limite_vagas_sem]

    secoes = []
    x_atual = MARGEM_X
    
    if tem_com:
        larg_secao = cols_c * largura_col_global
        secoes.append({'titulo': "COM EXPERIÊNCIA", 'vagas': vagas_com_finais, 'x_esq': x_atual, 'largura': larg_secao, 'cols': cols_c})
        x_atual += larg_secao 
        
    if tem_sem:
        larg_secao = cols_s * largura_col_global
        secoes.append({'titulo': "SEM EXPERIÊNCIA", 'vagas': vagas_sem_finais, 'x_esq': x_atual, 'largura': larg_secao, 'cols': cols_s})

    fonte_titulo = get_font(46, negrito=True)
    fonte_data = get_font(28, negrito=True)
    tamanho_fonte_cabecalho = min(42, max(24, int(tamanho_fonte_global * 1.3)))
    fonte_cabecalho = get_font(tamanho_fonte_cabecalho, negrito=True)
    fonte_vaga = get_font(tamanho_fonte_global, negrito=False)
    fonte_aviso = get_font(24, negrito=False)

    meses_pt = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL', 5: 'MAIO', 6: 'JUNHO',
        7: 'JULHO', 8: 'AGOSTO', 9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    agora = datetime.now()
    texto_titulo = "VAGAS DE TRABALHO DISPONÍVEIS - AGÊNCIA DO TRABALHADOR"
    texto_data = f"HOJE: {agora.day} DE {meses_pt[agora.month]} DE {agora.year}"

    img = Image.new('RGB', (LARGURA_TV, ALTURA_TV), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    # 1. Topo 
    try: bbox_titulo = draw.textbbox((0, 0), texto_titulo, font=fonte_titulo)
    except: bbox_titulo = [0, 0, fonte_titulo.getlength(texto_titulo), 46]
    draw.text(((LARGURA_TV - (bbox_titulo[2] - bbox_titulo[0])) / 2, 20), texto_titulo, font=fonte_titulo, fill='#103560')

    try: bbox_data = draw.textbbox((0, 0), texto_data, font=fonte_data)
    except: bbox_data = [0, 0, fonte_data.getlength(texto_data), 28]
    draw.text(((LARGURA_TV - (bbox_data[2] - bbox_data[0])) / 2, 80), texto_data, font=fonte_data, fill='#333333')

    # 2. Desenhando os Cabeçalhos 
    y_atual = MARGEM_Y_TOPO
    for sec in secoes:
        x_esq = sec['x_esq']
        x_dir = x_esq + sec['largura']
        draw.rectangle([x_esq, y_atual, x_dir, y_atual + ALTURA_CABECHALHO], fill='#103560', outline='white', width=2)
        try: bbox = draw.textbbox((0, 0), sec['titulo'], font=fonte_cabecalho)
        except: bbox = [0, 0, fonte_cabecalho.getlength(sec['titulo']), 30]
        draw.text((x_esq + (sec['largura'] - (bbox[2] - bbox[0]))/2, y_atual + 10), sec['titulo'], font=fonte_cabecalho, fill='white')
        
    y_atual += ALTURA_CABECHALHO

    # 3. PREENCHIMENTO DE VAGAS 
    for sec in secoes:
        if sec['cols'] == 0: continue
        largura_col_sec = sec['largura'] / sec['cols']
        respiro_lateral = 12 
        
        for idx, vaga in enumerate(sec['vagas']):
            col = idx // linhas_maximas
            lin = idx % linhas_maximas
            
            x_esq = sec['x_esq'] + (col * largura_col_sec)
            y_linha = y_atual + (lin * altura_lin_global)
            x_dir = x_esq + largura_col_sec
            y_baixo = y_linha + altura_lin_global
            
            cor_fundo = '#FFFFFF' if lin % 2 == 0 else '#F4F4F4'
            draw.rectangle([x_esq, y_linha, x_dir, y_baixo], fill=cor_fundo, outline='#DDDDDD', width=1)
            
            texto_seguro = truncar_texto_para_caber(vaga, fonte_vaga, draw, largura_col_sec - respiro_lateral)
            
            try:
                bbox = draw.textbbox((0, 0), texto_seguro, font=fonte_vaga)
                offset_y = (altura_lin_global - (bbox[3] - bbox[1])) / 2
                largura_txt = bbox[2] - bbox[0]
            except:
                offset_y = altura_lin_global * 0.2
                largura_txt = fonte_vaga.getlength(texto_seguro)
                
            draw.text((x_esq + (largura_col_sec - largura_txt)/2, y_linha + offset_y - 4), texto_seguro, font=fonte_vaga, fill='black')

    # 4. Divisória Central 
    if tem_com and tem_sem:
        x_div = secoes[1]['x_esq']
        linhas_usadas = 0
        if len(vagas_com_finais) > 0 or len(vagas_sem_finais) > 0:
            linhas_necessarias_esq = min(linhas_maximas, len(vagas_com_finais)) if cols_c == 1 else linhas_maximas
            linhas_necessarias_dir = min(linhas_maximas, len(vagas_sem_finais)) if cols_s == 1 else linhas_maximas
            linhas_usadas = max(linhas_necessarias_esq, linhas_necessarias_dir)
            if linhas_usadas > 0:
                draw.line([(x_div, MARGEM_Y_TOPO), (x_div, y_atual + (linhas_usadas * altura_lin_global))], fill='#103560', width=4)

    # 5. Logos no Rodapé 
    try:
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_logo_pref = os.path.join(diretorio_atual, 'assets', 'giphy.webp')
        caminho_logo_agencia = os.path.join(diretorio_atual, 'assets', 'logo_agencia.png')
        
        logo_pref = Image.open(caminho_logo_pref).convert("RGBA")
        logo_agencia = Image.open(caminho_logo_agencia).convert("RGBA")
        
        altura_logo = 100 
        
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

    # 6. Aviso no final da página 
    texto_aviso = "* As vagas estão sujeitas a limite de encaminhamentos e podem ser encerradas a qualquer momento."
    try: bbox_aviso = draw.textbbox((0, 0), texto_aviso, font=fonte_aviso)
    except: bbox_aviso = [0, 0, fonte_aviso.getlength(texto_aviso), 24]
    draw.text(((LARGURA_TV - (bbox_aviso[2] - bbox_aviso[0])) / 2, ALTURA_TV - 30), texto_aviso, font=fonte_aviso, fill='#555555')

    nome_arquivo = os.path.join(pasta_destino, "Tabela_TV_Completa.png")
    img.save(nome_arquivo)

def iniciar_conversao():
    if not caminho_com_exp and not caminho_sem_exp:
        messagebox.showwarning("Atenção", "Selecione pelo menos uma das planilhas para gerar a imagem!")
        return
    
    try:
        lista_com_exp = extrair_vagas(caminho_com_exp) if caminho_com_exp else []
        lista_sem_exp = extrair_vagas(caminho_sem_exp) if caminho_sem_exp else []

        pasta_destino = os.path.dirname(caminho_com_exp if caminho_com_exp else caminho_sem_exp)
        
        gerar_imagem_tv(lista_com_exp, lista_sem_exp, pasta_destino)
        
        msg_sucesso = f"Imagem criada com sucesso!\nSalva em: {pasta_destino}"
        messagebox.showinfo("Sucesso", msg_sucesso)
        
    except Exception as e:
        messagebox.showerror("Erro na Extração", f"Ocorreu um erro ao processar as planilhas:\n{str(e)}")

def sel_com_exp():
    global caminho_com_exp
    caminho = filedialog.askopenfilename(title="Selecione a Planilha COM Experiência", filetypes=[("Excel", "*.xls *.xlsx")])
    if caminho:
        caminho_com_exp = caminho
        lbl_com.config(text=f"📁 {os.path.basename(caminho)}", fg="green")

def sel_sem_exp():
    global caminho_sem_exp
    caminho = filedialog.askopenfilename(title="Selecione a Planilha SEM Experiência", filetypes=[("Excel", "*.xls *.xlsx")])
    if caminho:
        caminho_sem_exp = caminho
        lbl_sem.config(text=f"📁 {os.path.basename(caminho)}", fg="green")

# --- INTERFACE GRÁFICA (GUI) ---
janela = tk.Tk()
janela.title("Gerador de Tabelas para TV")
janela.geometry("500x320")
janela.eval('tk::PlaceWindow . center')
janela.configure(bg="#ffffff")

label_titulo = tk.Label(janela, text="Gerador de Vagas para TV", font=("Arial", 14, "bold"), bg="#ffffff")
label_titulo.pack(pady=15)

btn_sem = tk.Button(janela, text="Selecionar Planilha SEM Experiência", command=sel_sem_exp, font=("Arial", 10), bg="#F0F4F8")
btn_sem.pack(pady=5)
lbl_sem = tk.Label(janela, text="Nenhum arquivo selecionado.", font=("Arial", 8), bg="#ffffff", fg="gray")
lbl_sem.pack(pady=2)

btn_com = tk.Button(janela, text="Selecionar Planilha COM Experiência", command=sel_com_exp, font=("Arial", 10), bg="#F0F4F8")
btn_com.pack(pady=5)
lbl_com = tk.Label(janela, text="Nenhum arquivo selecionado.", font=("Arial", 8), bg="#ffffff", fg="gray")
lbl_com.pack(pady=2)

btn_converter = tk.Button(janela, text="📺 Gerar Tabela Dinâmica PNG", command=iniciar_conversao, font=("Arial", 11, "bold"), bg="#103560", fg="white")
btn_converter.pack(pady=20)

janela.mainloop()