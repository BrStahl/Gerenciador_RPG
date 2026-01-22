import random as rd
import tkinter as tk
from tkinter import ttk, messagebox,simpledialog
import mysql.connector
import database as db
import Personagem as ps
import function as fc
from PIL import Image, ImageTk
import io
from tkinter import filedialog
import random
import ast # Adicione no topo do arquivo
import os

class TooltipRPG:
    def __init__(self, tree):
        self.tree = tree
        self.tip_window = None

    def mostrar(self, texto, x, y):
        if self.tip_window or not texto: return
        self.tip_window = tw = tk.Toplevel(self.tree)
        tw.wm_overrideredirect(True) # Remove bordas da janela
        tw.wm_geometry(f"+{x+15}+{y+10}")
        tk.Label(tw, text=texto, background="#ffffe0", relief='solid', borderwidth=1,
                 justify='left', font=("Arial", 9)).pack()

    def esconder(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except: pass
            self.tip_window = None



# Cria os Slots do Personagem
def atribuir_slots_por_nivel(id_p, nivel_p, cursor):
    PROGRESSAO_FULLCASTER = {
        1: [2],           # 2 slots de 1º nível
        2: [3],           # 3 slots de 1º nível
        3: [4, 2],        # 4 de 1º nível, 2 de 2º nível
        4: [4, 3],        # 4 de 1º nível, 3 de 2º nível
        5: [4, 3, 2],     # 4 de 1º, 3 de 2º, 2 de 3º nível
    }
    """Insere os slots iniciais baseados no nível"""
    slots = PROGRESSAO_FULLCASTER.get(nivel_p, [0])

    for i, qtd_max in enumerate(slots):
        nivel_magia = i + 1
        sql = """INSERT INTO Espacos_Magia (id_personagem, nivel_magia, slots_max, slots_atuais)
                 VALUES (%s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE slots_max=%s, slots_atuais=%s"""
        cursor.execute(sql, (id_p, nivel_magia, qtd_max, qtd_max, qtd_max, qtd_max))

# Limpa os campos
def limpa_campos():
    Nome.delete(0,tk.END)

    combo_racas.set("")
    combo_s_racas.set("")
    combo_classe.set("")
    combo_Sub_classe.set("")
    combo_alinhamentos.set("")

    pts_For.set(8)
    pts_Dex.set(8)
    pts_Con.set(8)
    pts_Int.set(8)
    pts_Sab.set(8)
    pts_Car.set(8)

    qtd_pontos.set(15)

# Controla a distribuição de pontos
def altera_pontos(atri,qtd):
    pts_restantes = qtd_pontos.get()
    qtd_atu_atri = atri.get()

    if qtd > 0 and pts_restantes > 0:
        atri.set(qtd_atu_atri + 1)
        qtd_pontos.set(pts_restantes -1)

        if qtd_pontos.get() == 0:
            messagebox.showinfo("Aviso","Todos os pontos distribuidos!")

    elif qtd < 0 and qtd_atu_atri > 0 and qtd_atu_atri > 8:
        atri.set(qtd_atu_atri - 1)
        qtd_pontos.set(pts_restantes + 1)

# Busca Itens do Inventario
def busca_invetario(id_raca):
    conn = db.conexao()
    cursor = conn.cursor()

    query = "SELECT nome_item,quantidade FROM Itens_Iniciais WHERE id_raca = %s"
    cursor.execute(query, (id_raca,))
    itens = cursor.fetchall()

    inventario_Inicial = []

    for i in itens:
        if i[1] > 1:
            inventario_Inicial.append(f" • {i[0]} ({i[1]})")
        else:
            inventario_Inicial.append(f" • {i[0]}")

    return "\n".join(inventario_Inicial)

# Salvar Personagem
def salvar_personagem():
    # Dados Basicos Personagem
    Nome_per = Nome.get() # Nome
    raca = combo_racas.get() # Raça
    sraca = combo_s_racas.get() # Sub_Raça
    classe = combo_classe.get() # Classe
    Sub_Classe = combo_Sub_classe.get() # Sub-Classe
    alinhamentos = combo_alinhamentos.get() # Alinhamento
    XP = 0
    Lvl = 1
    Ouro = 0.00

    conn = db.conexao()
    cursor = conn.cursor()

    query = "SELECT Forca, Inteligencia, Constituicao, Destreza, Sabedoria, Carisma FROM Racas WHERE nome_raca = %s"
    cursor.execute(query, (raca,))
    bonus = cursor.fetchone()
    Forca = pts_For.get() + bonus[0]
    Inteligencia = pts_Int.get() + bonus[1]
    Constituicao = pts_Con.get() + bonus[2]
    Destreza = pts_Dex.get() + bonus[3]
    Sabedoria = pts_Sab.get() + bonus[4]
    Carisma = pts_Car.get() + bonus[5]
    Carga_Max = Forca * 7
    Carga_Atual = 0.00

    query2 = "SELECT dado_vida FROM Classes WHERE nome_classe = %s"
    cursor.execute(query2, (classe,))
    dado_vida = cursor.fetchone()
    vida_base = dado_vida[0] if dado_vida else 8
    if vida_base == '1d12':
        Mod_Vida = (Constituicao - 10 ) // 2
        Vida = 12 + Mod_Vida
    elif vida_base == '1d8' or vida_base == 8:
        Mod_Vida = (Constituicao - 10 ) // 2
        Vida = 8 + Mod_Vida
    elif vida_base == '1d10':
        Mod_Vida = (Constituicao - 10 ) // 2
        Vida = 10 + Mod_Vida
    elif vida_base == '1d6':
        Mod_Vida = (Constituicao - 10 ) // 2
        Vida = 6 + Mod_Vida

    # Modificadores
    Mod_Des =  (Destreza - 10 ) // 2

    Vida_Max = Vida
    Vida_Atual = Vida_Max
    Defesa = Mod_Des + 10
    Iniciativa = Mod_Des

    try:
        sql = """INSERT INTO
                    Personagens (id_personagem,nome,raca,sub_raca,classe,sub_classe,alinhamento,Forca,Inteligencia,Destreza,Constituicao,Carisma,Sabedoria,Vida_Max,Vida_Atual,defesa,Iniciativa,Carga_max,Carga_atual,XP,Lvl,Ouro)
                VALUES (
                    '', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
        """
        valores = (
            Nome_per, raca, sraca, classe, Sub_Classe, alinhamentos,
            Forca, Inteligencia, Destreza, Constituicao, Carisma, Sabedoria,
            Vida_Max, Vida_Atual, Defesa, Iniciativa, Carga_Max, Carga_Atual, XP, Lvl, Ouro
        )
        cursor.execute(sql, valores)
        conn.commit()


        # CAPTURA O ID GERADO PELO BANCO DE DADOS
        id_novo_personagem = cursor.lastrowid

        # ATRIBUI OS SLOTS DE MAGIA USANDO O NOVO ID
        atribuir_slots_por_nivel(id_novo_personagem, Lvl, cursor)

        conn.commit()
        messagebox.showinfo("Sucesso","Herói Gravado com Sucesso.")
        limpa_campos()
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Erro",f"Erro ao inserir: {e}")
    finally:
        conn.close()

# Carrega lista de Personagens -> Aba Herois
def carregar_personagem():
    for i in tabela_perso.get_children():
        tabela_perso.delete(i)

    conn = db.conexao()
    cursor = conn.cursor()

    query = "SELECT id_Personagem,nome,Vida_Max, Defesa,classe,sub_classe,raca, Lvl FROM Personagens"
    cursor.execute(query)
    Herois = cursor.fetchall()

    for p in Herois:
        tabela_perso.insert("","end",values=p)

    conn.close()

# Carrega lista de Monstros -> Bestiario
def carregar_inimigos():

    for i in tabela_inimigo.get_children():
        tabela_inimigo.delete(i)

    conn = db.conexao()
    cursor = conn.cursor()

    query = "SELECT id_inimigo,nome,tipo, hp_max,ca, forca,nivel_desafio FROM inimigos"
    cursor.execute(query)
    Herois = cursor.fetchall()

    for p in Herois:
        tabela_inimigo.insert("","end",values=p)

    conn.close()

# Atualiza Foto
def atualizar_foto_personagem(id_personagem):
    caminho_img = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])

    if caminho_img:
        with open(caminho_img, 'rb') as arquivo:
            binario_puro = arquivo.read() # Bytes reais

        conn = db.conexao()
        cursor = conn.cursor()

        # %s SEM ASPAS. O driver do MySQL cuida da conversão binária
        sql = "UPDATE Personagens SET foto_personagem = %s WHERE id_personagem = %s"

        # Os valores devem ser passados como o segundo argumento do execute
        cursor.execute(sql, (binario_puro, id_personagem))

        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Foto salva corretamente!")

