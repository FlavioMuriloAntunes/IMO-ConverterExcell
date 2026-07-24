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

def measure_text(text, font, draw):
    try:
        return draw.textbbox((0, 0), text, font=font)[2]
    except:
        return font.getlength(text)

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

    img_temp = Image.new('RGB', (10, 10))
    draw_temp = ImageDraw.Draw(img_temp)

    melhor_layout = None
    min_vagas_removidas = 999999
    melhor_listas = ([], [])

    for linhas in range(12, 24):
        cols_c = math.ceil(len(lista_com_exp) / linhas) if tem_com else 0
        cols_s = math.ceil(len(lista_sem_exp) / linhas) if tem_sem else 0
        
        total_cols = cols_c + cols_s
        if total_cols == 0: total_cols = 1
        
        largura_col = largura_tabela / total_cols
        altura_lin = area_util_y / linhas
        
        tamanho_fonte = min(42, max(20, int(altura_lin * 0.6)))
        if tamanho_fonte < 20: continue 
        
        fonte = get_font(tamanho_fonte)
        largura_max_texto = largura_col - 16 
        
        removidas_neste_teste = 0
        com_validas = []
        for v in lista_com_exp:
            if measure_text(v, fonte, draw_temp) <= largura_max_texto:
                com_validas.append(v)
            else:
                removidas_neste_teste += 1
                
        sem_validas = []
        for v in lista_sem_exp:
            if measure_text(v, fonte, draw_temp) <= largura_max_texto:
                sem_validas.append(v)
            else:
                removidas_neste_teste += 1
                
        if removidas_neste_teste < min_vagas_removidas:
            min_vagas_removidas = removidas_neste_teste
            melhor_layout = {
                'linhas': linhas,
                'cols_com': cols_c,
                'cols_sem': cols_s,
                'total_cols': total_cols,
                'largura_coluna': largura_col,
                'altura_linha': altura_lin,
                'tamanho_fonte': tamanho_fonte
            }
            melhor_listas = (com_validas, sem_validas)
            
            if min_vagas_removidas == 0:
                break

    vagas_com_finais, vagas_sem_finais = melhor_listas
    layout = melhor_layout
    
    secoes = []
    x_atual = MARGEM_X
    
    if tem_com:
        larg_secao = layout['cols_com'] * layout['largura_coluna']
        secoes.append({'titulo': "COM EXPERIÊNCIA", 'vagas': vagas_com_finais, 'x_esq': x_atual, 'largura': larg_secao, 'cols': layout['cols_com']})
        x_atual += larg_secao 
        
    if tem_sem:
        larg_secao = layout['cols_sem'] * layout['largura_coluna']
        secoes.append({'titulo': "SEM EXPERIÊNCIA", 'vagas': vagas_sem_finais, 'x_esq': x_atual, 'largura': larg_secao, 'cols': layout['cols_sem']})

    fonte_titulo = get_font(46, negrito=True)
    fonte_data = get_font(28, negrito=True)
    tamanho_fonte_cabecalho = min(42, max(22, int(layout['tamanho_fonte'] * 1.3)))
    fonte_cabecalho = get_font(tamanho_fonte_cabecalho, negrito=True)
    fonte_vaga = get_font(layout['tamanho_fonte'], negrito=False)
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

    # 3. PREENCHIMENTO CONTÍNUO (Remoção total de buracos brancos)
    for sec in secoes:
        largura_col_sec = sec['largura'] / sec['cols']
        
        # Desenhamos o bloco inteiro (borda externa da categoria)
        draw.rectangle([sec['x_esq'], y_atual, sec['x_esq'] + sec['largura'], y_atual + (layout['linhas'] * layout['altura_linha'])], outline='#DDDDDD', width=1)

        # Desenhamos célula por célula preenchendo todos os "buracos", mesmo que não haja vaga neles
        for col in range(sec['cols']):
            for lin in range(layout['linhas']):
                
                # A mágica do preenchimento: se for a última célula e não tiver vaga, nós apenas desenhamos ela em branco para manter a tabela bonita!
                idx = (col * layout['linhas']) + lin 
                
                x_esq = sec['x_esq'] + (col * largura_col_sec)
                y_linha = y_atual + (lin * layout['altura_linha'])
                x_dir = x_esq + largura_col_sec
                y_baixo = y_linha + layout['altura_linha']
                
                cor_fundo = '#FFFFFF' if lin % 2 == 0 else '#F4F4F4'
                
                # Desenha TODAS as células
                draw.rectangle([x_esq, y_linha, x_dir, y_baixo], fill=cor_fundo, outline='#DDDDDD', width=1)
                
                # Se tiver vaga pra essa célula, nós escrevemos
                if idx < len(sec['vagas']):
                    vaga = sec['vagas'][idx]
                    try:
                        bbox = draw.textbbox((0, 0), vaga, font=fonte_vaga)
                        offset_y = (layout['altura_linha'] - (bbox[3] - bbox[1])) / 2
                        largura_txt = bbox[2] - bbox[0]
                    except:
                        offset_y = layout['altura_linha'] * 0.2
                        largura_txt = fonte_vaga.getlength(vaga)
                        
                    draw.text((x_esq + (largura_col_sec - largura_txt)/2, y_linha + offset_y - 4), vaga, font=fonte_vaga, fill='black')

    # 4. Divisória Central (Desenhada no lugar exato da união)
    if tem_com and tem_sem:
        x_div = secoes[1]['x_esq'] 
        draw.line([(x_div, MARGEM_Y_TOPO), (x_div, y_atual + (layout['linhas'] * layout['altura_linha']))], fill='#103560', width=4)

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
    
    return min_vagas_removidas, len(vagas_com_finais), len(vagas_sem_finais)

def iniciar_conversao():
    if not caminho_com_exp and not caminho_sem_exp:
        messagebox.showwarning("Atenção", "Selecione pelo menos uma das planilhas para gerar a imagem!")
        return
    
    try:
        lista_com_exp = extrair_vagas(caminho_com_exp) if caminho_com_exp else []
        lista_sem_exp = extrair_vagas(caminho_sem_exp) if caminho_sem_exp else []

        pasta_destino = os.path.dirname(caminho_com_exp if caminho_com_exp else caminho_sem_exp)
        
        removidas, qtd_com, qtd_sem = gerar_imagem_tv(lista_com_exp, lista_sem_exp, pasta_destino)
        
        msg_sucesso = f"Imagem criada com sucesso!\nSalva em: {pasta_destino}\n\nResultados na Tela:\n✅ {qtd_com} Vagas COM Experiência\n✅ {qtd_sem} Vagas SEM Experiência"
        
        if removidas > 0:
            msg_sucesso += f"\n\n⚠️ Atenção: {removidas} vaga(s) precisaram ser ocultadas do painel por serem excessivamente grandes para a tela."
            
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