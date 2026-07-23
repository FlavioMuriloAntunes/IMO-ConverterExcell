import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import math
from datetime import datetime
import os

print("Iniciando o sistema...")

# --- VARIÁVEIS GLOBAIS E CONFIGURAÇÕES DA TV ---
caminhos_planilhas_brutas = []
LARGURA_TV = 1920
ALTURA_MINIMA_TV = 1080
MARGEM_X = 30          
MARGEM_Y_TOPO = 170    
MARGEM_Y_RODAPE = 160  
ALTURA_CABECHALHO = 60 

def get_font(tamanho, negrito=False):
    try:
        nome_fonte = "arialbd.ttf" if negrito else "arial.ttf"
        return ImageFont.truetype(nome_fonte, tamanho)
    except IOError:
        return ImageFont.load_default()

def processar_texto_vaga(texto, max_caracteres):
    if len(texto) > max_caracteres:
        return texto[:max_caracteres-3] + "..."
    return texto

def gerar_imagem_tv(lista_vagas, pasta_destino):
    total_vagas = len(lista_vagas)
    if total_vagas == 0:
        lista_vagas = ["NENHUMA VAGA ENCONTRADA"]
        total_vagas = 1

    qtd_colunas = 4            
    max_chars = 40             
    altura_linha = 60          
    tamanho_fonte_vaga = 26    
    tamanho_fonte_cabecalho = 32

    linhas_necessarias = math.ceil(total_vagas / qtd_colunas)
    if linhas_necessarias == 0: linhas_necessarias = 1
    
    altura_calculada = MARGEM_Y_TOPO + ALTURA_CABECHALHO + (linhas_necessarias * altura_linha) + MARGEM_Y_RODAPE
    altura_final_imagem = max(ALTURA_MINIMA_TV, altura_calculada)

    largura_tabela = LARGURA_TV - (MARGEM_X * 2)
    largura_coluna = largura_tabela / qtd_colunas

    fonte_titulo = get_font(48, negrito=True)
    fonte_data = get_font(30, negrito=True)
    fonte_cabecalho = get_font(tamanho_fonte_cabecalho, negrito=True)
    fonte_vaga = get_font(tamanho_fonte_vaga, negrito=False)

    meses_pt = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
        5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
        9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    agora = datetime.now()
    data_hoje = f"{agora.day} DE {meses_pt[agora.month]} DE {agora.year}"
    
    texto_titulo = "VAGAS DE TRABALHO DISPONÍVEIS - AGÊNCIA DO TRABALHADOR"
    texto_data = f"HOJE: {data_hoje}"

    img = Image.new('RGB', (LARGURA_TV, altura_final_imagem), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    # Topo
    bbox_titulo = draw.textbbox((0, 0), texto_titulo, font=fonte_titulo)
    largura_texto_titulo = bbox_titulo[2] - bbox_titulo[0]
    draw.text(((LARGURA_TV - largura_texto_titulo) / 2, 40), texto_titulo, font=fonte_titulo, fill='#103560')

    bbox_data = draw.textbbox((0, 0), texto_data, font=fonte_data)
    largura_texto_data = bbox_data[2] - bbox_data[0]
    draw.text(((LARGURA_TV - largura_texto_data) / 2, 105), texto_data, font=fonte_data, fill='#333333')

    # Cabeçalho
    y_atual = MARGEM_Y_TOPO
    for col in range(qtd_colunas):
        x_esq = MARGEM_X + (col * largura_coluna)
        x_dir = x_esq + largura_coluna
        
        draw.rectangle([x_esq, y_atual, x_dir, y_atual + ALTURA_CABECHALHO], fill='#103560', outline='#103560', width=2)
        
        texto_cab = "VAGAS DISPONÍVEIS"
        bbox_cab = draw.textbbox((0, 0), texto_cab, font=fonte_cabecalho)
        w_cab = bbox_cab[2] - bbox_cab[0]
        offset_y_cab = (ALTURA_CABECHALHO - (bbox_cab[3] - bbox_cab[1])) / 2
        draw.text((x_esq + (largura_coluna - w_cab)/2, y_atual + offset_y_cab - 4), texto_cab, font=fonte_cabecalho, fill='white')

    y_atual += ALTURA_CABECHALHO

    # Linhas da Tabela
    for idx, vaga in enumerate(lista_vagas):
        coluna_atual = idx // linhas_necessarias
        linha_atual = idx % linhas_necessarias
        
        x_esq = MARGEM_X + (coluna_atual * largura_coluna)
        x_dir = x_esq + largura_coluna
        y_linha = y_atual + (linha_atual * altura_linha)
        
        cor_fundo = '#FFFFFF' if linha_atual % 2 == 0 else '#F4F4F4'
        draw.rectangle([x_esq, y_linha, x_dir, y_linha + altura_linha], fill=cor_fundo, outline='#DDDDDD', width=1)
        
        texto_vaga_formatado = processar_texto_vaga(vaga, max_chars)
        bbox_vaga = draw.textbbox((0, 0), texto_vaga_formatado, font=fonte_vaga)
        w_vaga = bbox_vaga[2] - bbox_vaga[0]
        
        offset_y_texto = (altura_linha - (bbox_vaga[3] - bbox_vaga[1])) / 2
        draw.text((x_esq + (largura_coluna - w_vaga)/2, y_linha + offset_y_texto - 4), texto_vaga_formatado, font=fonte_vaga, fill='black')

    # Logos no Rodapé Dinâmico
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
        pos_y = altura_final_imagem - altura_logo - 30
        
        img.paste(logo_agencia, (pos_x_inicial, pos_y), logo_agencia)
        img.paste(logo_pref, (pos_x_inicial + largura_agencia + espacamento, pos_y), logo_pref)
        
    except Exception as e:
        print(f"Erro ao inserir logos: {e}")

    nome_arquivo = os.path.join(pasta_destino, "Tabela_TV_Completa.png")
    img.save(nome_arquivo)

def iniciar_conversao():
    if not caminhos_planilhas_brutas:
        messagebox.showwarning("Atenção", "Por favor, selecione as planilhas primeiro!")
        return
    
    palavras_ignoradas = ['cargo', 'vaga', 'função', 'vagas', 'ocupação', 'descrição', 'descricao', 'cbo']
    lista_vagas_limpa = []
    arquivos_processados = 0
    relatorio = [] # Guarda o histórico do que aconteceu em cada arquivo
    
    # Processa cada arquivo individualmente com isolamento de erros
    for caminho in caminhos_planilhas_brutas:
        nome_arquivo = os.path.basename(caminho)
        
        try:
            df = pd.read_excel(caminho, header=None)
            
            if len(df.columns) < 4:
                relatorio.append(f"❌ {nome_arquivo}: Ignorado (Tem menos de 4 colunas)")
                continue

            vagas_brutas = df.iloc[:, 3].dropna().tolist()
            
            vagas_encontradas = 0
            vagas_novas_adicionadas = 0
            
            for v in vagas_brutas:
                texto_bruto = str(v).strip()
                if texto_bruto.lower() not in palavras_ignoradas and texto_bruto != "":
                    texto_padronizado = texto_bruto.title()
                    vagas_encontradas += 1
                    
                    if texto_padronizado not in lista_vagas_limpa:
                        lista_vagas_limpa.append(texto_padronizado)
                        vagas_novas_adicionadas += 1

            relatorio.append(f"✅ {nome_arquivo}: {vagas_encontradas} lidas ({vagas_novas_adicionadas} únicas)")
            arquivos_processados += 1
            
        except Exception as e:
            relatorio.append(f"❌ {nome_arquivo}: Falha na leitura do Excel")
            print(f"Erro detalhado no arquivo {nome_arquivo}: {e}")

    # Se nenhum arquivo deu certo, avisa o usuário e para
    if arquivos_processados == 0 and len(lista_vagas_limpa) == 0:
        mensagem_falha = "Nenhuma vaga foi encontrada nas planilhas.\n\nResumo:\n" + "\n".join(relatorio)
        messagebox.showerror("Erro na Extração", mensagem_falha)
        return

    # Se deu certo, desenha a imagem final
    try:
        pasta_destino = os.path.dirname(caminhos_planilhas_brutas[0])
        gerar_imagem_tv(lista_vagas_limpa, pasta_destino)
        
        resumo_final = "\n".join(relatorio)
        messagebox.showinfo(
            "Conversão Concluída", 
            f"Imagem criada com sucesso!\nSalva em: {pasta_destino}\n\n"
            f"Vagas totais sem repetição: {len(lista_vagas_limpa)}\n\n"
            f"Relatório de Leitura:\n{resumo_final}"
        )
        
    except Exception as e:
        messagebox.showerror("Erro de Desenho", f"Falha ao tentar gerar a imagem PNG:\n{str(e)}")

def selecionar_arquivos():
    global caminhos_planilhas_brutas
    caminhos = filedialog.askopenfilenames(
        title="Selecione as Planilhas Brutas",
        filetypes=[("Arquivos Excel", "*.xls *.xlsx")]
    )
    if caminhos:
        caminhos_planilhas_brutas = list(caminhos)
        qtd = len(caminhos_planilhas_brutas)
        if qtd == 1:
            label_arquivo.config(text="1 arquivo selecionado.", fg="#103560")
        else:
            label_arquivo.config(text=f"{qtd} arquivos selecionados.", fg="#103560")

# --- INTERFACE GRÁFICA (GUI) ---
janela = tk.Tk()
janela.title("Gerador de Tabelas para TV")
janela.geometry("450x250")
janela.eval('tk::PlaceWindow . center')
janela.configure(bg="#ffffff")

label_titulo = tk.Label(janela, text="Gerador de Vagas para TV", font=("Arial", 14, "bold"), bg="#ffffff")
label_titulo.pack(pady=15)

btn_selecionar = tk.Button(janela, text="📁 Selecionar Planilhas (Segure CTRL)", command=selecionar_arquivos, font=("Arial", 10))
btn_selecionar.pack(pady=10)

label_arquivo = tk.Label(janela, text="Nenhum arquivo selecionado.", font=("Arial", 9), bg="#ffffff", fg="gray")
label_arquivo.pack(pady=5)

btn_converter = tk.Button(janela, text="📺 Gerar Tabela Dinâmica PNG", command=iniciar_conversao, font=("Arial", 11, "bold"), bg="#103560", fg="white")
btn_converter.pack(pady=20)

janela.mainloop()