# Exibe Ficha do Personagem
def mostrar_ficha(id_personagem):

    def ajustar_janela_ao_conteudo(event):
        # Obtém o widget da aba selecionada atualmente
        aba_selecionada = event.widget.nametowidget(event.widget.select())

        # Força a atualização dos widgets internos para calcular o tamanho real
        aba_selecionada.update_idletasks()

        # Pega a largura e altura necessária para essa aba específica
        largura = aba_selecionada.winfo_reqwidth() + 20 # +20 de margem de segurança
        altura = aba_selecionada.winfo_reqheight() + 50 # +50 para compensar o cabeçalho das abas

        # Aplica o novo tamanho à janela principal (root)
        # Substitua 'root' pelo nome da sua variável da janela principal se for diferente
        ficha.geometry(f"{largura}x{altura}")

    conn = db.conexao()
    cursor = conn.cursor(dictionary=True)

    query = '''SELECT
                    id_personagem,
                    P.nome,
                    P.raca,
                    CASE
                        WHEN P.sub_raca = "" or sub_raca IS NULL THEN '-----'
                        ELSE P.sub_raca
                    END AS sub_raca,
                    P.classe,
                    P.sub_classe,
                    P.alinhamento,
                    P.Forca,
                    P.Inteligencia,
                    P.Destreza,
                    P.Constituicao,
                    P.Carisma,
                    P.Sabedoria,
                    P.Vida_max,
                    P.Vida_Atual,
                    R. Velocidade,
                    P.defesa,
                    CASE
                        WHEN P.Iniciativa <= 0 THEN 0
                        ELSE P.Iniciativa
                    END AS Iniciativa,
                    P.Carga_max,
                    P.Carga_atual,
                    P.XP,
                    P.Lvl,
                    P.Ouro,
                    P.foto_personagem
                FROM Personagens P
                JOIN racas R
                    ON R.nome_raca = P.raca
                WHERE id_personagem = %s
            '''

    cursor.execute(query, (id_personagem,))
    p = cursor.fetchone()


    ficha = tk.Toplevel(janela)
    ficha.title(f"Ficha: {p['nome']}")
    ficha.geometry("720x450")
    ficha.grid_rowconfigure(0,weight=1)
    ficha.grid_columnconfigure(0,weight=3)


    notebook = ttk.Notebook(ficha)
    notebook.grid(row=0,column=0,sticky='nsew')

    notebook.bind("<<NotebookTabChanged>>", lambda e: ajustar_janela_ao_conteudo(e))
    # Abas Superior
    aba_dados_basicos = tk.Frame(notebook)
    aba_informacoes = tk.Frame(notebook)
    aba_inventario = tk.Frame(notebook)
    aba_magias = tk.Frame(notebook)

    # Exbição das Abas
    notebook.add(aba_dados_basicos,text="Dados Basicos")
    notebook.add(aba_informacoes,text="Informações")
    notebook.add(aba_inventario,text="Inventário")
    notebook.add(aba_magias,text="Magias")

    # Dados Ficha
    # --- ABA DADOS BÁSICOS (Modificada para incluir a foto) ---
    frame_ficha = tk.Frame(aba_dados_basicos)
    frame_ficha.pack(fill="both", expand=True, padx=5, pady=5)

    # 1. FRAME: DADOS BÁSICOS (Linha 0, Coluna 0)
    f_dados_Basicos = tk.LabelFrame(frame_ficha, text=" Dados Básicos ", font=("Arial", 8, "bold"))
    f_dados_Basicos.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    tk.Label(f_dados_Basicos, text=f"{p['nome'].upper()} - Lvl: {p['Lvl']}", font=("Arial", 11, "bold")).grid(row=0, column=0, pady=5, sticky='w', padx=5)
    tk.Label(f_dados_Basicos, text=f"Raça: {p['raca']} | Sub-Raça: {p['sub_raca']}", font=("Arial", 9, "bold")).grid(row=1, column=0, pady=2, sticky='w', padx=5)
    tk.Label(f_dados_Basicos, text=f"Classe: {p['classe']} | Arquetipo: {p['sub_classe']}", font=("Arial", 9, "bold")).grid(row=2, column=0, pady=2, sticky='w', padx=5)
    tk.Label(f_dados_Basicos, text=f"Ouro: {p['Ouro']}$", font=("Arial", 9, "bold")).grid(row=4, column=0, pady=2, sticky='w', padx=5)
    tk.Label(f_dados_Basicos, text=f"HP: {p['Vida_Atual']} / {p['Vida_max']}", font=("Arial", 8, "bold")).grid(row=5, column=0, sticky='w', padx=5)
    barra_hp = ttk.Progressbar(f_dados_Basicos, style="HP.Horizontal.TProgressbar", orient="horizontal", length=250, mode="determinate")
    barra_hp["maximum"] = p['Vida_max']
    barra_hp["value"] = p['Vida_Atual']
    barra_hp.grid(row=6, column=0, sticky='ew', padx=5, pady=5)

    # 2. FRAME: ATRIBUTOS (Linha 1, Coluna 0)
    # Colocando logo abaixo dos dados básicos para eliminar o espaço em branco
    f_atributos = tk.LabelFrame(frame_ficha, text=" Atributos ", font=("Arial", 8, "bold"))
    f_atributos.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    tk.Label(f_atributos, text=f"Def: {p['defesa']} | Ini: {p['Iniciativa']} | Vel: {p['Velocidade']}", font=("Arial", 9)).grid(row=0, column=0, sticky='w', padx=5)
    tk.Label(f_atributos, text=f"For: {p['Forca']} | Int: {p['Inteligencia']} | Sab: {p['Sabedoria']}", font=("Arial", 9)).grid(row=1, column=0, sticky='w', padx=5)
    tk.Label(f_atributos, text=f"Con: {p['Constituicao']} | Car: {p['Carisma']} | Des: {p['Destreza']}", font=("Arial", 9)).grid(row=2, column=0, sticky='w', padx=5)
    lbl_peso_status = tk.Label(f_atributos, text=f"Pes: {p['Carga_atual']} / {p['Carga_max']}kg", font=("Arial", 9))
    lbl_peso_status.grid(row=3, column=0, sticky='w', padx=5)

    # 3. FRAME: FOTO (Coluna 1, Ocupando 2 Linhas com Rowspan)
    f_foto_lb = tk.LabelFrame(frame_ficha, text=" Retrato do Herói ", font=("Arial", 8, "bold"))
    f_foto_lb.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")

    # Lógica da Foto (mantendo o seu fix do b'x89)
    if p['foto_personagem']:
        try:
            dados = p['foto_personagem']
            if isinstance(dados, str) and dados.startswith("b'"):
                import ast
                dados = ast.literal_eval(dados)

            fluxo_dados = io.BytesIO(dados)
            img_pil = Image.open(fluxo_dados)
            img_pil.thumbnail((220, 260)) # Aumentei um pouco para aproveitar o novo LabelFrame
            foto_tk = ImageTk.PhotoImage(img_pil)

            lbl_foto = tk.Label(f_foto_lb, image=foto_tk)
            lbl_foto.image = foto_tk
            lbl_foto.pack(padx=5, pady=5)
        except Exception as e:
            tk.Label(f_foto_lb, text="[ Erro na Imagem ]").pack()
    else:
        tk.Label(f_foto_lb, text="[ Sem Foto ]", width=25, height=12).pack()
        # --- PAINEL DE MAGIAS RÁPIDAS (Abaixo dos Atributos) ---

    # --- 1. CRIAÇÃO DO FRAME (Dados Básicos) ---
    # Posicionamos na Row 2, abaixo dos Atributos (Row 1)
    frame_magias_rapidas = tk.LabelFrame(frame_ficha, text="Magias Rápidas (Top 3)",font=("Arial",8,"bold"), padx=10, pady=3)
    # Agora o grid funciona, pois frame_ficha só usa grid internamente
    # Posicionamos na Row 2, abaixo dos Atributos (Row 1)
    frame_magias_rapidas.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    def conjurar_pelo_top3(id_p, dados_m):
        """Lógica simplificada para uso em botões de atalho"""
        nome = dados_m['nome_magia']
        nivel = dados_m['nivel']

        if nivel == 0:
            messagebox.showinfo("Truque", f"{nome} lançado!")
            return

        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)

        # Verifica slots
        cursor.execute("SELECT slots_atuais FROM Espacos_Magia WHERE id_personagem = %s AND nivel_magia = %s", (id_p, nivel))
        res = cursor.fetchone()

        if res and res['slots_atuais'] > 0:
            novo_valor = res['slots_atuais'] - 1
            cursor.execute("UPDATE Espacos_Magia SET slots_atuais = %s WHERE id_personagem = %s AND nivel_magia = %s",
                        (novo_valor, id_p, nivel))
            conn.commit()
            messagebox.showinfo("Sucesso", f"{nome} conjurado! Restam {novo_valor} slots de Lvl {nivel}.")
        else:
            messagebox.showwarning("Esgotado", f"Sem slots de nível {nivel}!")

        conn.close()

    def atualizar_painel_top3(id_p):
        """Limpa e reconstrói a lista de magias rápidas"""
        # Limpa widgets antigos
        for widget in frame_magias_rapidas.winfo_children():
            widget.destroy()

        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)

        # Busca as 3 magias de menor nível (mais usadas no dia a dia)
        query = """
            SELECT m.id_magia, m.nome_magia, m.nivel
            FROM magias m
            JOIN magias_conhecidas mc ON m.id_magia = mc.id_magia
            WHERE mc.id_personagem = %s
            ORDER BY m.nivel ASC LIMIT 3
        """
        cursor.execute(query, (id_p,))
        lista_magias = cursor.fetchall()

        if not lista_magias:
            tk.Label(frame_magias_rapidas, text="Grimório vazio.", fg="gray").grid(row=0, column=0)
        else:
            for i, magia in enumerate(lista_magias):
                # Nome da Magia
                lbl = tk.Label(frame_magias_rapidas, text=f"{magia['nome_magia']} (Lvl {magia['nivel']})", font=("Arial", 9))
                lbl.grid(row=i, column=0, sticky="w", pady=2)

                # Botão de Conjuração Rápida
                btn = tk.Button(
                    frame_magias_rapidas,
                    text="⚡",
                    bg="#007bff",
                    fg="white",
                    width=3,
                    command=lambda m=magia: conjurar_pelo_top3(id_p, m)
                )
                btn.grid(row=i, column=1, padx=5, pady=2)
        conn.close()
    atualizar_painel_top3(id_personagem)
    # Botão de carregar imagem dentro do novo LabelFrame
    btn_carregar = tk.Button(f_foto_lb, text="📷 Alterar Foto", font=("Arial", 7),
                            command=lambda: atualizar_foto_personagem(id_personagem))
    btn_carregar.pack(pady=5, fill="x", padx=5)

    # ----------------------------- Aba Informações ------------------------------------------------------------

    # ----------------------------- Dados da Raça --------------------------------------------------------------
    notebook = ttk.Notebook(aba_informacoes)
    notebook.grid(row=0,column=0,sticky='nsew')

    # Abas Superior
    aba_Raca = tk.Frame(notebook)
    aba_classe = tk.Frame(notebook)
    aba_s_classe = tk.Frame(notebook)

    # Exbição das Abas
    notebook.add(aba_Raca,text="Dados Raça")
    notebook.add(aba_classe,text="Dados Classe")
    notebook.add(aba_s_classe,text="Dados Sub-Classe")

    frame_acoes = tk.LabelFrame(aba_Raca,text="Informações",font=("Arial",8,"bold"))
    frame_acoes.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    # Frame "Caracteristicas"
    f_desc = tk.LabelFrame(frame_acoes,text="Caracteristicas da Raça",font=("Arial",7,"bold"))
    f_desc.grid(row=0,column=0,padx=2,pady=2,sticky="nsew")

    descri = "SELECT racas.descricao FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(descri, (id_personagem,))
    descricao = cursor.fetchone()

    if descricao and descricao['descricao']:
        texto_acoes = str(descricao['descricao']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui caracteristicas registradas."

    lbl_desc = tk.Label(f_desc, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_desc.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Idade"
    f_idade = tk.LabelFrame(frame_acoes,text="Idade",font=("Arial",7,"bold"))
    f_idade.grid(row=0,column=1,padx=2,pady=2,sticky="nsew")

    ida = "SELECT racas.Idade FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(ida, (id_personagem,))
    idade = cursor.fetchone()

    if idade and idade['Idade']:
        texto_acoes = str(idade['Idade']).replace('*','').replace(".","").replace("Idade","").replace("_","") # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui idade registradas."

    lbl_idade = tk.Label(f_idade, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_idade.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Altura "
    f_altura = tk.LabelFrame(frame_acoes,text="Altura",font=("Arial",7,"bold"))
    f_altura.grid(row=1,column=0,padx=2,pady=2,sticky="nsew")

    altura = "SELECT racas.Altura FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(altura, (id_personagem,))
    Altura = cursor.fetchone()

    if Altura and Altura['Altura']:
        texto_acoes = str(Altura['Altura']).replace('*','').replace(".","").replace("Tamanho","").replace("_","") # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui altura registradas."

    lbl_alt = tk.Label(f_altura, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_alt.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Alinhamentos "
    f_alinh = tk.LabelFrame(frame_acoes,text="Alinhamentos",font=("Arial",7,"bold"))
    f_alinh.grid(row=1,column=1,padx=2,pady=2,sticky="nsew")

    ali = "SELECT racas.Alinhamentos FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(ali, (id_personagem,))
    alinhamentos = cursor.fetchone()

    if alinhamentos and alinhamentos['Alinhamentos']:
        texto_acoes = str(alinhamentos['Alinhamentos']).replace('*','').replace(".","").replace("Alinhamento","").replace("_","") # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Alinhamentos registrados."

    lbl_ali = tk.Label(f_alinh, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_ali.grid(row=0,column=0,padx=5, pady=5,sticky="nsew")

    # Frame "Visão"
    f_visao = tk.LabelFrame(frame_acoes,text="Visão",font=("Arial",7,"bold"))
    f_visao.grid(row=2,column=0,padx=2,pady=2,sticky="nsew")

    visao = "SELECT racas.Visao FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(visao, (id_personagem,))
    Visao = cursor.fetchone()

    if Visao and Visao['Visao']:
        texto_acoes = str(Visao['Visao']).replace('*','').replace(".","").replace("_Darkvision._","Visão no Escuro: ").replace("_","") # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Visão registradas."

    lbl_visao = tk.Label(f_visao, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_visao.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Idiomas"
    f_lin = tk.LabelFrame(frame_acoes,text="Idiomas",font=("Arial",7,"bold"))
    f_lin.grid(row=2,column=1,padx=2,pady=2,sticky="nsew")

    idioma = "SELECT racas.Linguas FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(idioma, (id_personagem,))
    Lingua = cursor.fetchone()

    if Lingua and Lingua['Linguas']:
        texto_acoes = str(Lingua['Linguas']).replace('*','').replace(".","").replace("","").replace("_","") # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Idiomas registrados."

    lbl_linguas = tk.Label(f_lin, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_linguas.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Habilidades"
    f_hab = tk.LabelFrame(frame_acoes,text="Habilidades",font=("Arial",7,"bold"))
    f_hab.grid(row=3,column=0,padx=2,pady=2,sticky="nsew")

    hab = "SELECT racas.Habilidades FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(hab, (id_personagem,))
    Habilidade = cursor.fetchone()

    if Habilidade and Habilidade['Habilidades']:
        texto_acoes = str(Habilidade['Habilidades']).replace('*','').replace(".","").replace("","").replace("_","") # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Habilidades registradas."

    lbl_hab = tk.Label(f_hab, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_hab.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Velocidade"
    f_velo = tk.LabelFrame(frame_acoes,text="Velocidade",font=("Arial",7,"bold"))
    f_velo.grid(row=3,column=1,padx=2,pady=2,sticky="nsew")

    velo = "SELECT racas.Velocidade_desc FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
    cursor.execute(velo, (id_personagem,))
    Velocidade = cursor.fetchone()

    if Velocidade and Velocidade['Velocidade_desc']:
        texto_acoes = str(Velocidade['Velocidade_desc']).replace('*','').replace(".","").replace("","").replace("_","") # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Idiomas registrados."

    lbl_velo = tk.Label(f_velo, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_velo.grid(row=0,column=0,padx=5, pady=5)

    # ------------------------------------ Dados Da Classe ----------------------------------------------------------
    frame_d_classe = tk.LabelFrame(aba_classe,text="Informações de Classe",font=("Arial",8,"bold"))
    frame_d_classe.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    # Frame "Armadura"
    f_armadura = tk.LabelFrame(frame_d_classe,text="Armadura",font=("Arial",7,"bold"))
    f_armadura.grid(row=0,column=0,padx=2,pady=2,sticky="nsew")

    armor = "SELECT C.armadura FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s"
    cursor.execute(armor, (id_personagem,))
    armadura = cursor.fetchone()

    if armadura and armadura['armadura']:
        texto_acoes = str(armadura['armadura']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Armaduras registradas."

    lbl_armor = tk.Label(f_armadura, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_armor.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Ferramentas"
    f_ferr = tk.LabelFrame(frame_d_classe,text="Ferramentas",font=("Arial",7,"bold"))
    f_ferr.grid(row=0,column=1,padx=2,pady=2,sticky="nsew")

    ferr = "SELECT C.ferramentas FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s"
    cursor.execute(ferr, (id_personagem,))
    ferramentas = cursor.fetchone()

    if ferramentas and ferramentas['ferramentas']:
        texto_acoes = str(ferramentas['ferramentas']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Ferramentas registradas."

    lbl_ferr = tk.Label(f_ferr, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_ferr.grid(row=1,column=0,padx=5, pady=5)

    # Frame "Salvaguardas"
    f_salv = tk.LabelFrame(frame_d_classe,text="Salvaguardas",font=("Arial",7,"bold"))
    f_salv.grid(row=1,column=0,padx=2,pady=2,sticky="nsew")

    salv = "SELECT C.salvaguardas FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s"
    cursor.execute(salv, (id_personagem,))
    salvaguardas = cursor.fetchone()

    if salvaguardas and salvaguardas['salvaguardas']:
        texto_acoes = str(salvaguardas['salvaguardas']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Salvaguardas registradas."

    lbl_salv = tk.Label(f_salv, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_salv.grid(row=1,column=1,padx=5, pady=5)

    # Frame "Pericias"
    f_peri = tk.LabelFrame(frame_d_classe,text="Pericias",font=("Arial",7,"bold"))
    f_peri.grid(row=1,column=1,padx=2,pady=2,sticky="nsew")

    Per = "SELECT C.pericias FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s"
    cursor.execute(Per, (id_personagem,))
    pericias = cursor.fetchone()

    if pericias and pericias['pericias']:
        texto_acoes = str(pericias['pericias']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Pericias registradas."

    lbl_peri = tk.Label(f_peri, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_peri.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Equipamentos"
    f_equi = tk.LabelFrame(frame_d_classe,text="Equipamentos",font=("Arial",7,"bold"))
    f_equi.grid(row=2,column=0,padx=2,pady=2,sticky="nsew")

    ini_equip = "SELECT C.equipamento_inicial FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s"
    cursor.execute(ini_equip, (id_personagem,))
    equip_ini = cursor.fetchone()

    if equip_ini and equip_ini['equipamento_inicial']:
        texto_acoes = str(equip_ini['equipamento_inicial']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Equipamentos registrados."

    lbl_equi = tk.Label(f_equi, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_equi.grid(row=0,column=0,padx=5, pady=5)

    # Frame "Conjuração"
    f_conju = tk.LabelFrame(frame_d_classe,text="Atributos Para Conjuração",font=("Arial",7,"bold"))
    f_conju.grid(row=2,column=1,padx=2,pady=2,sticky="nsew")

    conju = "SELECT C.atributo_conjuracao FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s"
    cursor.execute(conju, (id_personagem,))
    conjuracao = cursor.fetchone()

    if conjuracao and conjuracao['atributo_conjuracao']:
        texto_acoes = str(conjuracao['atributo_conjuracao']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Conjurações registradas."

    lbl_conju = tk.Label(f_conju, text=texto_acoes, wraplength=330, justify="left", anchor="nw")
    lbl_conju.grid(row=0,column=0,padx=5, pady=5)

    # ---------------------------Descrição Sub- Classe--------------------------------------

    frame_s_classe = tk.LabelFrame(aba_s_classe,text="Informações da Sub-Classe",font=("Arial",8,"bold"))
    frame_s_classe.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    f_subcl = tk.LabelFrame(frame_s_classe,text="Descrição Sub-Classe (Arquetipo)",font=("Arial",7,"bold"))
    f_subcl.grid(row=0,column=0,rowspan=3,padx=2,pady=2,sticky="nsew")

    desc_sub = "SELECT sub_classe FROM personagens WHERE id_personagem = %s"
    cursor.execute(desc_sub, (id_personagem,))
    id_sclasse = cursor.fetchone()

    id_sub_classe = "SELECT descricao FROM sub_classes WHERE nome_subclasse = %s"
    cursor.execute(id_sub_classe, (id_sclasse['sub_classe'],))
    descricao_sclass = cursor.fetchone()

    if descricao_sclass and descricao_sclass['descricao']:
        texto_acoes = str(descricao_sclass['descricao']).replace('#','') # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Esta raça não possui Arquetipos registrados."

    lbl_sub = tk.Label(f_subcl, text=texto_acoes, wraplength= 670, justify="left", anchor="nw")
    lbl_sub.grid(row=0,column=0,rowspan=2,padx=5, pady=5)

    # ------------------ Aba Inventario----------------------------------------

    # Frame para a lista e a barra de rolagem
    frame_lista = tk.Frame(aba_inventario)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    # Configuração da Treeview (Colunas)
    colunas = ("Item", "Qtd", "Peso Uni", "Peso Total", "Tipo","Equipado","Slot")
    tabela = ttk.Treeview(frame_lista, columns=colunas, show="headings")

    tabela.heading("Item", text="Item")
    tabela.heading("Qtd", text="Qtd")
    tabela.heading("Peso Uni", text="Peso (Un)")
    tabela.heading("Peso Total", text="Total")
    tabela.heading("Tipo", text="Tipo")
    tabela.heading("Equipado", text="Equipamento")
    tabela.heading("Slot", text="Slot")

    # Ajustando largura das colunas
    tabela.column("Item", width=100)
    tabela.column("Qtd", width=50, anchor="center")
    tabela.column("Peso Uni", width=40, anchor="center")
    tabela.column("Peso Total", width=40, anchor="center")
    tabela.column("Tipo", width=40, anchor="center")
    tabela.column("Equipado", width=40, anchor="center")
    tabela.column("Slot", width=80, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)

    # Barra de Rolagem
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Botões de Ação
    frame_botoes = tk.Frame(aba_inventario)
    frame_botoes.pack(fill="x", padx=10, pady=5)

    tk.Button(frame_botoes, text="➕ Adicionar Item", bg="#28a745", fg="white", command=lambda: abrir_janela_selecao(id_personagem, tabela, lbl_peso_status, p['Carga_max'])).pack(side="left", padx=5)
    tk.Button(frame_botoes, text="➖ Remover", bg="#dc3545", fg="white",command=lambda: remover_item_selecionado(id_personagem, tabela, lbl_peso_status, p['Carga_max'])).pack(side="left", padx=5)

    # Chama a primeira carga de dados assim que abrir a ficha
    atualizar_inventario_e_peso_ui(id_personagem, tabela, lbl_peso_status, p['Carga_max'])

    def ao_clicar_tabela(event):
        item_id = tabela.identify_row(event.y)
        coluna = tabela.identify_column(event.x)

        if not item_id: return

        # Coluna #6 é "Equipamento" (Checkbox)
        if coluna == "#6":
            valores = list(tabela.item(item_id, 'values'))

            # Índice 5 na lista 'values'
            if valores[5] == "☐":
                valores[5] = "☑"
                valores[6] = "Mão Direita" # Define apenas o padrão inicial
            else:
                valores[5] = "☐"
                valores[6] = "" # Limpa o slot se desequipar

            tabela.item(item_id, values=valores)
            # DICA: Aqui você deve chamar o UPDATE no Banco de Dados para 'equipado = 1'

    # --- FUNÇÃO: SELETOR DE SLOT (CORRIGIDA) ---
    def abrir_seletor_slot(event, item_id):
        coluna = tabela.identify_column(event.x)
        x, y, largura, altura = tabela.bbox(item_id, coluna)

        opcoes = ["Mão Direita", "Mão Esquerda", "Costas", "Cinto", "Cabeça", "Corpo"]
        cb_slot = ttk.Combobox(tabela, values=opcoes, state="readonly")
        cb_slot.place(x=x, y=y, width=largura, height=altura)
        cb_slot.focus()

        def fechar_e_salvar(event):
            if not cb_slot.winfo_exists(): return # PROTEÇÃO CONTRA O ERRO

            novo_local = cb_slot.get()
            novos_v = list(tabela.item(item_id, 'values'))
            novos_v[6] = novo_local # Índice 6 é o Slot
            tabela.item(item_id, values=novos_v)

            # SALVAR NO SQL
            conn = db.conexao()
            cursor = conn.cursor()
            cursor.execute("UPDATE Inventario_Personagem SET local_equipado = %s WHERE id_inventario = %s",
                           (novo_local, item_id))
            conn.commit()
            conn.close()
            cb_slot.destroy()

        cb_slot.bind("<<ComboboxSelected>>", fechar_e_salvar)
        # Proteção extra no FocusOut para evitar o "bad window path"
        cb_slot.bind("<FocusOut>", lambda e: cb_slot.destroy() if cb_slot.winfo_exists() else None)

    # --- FUNÇÃO: TOOLTIP COM SELECT ---
    tooltip = TooltipRPG(tabela)

    # --- FUNÇÃO: TOOLTIP COM BUSCA NO BANCO ---
    def monitorar_mouse(event):
        item_id = tabela.identify_row(event.y)
        if item_id:
            conn = db.conexao()
            cursor = conn.cursor(dictionary=True)
            # Busca propriedades e bônus usando o ID do inventário (iid)
            query = """
                SELECT E.Propriedades, E.Dado_dano, E.Tipo_dano
                FROM Inventario_Personagem IP
                JOIN equipamentos E ON IP.id_equipamento = E.id_equipamento
                WHERE IP.id_inventario = %s
            """
            cursor.execute(query, (item_id,))
            res = cursor.fetchone()
            conn.close()

            if res:
                info = f"Dano: {res['Dado_dano']} ({res['Tipo_dano']})\nPropriedades: {res['Propriedades']}"
                tooltip.esconder()
                tooltip.mostrar(info, event.x_root, event.y_root)
        else:
            tooltip.esconder()

    # --- FUNÇÃO: CONSUMIR ITEM ---
    def usar_item_consumivel(id_inventario, valores, id_p, c_max):
        qtd_atual = int(valores[1])
        if qtd_atual > 0:
            nova_qtd = qtd_atual - 1
            conn = db.conexao()
            cursor = conn.cursor()
            if nova_qtd > 0:
                cursor.execute("UPDATE Inventario_Personagem SET quantidade = %s WHERE id_inventario = %s",
                               (nova_qtd, id_inventario))
            else:
                cursor.execute("DELETE FROM Inventario_Personagem WHERE id_inventario = %s", (id_inventario,))
            conn.commit()
            conn.close()
            # Atualiza a interface e o peso total
            atualizar_inventario_e_peso_ui(id_p, tabela, lbl_peso_status, c_max)

    # --- FUNÇÃO: DUPLO CLIQUE (GATEKEEPER) ---
    def ao_dar_duplo_clique(event, id_p, c_max):
        item_id = tabela.focus()
        coluna = tabela.identify_column(event.x)
        if not item_id: return

        valores = list(tabela.item(item_id, 'values'))
        tipo = valores[4] # Índice 4 é o "Tipo"

        # 1. Se for Consumível, chama o diálogo de uso
        if tipo == "Consumivel":
            if messagebox.askyesno("Usar", f"Deseja consumir 1x {valores[0]}?"):
                usar_item_consumivel(item_id, valores, id_p, c_max)
            return

        # 2. Se for Equipamento e estiver equipado (Índice 5), abre o slot
        if coluna == "#7" and valores[5] == "☑":
            abrir_seletor_slot(event, item_id)

    # --- FUNÇÃO: CLIQUE ÚNICO (CHECKBOX) COM UPDATE ---
    def ao_clicar_tabela(event, id_p, c_max):
        item_id = tabela.identify_row(event.y)
        coluna = tabela.identify_column(event.x)
        if not item_id or coluna != "#6": return

        valores = list(tabela.item(item_id, 'values'))
        if valores[5] == "☐":
            valores[5] = "☑"
            valores[6] = "Mão Direita"
            status = 1
        else:
            valores[5] = "☐"
            valores[6] = ""
            status = 0

        tabela.item(item_id, values=valores)
        # Salva no banco de dados
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Inventario_Personagem SET equipado = %s, local_equipado = %s WHERE id_inventario = %s",
                       (status, valores[6], item_id))
        conn.commit()
        conn.close()

    # Bindings com lambda para passar o contexto do personagem atual
    tabela.bind("<ButtonRelease-1>", lambda e: ao_clicar_tabela(e, id_personagem, p['Carga_max']))
    tabela.bind("<Double-1>", lambda e: ao_dar_duplo_clique(e, id_personagem, p['Carga_max']))
    tabela.bind("<Motion>", monitorar_mouse)
    tabela.bind("<Leave>", lambda e: tooltip.esconder())

    conn.close()
    # ------------------------------------------- Aba Magias---------------------------------------

    def carregar_magias_personagem(id_p, tree):
        """Atualiza a lista de magias que o personagem conhece"""
        for i in tree.get_children():
            tree.delete(i)

        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT m.id_magia, m.nome_magia, m.nivel, m.escola,
                m.tempo_conjuracao, m.alcance, m.dano_cura
            FROM magias m
            JOIN magias_conhecidas mc ON m.id_magia = mc.id_magia
            WHERE mc.id_personagem = %s
            ORDER BY m.nivel ASC, m.nome_magia ASC
        """
        cursor.execute(query, (id_p,))
        for m in cursor.fetchall():
            tree.insert("", "end", values=(
                m['id_magia'], m['nome_magia'], m['nivel'],
                m['escola'], m['tempo_conjuracao'], m['alcance'], m['dano_cura']
            ))
        conn.close()

    def realizar_descanso_longo(id_p, tree_magias):
        """Restaura HP e Slots de Magia no Banco de Dados"""
        # Confirmação para evitar cliques acidentais
        if not messagebox.askyesno("Descanso Longo", "Deseja realizar um Descanso Longo?\nIsso restaurará todo o HP e Slots de Magia."):
            return

        conn = db.conexao()
        cursor = conn.cursor()

        try:
            # 1. SQL: Reseta Slots (Atual = Max)
            sql_slots = "UPDATE Espacos_Magia SET slots_atuais = slots_max WHERE id_personagem = %s"
            cursor.execute(sql_slots, (id_p,))

            # 2. SQL: Reseta HP (Atual = Max)
            sql_hp = "UPDATE Personagens SET Vida_Atual = Vida_Max WHERE id_personagem = %s"
            cursor.execute(sql_hp, (id_p,))

            conn.commit()

            # 3. Atualização da Interface
            carregar_magias_personagem(id_p, tree_magias)

            messagebox.showinfo("Descanso", "O herói descansou! Recursos totalmente restaurados.")

            # DICA: Se você tiver uma função que atualiza a barra de vida na tela principal, chame-a aqui.

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao processar descanso: {e}")
        finally:
            conn.close()

    def realizar_conjuracao(id_p, tree):
        """Consome um slot de magia do nível correspondente ao conjurar"""
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma magia!")
            return

        valores = tree.item(selecionado)['values']
        nivel_m = int(valores[2])
        nome_m = valores[1]

        if nivel_m == 0:
            messagebox.showinfo("Truque", f"{nome_m} conjurado!")
            return

        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT slots_atuais FROM Espacos_Magia WHERE id_personagem = %s AND nivel_magia = %s",
                    (id_p, nivel_m))
        res = cursor.fetchone()

        if res and res['slots_atuais'] > 0:
            # Lógica: $Slots_{atuais} = Slots_{atuais} - 1$
            novo_valor = res['slots_atuais'] - 1
            cursor.execute("UPDATE Espacos_Magia SET slots_atuais = %s WHERE id_personagem = %s AND nivel_magia = %s",
                        (novo_valor, id_p, nivel_m))
            conn.commit()
            messagebox.showinfo("Sucesso", f"{nome_m} conjurado! Restam {novo_valor} slots de nível {nivel_m}.")
        else:
            messagebox.showerror("Esgotado", f"Sem espaços de magia de nível {nivel_m}!")
        conn.close()

    def abrir_janela_busca_magias(id_p, tree_principal):
        janela = tk.Toplevel()
        janela.title("Aprender Magia")
        janela.geometry("700x500")
        janela.columnconfigure(0, weight=1)
        janela.rowconfigure(1, weight=1)

        # Busca
        f_busca = tk.Frame(janela)
        f_busca.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        f_busca.columnconfigure(1, weight=1)

        tk.Label(f_busca, text="Filtro:").grid(row=0, column=0)
        ent_f = tk.Entry(f_busca)
        ent_f.grid(row=0, column=1, sticky="ew", padx=5)

        # Resultados
        cols = ("ID", "Nome", "Nível", "Escola")
        t_res = ttk.Treeview(janela, columns=cols, show="headings")
        for c in cols:
            t_res.heading(c, text=c)
            t_res.column(c, width=100, anchor="center")
        t_res.grid(row=1, column=0, sticky="nsew", padx=10)

        def pesquisar(event=None):
            for i in t_res.get_children(): t_res.delete(i)
            c = db.conexao(); cur = c.cursor(dictionary=True)
            cur.execute("SELECT id_magia, nome_magia, nivel, escola FROM magias WHERE nome_magia LIKE %s", (f"%{ent_f.get()}%",))
            for r in cur.fetchall():
                t_res.insert("", "end", values=(r['id_magia'], r['nome_magia'], r['nivel'], r['escola']))
            c.close()

        ent_f.bind("<KeyRelease>", pesquisar)

        def aprender():
            sel = t_res.selection()
            if not sel: return
            val = t_res.item(sel)['values']
            c = db.conexao(); cur = c.cursor()
            try:
                cur.execute("INSERT INTO magias_conhecidas (id_personagem, id_magia) VALUES (%s, %s)", (id_p, val[0]))
                c.commit()
                carregar_magias_personagem(id_p, tree_principal)
                messagebox.showinfo("Sucesso", f"{val[1]} aprendida!")
            except:
                messagebox.showwarning("Erro", "Você já conhece esta magia.")
            finally: c.close()

        tk.Button(janela, text="Aprender Selecionada", bg="#28a745", fg="white", command=aprender).grid(row=2, column=0, pady=10)
        pesquisar()

    # Configurações de peso para expansão
    aba_magias.columnconfigure(0, weight=1)
    aba_magias.rowconfigure(1, weight=1)

    # Frame Superior (Botões)
    frame_topo = tk.Frame(aba_magias)
    frame_topo.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

    tk.Button(frame_topo, text="📖 Aprender Magia", bg="#17a2b8", fg="white",
            command=lambda: abrir_janela_busca_magias(id_personagem, tabela_magias)).grid(row=0, column=0, padx=5)

    # Treeview de Magias Conhecidas
    colunas_m = ("ID", "Nome", "Nível", "Escola", "Tempo", "Alcance", "Dano")
    tabela_magias = ttk.Treeview(aba_magias, columns=colunas_m, show="headings")

    for col in colunas_m:
        tabela_magias.heading(col, text=col)
        tabela_magias.column(col, width=90, anchor="center")

    tabela_magias.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    # Barra de Rolagem
    scroll_m = ttk.Scrollbar(aba_magias, orient="vertical", command=tabela_magias.yview)
    tabela_magias.configure(yscrollcommand=scroll_m.set)
    scroll_m.grid(row=1, column=1, sticky="ns")

    # Botão de Ação Principal
    btn_cast = tk.Button(aba_magias, text="⚡ CONJURAR", bg="#007bff", fg="white", font=("Arial", 11, "bold"),
                        command=lambda: realizar_conjuracao(id_personagem, tabela_magias))
    btn_cast.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

    # 5. NOVO: Botão de Descanso Longo (Linha 3)
    btn_rest = tk.Button(
        aba_magias,
        text="⛺ DESCANSO LONGO (RESTAURAR TUDO)",
        bg="#28a745", # Verde para indicar recuperação
        fg="white",
        font=("Arial", 11, "bold"),
        command=lambda: realizar_descanso_longo(id_personagem, tabela_magias)
    )
    btn_rest.grid(row=3, column=0, sticky="ew", padx=20, pady=(5, 15))
    # Carga inicial
    carregar_magias_personagem(id_personagem,tabela_magias)

# Exibe Ficha do Monstro
def mostra_monstro(id_monstro):
    conn = db.conexao()
    cursor = conn.cursor(dictionary=True)

    query = '''
                SELECT
                nome,
                nivel_desafio,
                tipo,
                hp_max,
                CASE
                    WHEN (forca- 10) / 2  <= 0 or forca  IS NULL THEN 0.00
                    ELSE (forca- 10) / 2
                END AS forca,
                CASE
                    WHEN (destreza - 10) / 2 <= 0 or destreza  IS NULL THEN 0.00
                    ELSE  (destreza - 10) / 2
                END AS destreza,
                CASE
                    WHEN (constituicao - 10) / 2 <= 0 or constituicao  IS NULL THEN 0.00
                    ELSE (constituicao - 10) / 2
                END  AS constituicao,
                CASE
                    WHEN (inteligencia - 10) / 2 <= 0 or inteligencia  IS NULL THEN 0.00
                    ELSE (inteligencia - 10) / 2
                END AS inteligencia,
                CASE
                    WHEN (carisma - 10) / 2 <= 0 or carisma IS NULL THEN 0.00
                    ELSE (carisma - 10) / 2
                END AS carisma,
                CASE
                    WHEN (sabedoria - 10) / 2 <=0 or sabedoria IS NULL THEN 0.00
                    ELSE (sabedoria - 10) / 2
                END AS sabedoria,
                ca AS defesa,
                CASE
                    WHEN (destreza - 10) / 2 <= 0 or destreza  IS NULL THEN 0.00
                    ELSE (destreza - 10) / 2
                END AS iniciativa
            FROM inimigos WHERE id_inimigo = %s'''

    cursor.execute(query, (id_monstro,))
    p = cursor.fetchone()

    ficha = tk.Toplevel(janela)
    ficha.title(f"Inimigo: {p['nome']}")
    ficha.geometry("540x450")
    ficha.grid_rowconfigure(0,weight=1)
    ficha.grid_columnconfigure(0,weight=1)

    # Dados Ficha
    frame_ficha = tk.LabelFrame(ficha,text=f"Inimigo: {p['nome']}",font=("Arial",9,"bold"))
    frame_ficha.grid(row=0,column=0,padx=(3,3),pady=(3,3),sticky="nsew")

    tk.Label(frame_ficha,text=f"{p['nome'].upper()} - Lvl: {p['nivel_desafio']}",font=("Arial",8,"bold")).grid(row=0,column=0,pady=5,sticky='w')
    tk.Label(frame_ficha,text=f"Tipo: {p['tipo']}", font=("Arial",9,"italic")).grid(row=1,column=0,pady=5,sticky='w')

    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure("HP.Horizontal.TProgressbar", background ='green',troughcolor='red')

    tk.Label(frame_ficha,text=f"HP: {p['hp_max']}",font=("Arial",8,"bold")).grid(row=2,column=0,padx=(4,4),sticky='w')

    barra_hp = ttk.Progressbar(frame_ficha,style="HP.Horizontal.TProgressbar",orient="horizontal",length=250,mode="determinate")

    barra_hp["maximum"] = p['hp_max']
    barra_hp["value"] = p['hp_max']
    barra_hp.grid(row=3,column=0,sticky='w')

    frame_status = tk.Frame(frame_ficha)
    frame_status.grid(row=5,column=0)

    tk.Label(frame_status, text=f"Def: {p['defesa']:.2f} | Ini: {p['iniciativa']:.2f}", font=("Arial", 9)).grid(row=0, column=0,sticky='w',padx=(2,2))
    tk.Label(frame_status, text=f"For: {p['forca']:.2f}  | Des: {p['destreza']:.2f}   | Con: {p['constituicao']:.2f}", font=("Arial", 9)).grid(row=1, column=0,sticky='w',padx=(2,2))
    tk.Label(frame_status, text=f"Sab: {p['sabedoria']:.2f} | Car: {p['carisma']:.2f} | Int: {p['inteligencia']:.2f}", font=("Arial", 9)).grid(row=2, column=0,sticky='w',padx=(2,2))

    # ----------------------------- Frame Ações ------------------------------------------------------------

    frame_acoes = tk.LabelFrame(ficha,text="Ações:")
    frame_acoes.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    # Buscamos a descrição que você já traduziu da API
    acoes_sql = "SELECT descricao_acoes FROM inimigos WHERE id_inimigo = %s"
    cursor.execute(acoes_sql, (id_monstro,))
    resultado = cursor.fetchone()

    # 3. Verificação e Exibição
    if resultado and resultado['descricao_acoes']:
        texto_acoes = resultado['descricao_acoes'] # Acessa pela chave, não pelo índice 0
    else:
        texto_acoes = "Este monstro não possui ações especiais registradas."

    # Usamos wraplength=300 para o texto quebrar linha automaticamente
    lbl_desc = tk.Label(frame_acoes, text=texto_acoes, wraplength=250, justify="left", anchor="nw")
    lbl_desc.pack(padx=5, pady=5, expand=True, fill="both")
    conn.close()

# Função auxiliar para buscar os dados (coloque fora da criar_tela_inicio) ---
def obter_contagens_resumo():
    try:
        conn = db.conexao()
        cursor = conn.cursor()

        # Conta heróis
        cursor.execute("SELECT COUNT(*) FROM Personagens")
        total_herois = cursor.fetchone()[0]

        # Conta monstros (ajuste o nome da tabela se for diferente, ex: 'inimigos')
        cursor.execute("SELECT COUNT(*) FROM inimigos")
        total_monstros = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM equipamentos")
        total_equi = cursor.fetchone()[0]

        conn.close()
        return total_herois, total_monstros
    except Exception as e:
        print(f"Erro ao buscar resumo: {e}")
        return 0, 0

# Tela Inicial
def criar_tela_inicio(aba_inicio):

    # 1. CONFIGURAÇÃO DA CITAÇÃO DO DIA
    citacoes = [
        '"A aventura espera por aqueles que ousam buscá-la."',
        '"Role iniciativa! O destino do mundo depende disso."',
        '"Em cada sombra pode se esconder um tesouro ou um dragão."',
        '"A magia é a arte de transformar a vontade em realidade."',
        '"Um grupo unido é mais forte que qualquer muralha."',
        '"Lembre-se: o Mestre sempre tem a última palavra (e o dragão)."',
        '"A melhor história é aquela que escrevemos juntos na mesa."',
        '"Cuidado com o baú que respira,as vezes ele pode ser um mimico"'
    ]

    citacao_do_dia = random.choice(citacoes)

    # 2. CONFIGURAÇÃO DO FUNDO (CANVAS E IMAGEM)
    # Cria um canvas que preenche toda a aba
    canvas = tk.Canvas(aba_inicio, width=720, height=450, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    # 1. Localiza a pasta onde o seu main.py está
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    # 2. Monta o caminho completo para a imagem
    # MUITO IMPORTANTE: Verifique se a extensão é .png ou .webp
    caminho_imagem = os.path.join(diretorio_atual, "fundo_mapa_rpg.png")

    try:
            # 3. Abre a imagem usando o caminho seguro
            img_original = Image.open(caminho_imagem)
            img_fundo = img_original.resize((640, 400), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_fundo)

            canvas.create_image(0, 0, image=img_tk, anchor="nw")
            canvas.image = img_tk
    except Exception as e:
        print(f"Erro ao carregar imagem de fundo: {e}")
        # Fundo de emergência caso a imagem falhe
        canvas.config(bg="#3e2b1f")

    # 3. ADICIONAR A CITAÇÃO DO DIA (SOBRE A IMAGEM)
    # Coloca o texto na parte inferior, centralizado
    canvas.create_text(350, 360, text=citacao_do_dia,
                       font=("Gabriola", 14, "bold"), # Tente fontes como Gabriola, Constantia ou Cambria
                       fill="#000000", # Cor branca para contraste
                       width=600, justify="center")

    # 4. CRIAR OS CARDS DE RESUMO (SOBRE A IMAGEM)
    # Busca os dados atualizados do banco
    herois_qtd, monstros_qtd = obter_contagens_resumo()

    # Cria um frame para agrupar os cards. Usamos uma cor de fundo semi-transparente
    # (no Tkinter, "semi-transparente" é uma cor sólida que combina com o fundo)
    f_cards_container = tk.Frame(canvas, bg="#4e342e", bd=2, relief="ridge")

    # Coloca este frame container "dentro" do canvas, no centro
    canvas.create_window(340, 210, window=f_cards_container, width=240, height=110)

    # Estilos para os textos dos cards
    estilo_titulo = {"font": ("Constantia", 11, "bold"), "bg": "#4e342e", "fg": "#d7c4a5"}
    estilo_numero = {"font": ("Constantia", 26, "bold"), "bg": "#4e342e", "fg": "#ffd700"}
    estilo_separador = {"font": ("Arial", 30), "bg": "#4e342e", "fg": "#8c6d53"}

    # --- Card 1: Heróis ---
    card_herois = tk.Frame(f_cards_container, bg="#4e342e", padx=15)
    card_herois.grid(row=0, column=0, pady=15)
    tk.Label(card_herois, text="HERÓIS", **estilo_titulo).pack()
    tk.Label(card_herois, text=str(herois_qtd), **estilo_numero).pack()

    # Separador visual
    tk.Label(f_cards_container, text="|", **estilo_separador).grid(row=0, column=1)

    # --- Card 2: Bestiário ---
    card_monstros = tk.Frame(f_cards_container, bg="#4e342e", padx=15)
    card_monstros.grid(row=0, column=2, pady=15)
    tk.Label(card_monstros, text="BESTIÁRIO", **estilo_titulo).pack()
    tk.Label(card_monstros, text=str(monstros_qtd), **estilo_numero).pack()

# Atualiza Carga de peso
def atualizar_inventario_e_peso_ui(id_personagem, tabela_treeview, lbl_peso_status, carga_max):
    # 1. Limpa a Treeview atual para não duplicar itens
    for i in tabela_treeview.get_children():
        tabela_treeview.delete(i)

    conn = db.conexao()
    cursor = conn.cursor(dictionary=True)

    # 2. AJUSTE: Buscar também os campos 'equipado' e 'local_equipado'
    query = """
        SELECT IP.id_inventario, E.Nome_equi, IP.quantidade, E.Peso, E.Tipo_equi,
               IP.equipado, IP.local_equipado
        FROM Inventario_Personagem IP
        JOIN equipamento E ON IP.id_equipamento = E.id_equipamento
        WHERE IP.id_personagem = %s
    """
    cursor.execute(query, (id_personagem,))
    itens = cursor.fetchall()

    peso_total_acumulado = 0.0

    # 3. AJUSTE: Inserir todos os 7 valores na Treeview
    for item in itens:
        p_total = item['quantidade'] * item['Peso']
        peso_total_acumulado += p_total

        # Converter o status do banco para visual
        simbolo = "☑" if item['equipado'] else "☐"
        slot = item['local_equipado'] if item['local_equipado'] else ""

        tabela_treeview.insert("", "end", iid=item['id_inventario'], values=(
            item['Nome_equi'],
            item['quantidade'],
            item['Peso'],
            p_total,
            item['Tipo_equi'],
            simbolo, # Agora o índice 5 existe!
            slot     # Agora o índice 6 existe!
        ))

    # 4. Atualiza o Banco de Dados com o novo peso real
    cursor.execute("UPDATE Personagens SET Carga_atual = %s WHERE id_personagem = %s",
                   (peso_total_acumulado, id_personagem))
    conn.commit()
    conn.close()

    # 5. ATUALIZAÇÃO DINÂMICA DA UI
    lbl_peso_status.config(text=f"Pes: {peso_total_acumulado:.1f} / {carga_max}kg")

    if peso_total_acumulado > carga_max:
        lbl_peso_status.config(fg="red")
    else:
        lbl_peso_status.config(fg="black")

# Adicionar Item inventario
def abrir_janela_selecao(id_personagem, tabela_inventario_principal, lbl_peso_status, carga_max):
    # 1. Configuração da Janela Secundária
    janela_busca = tk.Toplevel()
    janela_busca.title("Adicionar Item ao Inventário")
    janela_busca.geometry("500x400")
    janela_busca.grab_set() # Bloqueia a janela principal até fechar esta

    # 2. Barra de Busca
    frame_busca = tk.Frame(janela_busca, pady=10)
    frame_busca.pack(fill="x")

    tk.Label(frame_busca, text="Buscar Item:").pack(side="left", padx=5)
    ent_busca = tk.Entry(frame_busca)
    ent_busca.pack(side="left", fill="x", expand=True, padx=5)

    # 3. Lista de Equipamentos (Treeview)
    colunas = ("id", "nome", "tipo", "peso")
    tabela_busca = ttk.Treeview(janela_busca, columns=colunas, show="headings", height=10)

    tabela_busca.heading("id", text="ID")
    tabela_busca.heading("nome", text="Nome")
    tabela_busca.heading("tipo", text="Tipo")
    tabela_busca.heading("peso", text="Peso")

    tabela_busca.column("id", width=30)
    tabela_busca.column("nome", width=180)
    tabela_busca.column("tipo", width=100)
    tabela_busca.column("peso", width=50)
    tabela_busca.pack(fill="both", expand=True, padx=10)

    # 4. Função Interna de Busca no Banco de Dados
    def pesquisar_itens(event=None):
        # Limpa a lista atual
        for i in tabela_busca.get_children():
            tabela_busca.delete(i)

        termo = ent_busca.get()
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)

        # Busca por nome (usando a tabela 'equipamento' que você já possui)
        query = "SELECT id_equipamento, Nome_equi, Tipo_equi, Peso FROM equipamento WHERE Nome_equi LIKE %s"
        cursor.execute(query, (f"%{termo}%",))

        for item in cursor.fetchall():
            tabela_busca.insert("", "end", values=(
                item['id_equipamento'], item['Nome_equi'], item['Tipo_equi'], item['Peso']
            ))
        conn.close()

    ent_busca.bind("<KeyRelease>", pesquisar_itens) # Pesquisa enquanto digita

    # Confirma seleção do item
    def confirmar_selecao():
        selecionado = tabela_busca.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item da lista!")
            return

        # 1. Pega os dados básicos
        valores = tabela_busca.item(selecionado)['values']
        id_item = valores[0]
        nome_item = valores[1]

        # 2. Pergunta a quantidade via pop-up
        # O parâmetro minvalue=1 impede que o usuário digite 0 ou números negativos
        quantidade = simpledialog.askinteger(
            "Quantidade",
            f"Quantas unidades de {nome_item} deseja adicionar?",
            parent=janela_busca,
            minvalue=1,
            initialvalue=1
        )

        # Se o usuário clicar em "Cancelar", a variável quantidade será None
        if quantidade is None:
            return

        conn = db.conexao()
        cursor = conn.cursor()

        try:
            # 3. Insere no Banco de Dados com a quantidade escolhida
            sql = "INSERT INTO Inventario_Personagem (id_personagem, id_equipamento, quantidade) VALUES (%s, %s, %s)"
            cursor.execute(sql, (id_personagem, id_item, quantidade))
            conn.commit()

            # 4. Atualiza a UI da ficha principal
            atualizar_inventario_e_peso_ui(id_personagem, tabela_inventario_principal, lbl_peso_status, carga_max)

            janela_busca.destroy()
            messagebox.showinfo("Sucesso", f"{quantidade}x {nome_item} adicionado ao inventário!")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao adicionar: {e}")
        finally:
            conn.close()

    # Botão de Confirmação
    btn_confirmar = tk.Button(janela_busca, text="Adicionar Selecionado",
                             bg="#28a745", fg="white", command=confirmar_selecao)
    btn_confirmar.pack(pady=10)

    # Carrega a lista inicial (todos os itens)
    pesquisar_itens()

# Remove item inventario
def remover_item_selecionado(id_personagem, tabela_treeview, lbl_peso_status, carga_max):
    item_selecionado = tabela_treeview.selection()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um item para remover!")
        return

    id_inv = item_selecionado[0] # Pega o iid que definimos como id_inventario

    if messagebox.askyesno("Confirmar", "Deseja remover este item do inventário?"):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Inventario_Personagem WHERE id_inventario = %s", (id_inv,))
        conn.commit()
        conn.close()

        # Chama o refresh para atualizar tudo automaticamente
        atualizar_inventario_e_peso_ui(id_personagem, tabela_treeview, lbl_peso_status, carga_max)

# Criação da Janela principal
janela = tk.Tk()
janela.title("Criação de Personagem - RPG") # Titulo que sera exibido
janela.geometry('650x430') # Ajsute do tamanho da tela

# Abas do Sistema
notebook = ttk.Notebook(janela)
notebook.grid(row=0,column=0,sticky='nsew')

# Abas Superior
aba_criacao = tk.Frame(notebook)
aba_visualizacao = tk.Frame(notebook)
aba_bestiario = tk.Frame(notebook)
aba_inicio = tk.Frame(notebook)

# Exbição das Abas
notebook.add(aba_inicio,text="Inicio")
notebook.add(aba_criacao,text="Novo Personagem")
notebook.add(aba_visualizacao,text="Heróis")
notebook.add(aba_bestiario,text="Bestiario")

# criacao = tk.Frame(aba_criacao)
criacao = tk.LabelFrame(aba_criacao, text=" Dados de Criação", padx=5, pady=5)
criacao.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
tk.Label(criacao,text="Dados Basicos",font=("Arial",7,"bold")).grid(row=0,column=0,sticky="w",pady=(5,5))

# Campos de Nome
tk.Label(criacao,text="Nome: ",font = ("Arial",8,"bold")).grid(row = 1, column = 0,sticky= "w")
Nome = tk.Entry(criacao, width= 65,font=("Arial",7))
Nome.grid(row = 1, column = 1,columnspan=3,padx=(1,1),pady= (2,2),sticky= "w")

# Label informativo Raças
tk.Label(criacao,text="Raça: ",font = ("Arial",8,"bold")).grid(row = 2,column = 0, sticky= "w")

# Lista Suspensa Raças
raca = db.lista_racas()
combo_racas = ttk.Combobox(criacao, values = raca, state = "readonly",width = 12)
combo_racas.grid(row = 2, column = 1,padx=(1,1),pady= (2,2),sticky= "w")

tk.Label(criacao,text="Sub-Raça: ",font = ("Arial",8,"bold")).grid(row = 2,column = 2, sticky= "w")

# Combo Sub_raça
sub_raca = [""]
combo_s_racas = ttk.Combobox(criacao, values = sub_raca, state = "readonly",width = 20)
combo_s_racas.grid(row = 2, column = 3,padx=(1,1),pady= (2,2),sticky= "w")

# Lista Alinhamentos
tk.Label(criacao,text="Alinhamentos: ",font=("Arial",8,"bold")).grid(row= 3, column=0)

# Combo Alinhamentos
alinhamentos = db.lista_alinhamentos()
combo_alinhamentos = ttk.Combobox(criacao,values = alinhamentos, state= "readonly", width= 12)
combo_alinhamentos.grid(row= 3, column= 1,padx=(1,1),pady= (2,2),sticky= "w")

# Label Informativa Classe
tk.Label(criacao,text = 'Classe:', font=("Arial",8,"bold")).grid(row = 4, column = 0,padx=(1,1),pady= (2,2),sticky= "w")

# Combo Classes
classe = db.lista_classes()
combo_classe = ttk.Combobox(criacao, values=classe,state="readonly", width = 12)
combo_classe.grid(row = 4,column = 1,padx=(1,1),pady= (2,2),sticky= "w")

# Label Informativa Sub-Classe
tk.Label(criacao,text = 'Arquetipos:', font=("Arial",8,"bold")).grid(row = 4, column = 2,pady= (2,2),sticky= "w")

# Combo Sub-Classes
Sub_Classe = db.lista_Sub_Classe()
combo_Sub_classe = ttk.Combobox(criacao, values=Sub_Classe ,state="readonly", width = 20)
combo_Sub_classe.grid(row = 4,column = 3,padx=(1,1),pady= (2,2),sticky= "w")

divisor = ttk.Separator(criacao,orient='horizontal')
divisor.grid(row=5,column=0,columnspan=4,sticky="ew",pady=(5,5))

frame_Atri = tk.Frame(criacao)
frame_Atri.grid(row=7,column=0,columnspan=7, sticky="ew",pady= (10,0))

divisor_ver = ttk.Separator(frame_Atri,orient="vertical")
divisor_ver.grid(row=0,column=2,rowspan=7,sticky="ns",padx=(10,10))

qtd_pontos = tk.IntVar(value=15)

tk.Label(frame_Atri,text="Atributos",font=("Arial",7,"bold")).grid(row=0,column=0,sticky="w")
tk.Label(frame_Atri,text=f"Pontos:",font=("Arial",7,"bold")).grid(row=1 ,column=0 ,padx=(0,0),sticky= "w")
tk.Label(frame_Atri,textvariable=qtd_pontos, font=("Arial",7 )).grid(row=1, column=1,padx=(0,0),sticky="w")

# Variaveis de Pontos de Distribuição
pts_For = tk.IntVar(value=8)
pts_Dex = tk.IntVar(value=8)
pts_Int = tk.IntVar(value=8)
pts_Car = tk.IntVar(value=8)
pts_Sab = tk.IntVar(value=8)
pts_Con = tk.IntVar(value=8)

#--------------- Coluna 0 - Coluna 3 ------------------------------
frame_pts = tk.Frame(frame_Atri)
frame_pts.grid(row=2,column=0,columnspan=2,pady=(3,3),sticky="nw")

# Atributo Força
tk.Label(frame_pts,text="Força",font=("Arial",7,"bold")).grid(row=0, column=0,columnspan=3,padx=(0,0),pady=(3,3))
tk.Button(frame_pts,text="-", command=lambda: altera_pontos(pts_For,-1),width=2,font=("Arial",7)).grid(row=1,column=0,padx=(10,0))
tk.Label(frame_pts,textvariable=pts_For,font=("Arial",7),width=2).grid(row=1,column=1,padx=(1,1))
tk.Button(frame_pts,text="+",command=lambda: altera_pontos(pts_For,1),width=2,font=("Arial",7)).grid(row=1,column=2)

# Atributo Inteligencia
tk.Label(frame_pts,text="Inteligencia",font=("Arial",7,"bold")).grid(row=3,column=0,columnspan=3,pady=(3,3), padx=(0,0))
tk.Button(frame_pts,text="-",command=lambda: altera_pontos(pts_Int,-1),width=2,font=("Arial",7)).grid(row=4,column=0, padx=(10,0))
tk.Label(frame_pts,textvariable=pts_Int,font=("Arial",7),width=3).grid(row=4,column=1,padx=(1,1))
tk.Button(frame_pts,text="+",command=lambda: altera_pontos(pts_Int,1),width=2,font=("Arial",7)).grid(row=4,column=2)

# Atributo Inteligencia
tk.Label(frame_pts,text="Carisma",font=("Arial",7,"bold")).grid(row=5,column=0,columnspan=3,pady=(3,3), padx=(0,0))
tk.Button(frame_pts,text="-",command=lambda: altera_pontos(pts_Car,-1),width=2,font=("Arial",7)).grid(row=6,column=0, padx=(10,0))
tk.Label(frame_pts,textvariable=pts_Car,font=("Arial",7),width=3).grid(row=6,column=1,padx=(1,1))
tk.Button(frame_pts,text="+",command=lambda: altera_pontos(pts_Car,1),width=2,font=("Arial",7)).grid(row=6,column=2)

#--------------- Coluna 3 - Coluna 6 ------------------------------
# Atributo Destreza
tk.Label(frame_pts,text="Destreza",font=("Arial",7,"bold")).grid(row=0,column=3,columnspan=3,pady=(3,3), padx=(20,0))
tk.Button(frame_pts,text="-",command=lambda: altera_pontos(pts_Dex,-1),width=2,font=("Arial",7)).grid(row=1,column=4, padx=(20,0))
tk.Label(frame_pts,textvariable=pts_Dex,font=("Arial",7),width=2).grid(row=1,column=5,padx=(1,1))
tk.Button(frame_pts,text="+",command=lambda: altera_pontos(pts_Dex,1),width=2,font=("Arial",7)).grid(row=1,column=6)

# Atributo Sabedoria
tk.Label(frame_pts,text="Sabedoria",font=("Arial",7,"bold")).grid(row=3,column=3,columnspan=3,pady=(3,3), padx=(20,0))
tk.Button(frame_pts,text="-",command=lambda: altera_pontos(pts_Sab,-1),width=2,font=("Arial",7)).grid(row=4,column=4, padx=(20,0))
tk.Label(frame_pts,textvariable=pts_Sab,font=("Arial",7),width=2).grid(row=4,column=5,padx=(1,1))
tk.Button(frame_pts,text="+",command=lambda: altera_pontos(pts_Sab,1),width=2,font=("Arial",7)).grid(row=4, column=6)

# Atributo Constituição
tk.Label(frame_pts,text="Constituição",font=("Arial",7,"bold")).grid(row=5,column=3,columnspan=3,pady=(3,3), padx=(20,0))
tk.Button(frame_pts,text="-",command=lambda: altera_pontos(pts_Con,-1),width=2,font=("Arial",7)).grid(row=6,column=4, padx=(20,0))
tk.Label(frame_pts,textvariable=pts_Con,font=("Arial",7),width=2).grid(row=6,column=5,padx=(1,1))
tk.Button(frame_pts,text="+",command=lambda: altera_pontos(pts_Con,1),width=2,font=("Arial",7)).grid(row=6, column=6)

# Botão para salvar, posicionado abaixo dos atributos
btn_salvar = tk.Button(aba_criacao, text="Gravar Herói",
                       command=lambda: salvar_personagem(),
                       bg="#4CAF50", fg="white", font=("Arial", 8, "bold"))
btn_salvar.grid(row=7, column=0, columnspan=7, padx=10, sticky="ew")

# ----------------------------------------- Aba Herois-------------------------
colunas = ("ID","Nome","HP Maximo","Defesa","Classe","Sub Classe","Raça","Lvl")
frame_herois = tk.LabelFrame(aba_visualizacao, text=" Heróis ", padx=5, pady=5)
frame_herois.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
tabela_perso = ttk.Treeview(frame_herois,columns=colunas,show="headings",height=8)

# Cabeçalho da Tabela.
tabela_perso.heading("ID",text="ID")
tabela_perso.heading("Nome",text="Nome")
tabela_perso.heading("HP Maximo",text="Vida Maxima")
tabela_perso.heading("Defesa",text="Defesa")
tabela_perso.heading("Classe",text="Classe")
tabela_perso.heading("Sub Classe",text="Sub Classe")
tabela_perso.heading("Raça",text="Raça")
tabela_perso.heading("Lvl",text="Level")

# Infomações da Coluna
tabela_perso.column("ID",width=40, anchor="center")
tabela_perso.column("Nome",width=80, anchor="center",stretch=True)
tabela_perso.column("HP Maximo",width=80, anchor="center")
tabela_perso.column("Defesa",width=80, anchor="center")
tabela_perso.column("Classe",width=80, anchor="center")
tabela_perso.column("Sub Classe",width=80, anchor="center")
tabela_perso.column("Raça",width=80, anchor="center")
tabela_perso.column("Lvl",width=50, anchor="center")

tabela_perso.grid(row=1,column=0, padx=10, pady=10, sticky="nsew")

atualiza = tk.Button(aba_visualizacao,text="Atualizar Lista", command=lambda: carregar_personagem())
atualiza.grid(row=2,column=0,pady=5)

# ----------------------------------------- Aba Bestiario -------------------------
colunas = ("ID","Nome","Tipo","HP Maximo","Defesa","Força","Lvl")
frame_inimigos = tk.LabelFrame(aba_bestiario, text=" Bestiário ", padx=5, pady=5)
frame_inimigos.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
tabela_inimigo = ttk.Treeview(frame_inimigos,columns=colunas,show="headings",height=8)

# Cabeçalho da Tabela.
tabela_inimigo.heading("ID",text="ID")
tabela_inimigo.heading("Nome",text="Nome")
tabela_inimigo.heading("Tipo",text="Tipo")
tabela_inimigo.heading("HP Maximo",text="Vida Maxima")
tabela_inimigo.heading("Lvl",text="Level")
tabela_inimigo.heading("Defesa",text="Defesa")
tabela_inimigo.heading("Força",text="Força")

# Infomações da Coluna
tabela_inimigo.column("ID",width=30, anchor="center")
tabela_inimigo.column("Nome",width=100, anchor="center",stretch=True)
tabela_inimigo.column("Tipo",width=100, anchor="center")
tabela_inimigo.column("HP Maximo",width=100, anchor="center")
tabela_inimigo.column("Defesa",width=100, anchor="center")
tabela_inimigo.column("Força",width=100, anchor="center")
tabela_inimigo.column("Lvl",width=50, anchor="center")

tabela_inimigo.grid(row=1,column=0, padx=10, pady=10, sticky="nsew")

atualiza = tk.Button(aba_bestiario,text="Atualizar Lista", command=lambda: carregar_inimigos())
atualiza.grid(row=2,column=0,pady=5)

# Função de click ao selecionar a Raça desejada.
def raca_selecionada (event):
    conn = db.conexao()
    cursor = conn.cursor()

    raca_escolhida = combo_racas.get()
    id_raca = db.id_raca(raca_escolhida)

    query = "SELECT nome_subraca FROM Sub_racas WHERE id_raca = %s"
    cursor.execute(query, (id_raca,))
    sracas = cursor.fetchall()

    lista_sracas = [sracas[0] for sracas in sracas]
    combo_s_racas['values'] = lista_sracas
    combo_s_racas.set("")

    # itens_Formatados = busca_invetario(id_raca)
    # inv.set(itens_Formatados)
    print(f'O jogador escolheu: {raca_escolhida}')

# Função de click ao selecionar a Classe desejada.
def classe_selecionada(event):
    conn= db.conexao()
    cursor = conn.cursor()
    classe_escolhida = combo_classe.get()
    id = db.id_classe(classe_escolhida)

    query = "SELECT nome_subclasse FROM Sub_Classes WHERE id_classe = %s"

    cursor.execute(query, (id,))
    sub_classes = cursor.fetchall()

    Lista_Sub_classe = [sub[0] for sub in sub_classes]
    combo_Sub_classe['values'] = Lista_Sub_classe
    combo_Sub_classe.set("")

    print(f'O jogador escolheu a classe: {classe_escolhida} - Id: {id}')

# Função de click ao selecionar a Alinhamento desejada.
def alinh_selecionado(event):
    alinhamento_selecionado = combo_alinhamentos.get()
    print(f'O jogador selecionou o Alinhamneto: {alinhamento_selecionado}')

# Função de click ao selecionar a Sub-Classe desejada.
def Sub_Classe_selecionada(event):
    Sub_Classe_Selecionada = combo_Sub_classe.get()
    print(f'O jogador selecionou a Sub-Classe: {Sub_Classe_Selecionada}')

# Abre a "Ficha do Personagem"
def on_double_click_perso(event):
    item_id = tabela_perso.selection()[0] # Pega a linha clicada
    valores = tabela_perso.item(item_id, "values")
    mostrar_ficha(valores[0]) # Envia o ID do personagem para a função

# Abre Ficha Do Monstro
def on_double_click_best(event):
    item_id = tabela_inimigo.selection()[0] # Pega a linha clicada
    valores = tabela_inimigo.item(item_id, "values")
    mostra_monstro(valores[0])

# Vincula o Evento ao Combobox informado.
combo_racas.bind("<<ComboboxSelected>>",raca_selecionada)
combo_classe.bind("<<ComboboxSelected>>",classe_selecionada)
combo_alinhamentos.bind("<<ComboboxSelected>>",alinh_selecionado)
combo_Sub_classe.bind("<<ComboboxSelected>>",Sub_Classe_selecionada)
tabela_perso.bind("<Double-1>", on_double_click_perso)
tabela_inimigo.bind("<Double-1>", on_double_click_best)

# Aba Inicio
criar_tela_inicio(aba_inicio)
# tk.Label(frame_index, text="Bem-vindo ao Gestor de RPG\nClique em 'Personagem' para começar",justify='center').grid(pady=50)

janela.mainloop()