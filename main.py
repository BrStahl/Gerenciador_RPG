import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import io
from tkinter import filedialog
import random as rd
import ast
import os

from dao import PersonagemDAO, InventarioDAO, MagiaDAO, MonstroDAO, ReferenciaDAO
from model.personagem import Personagem

class TooltipRPG:
    def __init__(self, tree):
        self.tree = tree
        self.tip_window = None

    def mostrar(self, texto, x, y):
        if self.tip_window or not texto: return
        self.tip_window = tw = tk.Toplevel(self.tree)
        tw.wm_overrideredirect(True)
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
def atribuir_slots_por_nivel(id_p, nivel_p):
    PersonagemDAO.atribuir_slots_por_nivel(id_p, nivel_p)

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
    itens = InventarioDAO.buscar_itens_iniciais(id_raca)
    inventario_Inicial = []

    for i in itens:
        if i[1] > 1:
            inventario_Inicial.append(f" • {i[0]} ({i[1]})")
        else:
            inventario_Inicial.append(f" • {i[0]}")

    return "\n".join(inventario_Inicial)

# Salvar Personagem
def salvar_personagem():
    try:
        nome_per = Nome.get()
        raca = combo_racas.get()
        sraca = combo_s_racas.get()
        classe = combo_classe.get()
        sub_classe = combo_Sub_classe.get()
        alinhamento = combo_alinhamentos.get()

        forca = pts_For.get()
        destreza = pts_Dex.get()
        constituicao = pts_Con.get()
        inteligencia = pts_Int.get()
        sabedoria = pts_Sab.get()
        carisma = pts_Car.get()

        # Obter bônus racial
        bonus = ReferenciaDAO.obter_bonus_raca(raca)
        if bonus:
            forca += bonus[0]
            inteligencia += bonus[1]
            constituicao += bonus[2]
            destreza += bonus[3]
            sabedoria += bonus[4]
            carisma += bonus[5]

        # Criar objeto Personagem (Model) para calcular status
        novo_personagem = Personagem(
            nome_per, raca, classe, sub_classe, alinhamento,
            forca, destreza, constituicao, inteligencia, sabedoria, carisma
        )

        # Ajustar vida base se necessário (Model já tem lógica base, mas aqui pega dado_vida do DB)
        dado_vida_tupla = ReferenciaDAO.obter_dado_vida_classe(classe)
        dado_vida = dado_vida_tupla[0] if dado_vida_tupla else 8

        # Recalcular vida com base no dado real do banco (opcional se o Model já tiver isso hardcoded,
        # mas aqui mantemos consistência com o banco)
        mod_vida = (constituicao - 10) // 2
        vida_base_val = 8
        if dado_vida == '1d12': vida_base_val = 12
        elif dado_vida == '1d10': vida_base_val = 10
        elif dado_vida == '1d6': vida_base_val = 6

        novo_personagem.vida_max = vida_base_val + mod_vida
        novo_personagem.vida_atual = novo_personagem.vida_max

        # Preparar dados para o DAO
        dados_persist = novo_personagem.to_dict()
        # Ajuste para sub_raca que não está no init do to_dict diretamente ou precisa ser passado
        dados_persist['sub_raca'] = sraca

        # Salvar via DAO
        id_novo = PersonagemDAO.criar_personagem(dados_persist)

        # Atribuir slots
        PersonagemDAO.atribuir_slots_por_nivel(id_novo, novo_personagem.lvl)

        messagebox.showinfo("Sucesso","Herói Gravado com Sucesso.")
        limpa_campos()

    except Exception as e:
        messagebox.showerror("Erro",f"Erro ao inserir: {e}")

# Carrega lista de Personagens -> Aba Herois
def carregar_personagem():
    for i in tabela_perso.get_children():
        tabela_perso.delete(i)

    herois = PersonagemDAO.listar_herois()

    for p in herois:
        tabela_perso.insert("","end",values=p)

# Carrega lista de Monstros -> Bestiario
def carregar_inimigos():
    for i in tabela_inimigo.get_children():
        tabela_inimigo.delete(i)

    monstros = MonstroDAO.listar_monstros()

    for p in monstros:
        tabela_inimigo.insert("","end",values=p)

# Atualiza Foto
def atualizar_foto_personagem(id_personagem):
    caminho_img = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])

    if caminho_img:
        with open(caminho_img, 'rb') as arquivo:
            binario_puro = arquivo.read()

        PersonagemDAO.atualizar_foto(id_personagem, binario_puro)
        messagebox.showinfo("Sucesso", "Foto salva corretamente!")

# Exibe Ficha do Personagem
def mostrar_ficha(id_personagem):

    def ajustar_janela_ao_conteudo(event):
        aba_selecionada = event.widget.nametowidget(event.widget.select())
        aba_selecionada.update_idletasks()
        largura = aba_selecionada.winfo_reqwidth() + 20
        altura = aba_selecionada.winfo_reqheight() + 50
        ficha.geometry(f"{largura}x{altura}")

    p = PersonagemDAO.buscar_por_id(id_personagem)

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

    notebook.add(aba_dados_basicos,text="Dados Basicos")
    notebook.add(aba_informacoes,text="Informações")
    notebook.add(aba_inventario,text="Inventário")
    notebook.add(aba_magias,text="Magias")

    # Dados Ficha
    frame_ficha = tk.Frame(aba_dados_basicos)
    frame_ficha.pack(fill="both", expand=True, padx=5, pady=5)

    # 1. FRAME: DADOS BÁSICOS
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

    # 2. FRAME: ATRIBUTOS
    f_atributos = tk.LabelFrame(frame_ficha, text=" Atributos ", font=("Arial", 8, "bold"))
    f_atributos.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    tk.Label(f_atributos, text=f"Def: {p['defesa']} | Ini: {p['Iniciativa']} | Vel: {p['Velocidade']}", font=("Arial", 9)).grid(row=0, column=0, sticky='w', padx=5)
    tk.Label(f_atributos, text=f"For: {p['Forca']} | Int: {p['Inteligencia']} | Sab: {p['Sabedoria']}", font=("Arial", 9)).grid(row=1, column=0, sticky='w', padx=5)
    tk.Label(f_atributos, text=f"Con: {p['Constituicao']} | Car: {p['Carisma']} | Des: {p['Destreza']}", font=("Arial", 9)).grid(row=2, column=0, sticky='w', padx=5)
    lbl_peso_status = tk.Label(f_atributos, text=f"Pes: {p['Carga_atual']} / {p['Carga_max']}kg", font=("Arial", 9))
    lbl_peso_status.grid(row=3, column=0, sticky='w', padx=5)

    # 3. FRAME: FOTO
    f_foto_lb = tk.LabelFrame(frame_ficha, text=" Retrato do Herói ", font=("Arial", 8, "bold"))
    f_foto_lb.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")

    if p['foto_personagem']:
        try:
            dados = p['foto_personagem']
            if isinstance(dados, str) and dados.startswith("b'"):
                dados = ast.literal_eval(dados)

            fluxo_dados = io.BytesIO(dados)
            img_pil = Image.open(fluxo_dados)
            img_pil.thumbnail((220, 260))
            foto_tk = ImageTk.PhotoImage(img_pil)

            lbl_foto = tk.Label(f_foto_lb, image=foto_tk)
            lbl_foto.image = foto_tk
            lbl_foto.pack(padx=5, pady=5)
        except Exception as e:
            tk.Label(f_foto_lb, text="[ Erro na Imagem ]").pack()
    else:
        tk.Label(f_foto_lb, text="[ Sem Foto ]", width=25, height=12).pack()

    # --- PAINEL DE MAGIAS RÁPIDAS ---
    frame_magias_rapidas = tk.LabelFrame(frame_ficha, text="Magias Rápidas (Top 3)",font=("Arial",8,"bold"), padx=10, pady=3)
    frame_magias_rapidas.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    def conjurar_pelo_top3(id_p, dados_m):
        nome = dados_m['nome_magia']
        nivel = dados_m['nivel']

        if nivel == 0:
            messagebox.showinfo("Truque", f"{nome} lançado!")
            return

        res = MagiaDAO.buscar_slots(id_p, nivel)

        if res and res['slots_atuais'] > 0:
            novo_valor = res['slots_atuais'] - 1
            MagiaDAO.atualizar_slots(id_p, nivel, novo_valor)
            messagebox.showinfo("Sucesso", f"{nome} conjurado! Restam {novo_valor} slots de Lvl {nivel}.")
        else:
            messagebox.showwarning("Esgotado", f"Sem slots de nível {nivel}!")

    def atualizar_painel_top3(id_p):
        for widget in frame_magias_rapidas.winfo_children():
            widget.destroy()

        lista_magias = MagiaDAO.listar_top3_magias(id_p)

        if not lista_magias:
            tk.Label(frame_magias_rapidas, text="Grimório vazio.", fg="gray").grid(row=0, column=0)
        else:
            for i, magia in enumerate(lista_magias):
                lbl = tk.Label(frame_magias_rapidas, text=f"{magia['nome_magia']} (Lvl {magia['nivel']})", font=("Arial", 9))
                lbl.grid(row=i, column=0, sticky="w", pady=2)

                btn = tk.Button(
                    frame_magias_rapidas,
                    text="⚡",
                    bg="#007bff",
                    fg="white",
                    width=3,
                    command=lambda m=magia: conjurar_pelo_top3(id_p, m)
                )
                btn.grid(row=i, column=1, padx=5, pady=2)

    atualizar_painel_top3(id_personagem)

    btn_carregar = tk.Button(f_foto_lb, text="📷 Alterar Foto", font=("Arial", 7),
                            command=lambda: atualizar_foto_personagem(id_personagem))
    btn_carregar.pack(pady=5, fill="x", padx=5)

    # ----------------------------- Aba Informações ------------------------------------------------------------
    notebook = ttk.Notebook(aba_informacoes)
    notebook.grid(row=0,column=0,sticky='nsew')

    aba_Raca = tk.Frame(notebook)
    aba_classe = tk.Frame(notebook)
    aba_s_classe = tk.Frame(notebook)

    notebook.add(aba_Raca,text="Dados Raça")
    notebook.add(aba_classe,text="Dados Classe")
    notebook.add(aba_s_classe,text="Dados Sub-Classe")

    frame_acoes = tk.LabelFrame(aba_Raca,text="Informações",font=("Arial",8,"bold"))
    frame_acoes.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    detalhes_raca = PersonagemDAO.obter_detalhes_raca(id_personagem)

    # Helper para extrair texto
    def extrair_texto(dicionario, chave, padrao="Não registrado"):
        if dicionario and dicionario.get(chave):
            return str(dicionario[chave]).replace('#','').replace('*','').replace("_","")
        return padrao

    # Frame "Caracteristicas" - descri já buscado antes? Não, buscar agora
    descricao_raca = PersonagemDAO.obter_descricao_raca(id_personagem)
    txt_desc = extrair_texto(descricao_raca, 'descricao')

    f_desc = tk.LabelFrame(frame_acoes,text="Caracteristicas da Raça",font=("Arial",7,"bold"))
    f_desc.grid(row=0,column=0,padx=2,pady=2,sticky="nsew")
    tk.Label(f_desc, text=txt_desc, wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5)

    # Frame "Idade"
    f_idade = tk.LabelFrame(frame_acoes,text="Idade",font=("Arial",7,"bold"))
    f_idade.grid(row=0,column=1,padx=2,pady=2,sticky="nsew")
    tk.Label(f_idade, text=extrair_texto(detalhes_raca['idade'], 'Idade'), wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5)

    # Frame "Altura "
    f_altura = tk.LabelFrame(frame_acoes,text="Altura",font=("Arial",7,"bold"))
    f_altura.grid(row=1,column=0,padx=2,pady=2,sticky="nsew")
    tk.Label(f_altura, text=extrair_texto(detalhes_raca['altura'], 'Altura'), wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5)

    # Frame "Alinhamentos "
    f_alinh = tk.LabelFrame(frame_acoes,text="Alinhamentos",font=("Arial",7,"bold"))
    f_alinh.grid(row=1,column=1,padx=2,pady=2,sticky="nsew")
    tk.Label(f_alinh, text=extrair_texto(detalhes_raca['alinhamento'], 'Alinhamentos'), wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5,sticky="nsew")

    # Frame "Visão"
    f_visao = tk.LabelFrame(frame_acoes,text="Visão",font=("Arial",7,"bold"))
    f_visao.grid(row=2,column=0,padx=2,pady=2,sticky="nsew")
    tk.Label(f_visao, text=extrair_texto(detalhes_raca['visao'], 'Visao'), wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5)

    # Frame "Idiomas"
    f_lin = tk.LabelFrame(frame_acoes,text="Idiomas",font=("Arial",7,"bold"))
    f_lin.grid(row=2,column=1,padx=2,pady=2,sticky="nsew")
    tk.Label(f_lin, text=extrair_texto(detalhes_raca['idiomas'], 'Linguas'), wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5)

    # Frame "Habilidades"
    f_hab = tk.LabelFrame(frame_acoes,text="Habilidades",font=("Arial",7,"bold"))
    f_hab.grid(row=3,column=0,padx=2,pady=2,sticky="nsew")
    tk.Label(f_hab, text=extrair_texto(detalhes_raca['habilidades'], 'Habilidades'), wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5)

    # Frame "Velocidade"
    f_velo = tk.LabelFrame(frame_acoes,text="Velocidade",font=("Arial",7,"bold"))
    f_velo.grid(row=3,column=1,padx=2,pady=2,sticky="nsew")
    tk.Label(f_velo, text=extrair_texto(detalhes_raca['velocidade'], 'Velocidade_desc'), wraplength=330, justify="left", anchor="nw").grid(row=0,column=0,padx=5, pady=5)

    # ------------------------------------ Dados Da Classe ----------------------------------------------------------
    detalhes_classe = PersonagemDAO.obter_detalhes_classe(id_personagem)

    frame_d_classe = tk.LabelFrame(aba_classe,text="Informações de Classe",font=("Arial",8,"bold"))
    frame_d_classe.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    campos_classe = [
        ('armadura', 'Armadura', 0, 0),
        ('ferramentas', 'Ferramentas', 0, 1),
        ('salvaguardas', 'Salvaguardas', 1, 0),
        ('pericias', 'Pericias', 1, 1),
        ('equipamento_inicial', 'Equipamentos', 2, 0),
        ('atributo_conjuracao', 'Atributos Para Conjuração', 2, 1)
    ]

    for chave, titulo, r, c in campos_classe:
        f_tmp = tk.LabelFrame(frame_d_classe, text=titulo, font=("Arial",7,"bold"))
        f_tmp.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
        tk.Label(f_tmp, text=extrair_texto(detalhes_classe[chave], chave), wraplength=330, justify="left", anchor="nw").grid(row=0, column=0, padx=5, pady=5)

    # ---------------------------Descrição Sub- Classe--------------------------------------
    frame_s_classe = tk.LabelFrame(aba_s_classe,text="Informações da Sub-Classe",font=("Arial",8,"bold"))
    frame_s_classe.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    f_subcl = tk.LabelFrame(frame_s_classe,text="Descrição Sub-Classe (Arquetipo)",font=("Arial",7,"bold"))
    f_subcl.grid(row=0,column=0,rowspan=3,padx=2,pady=2,sticky="nsew")

    desc_subclasse = PersonagemDAO.obter_descricao_subclasse(id_personagem)
    txt_sub = extrair_texto(desc_subclasse, 'descricao')

    lbl_sub = tk.Label(f_subcl, text=txt_sub, wraplength= 670, justify="left", anchor="nw")
    lbl_sub.grid(row=0,column=0,rowspan=2,padx=5, pady=5)

    # ------------------ Aba Inventario----------------------------------------
    frame_lista = tk.Frame(aba_inventario)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("Item", "Qtd", "Peso Uni", "Peso Total", "Tipo","Equipado","Slot")
    tabela = ttk.Treeview(frame_lista, columns=colunas, show="headings")

    tabela.heading("Item", text="Item")
    tabela.heading("Qtd", text="Qtd")
    tabela.heading("Peso Uni", text="Peso (Un)")
    tabela.heading("Peso Total", text="Total")
    tabela.heading("Tipo", text="Tipo")
    tabela.heading("Equipado", text="Equipamento")
    tabela.heading("Slot", text="Slot")

    tabela.column("Item", width=100)
    tabela.column("Qtd", width=50, anchor="center")
    tabela.column("Peso Uni", width=40, anchor="center")
    tabela.column("Peso Total", width=40, anchor="center")
    tabela.column("Tipo", width=40, anchor="center")
    tabela.column("Equipado", width=40, anchor="center")
    tabela.column("Slot", width=80, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    frame_botoes = tk.Frame(aba_inventario)
    frame_botoes.pack(fill="x", padx=10, pady=5)

    tk.Button(frame_botoes, text="➕ Adicionar Item", bg="#28a745", fg="white", command=lambda: abrir_janela_selecao(id_personagem, tabela, lbl_peso_status, p['Carga_max'])).pack(side="left", padx=5)
    tk.Button(frame_botoes, text="➖ Remover", bg="#dc3545", fg="white",command=lambda: remover_item_selecionado(id_personagem, tabela, lbl_peso_status, p['Carga_max'])).pack(side="left", padx=5)

    atualizar_inventario_e_peso_ui(id_personagem, tabela, lbl_peso_status, p['Carga_max'])

    def abrir_seletor_slot(event, item_id):
        coluna = tabela.identify_column(event.x)
        x, y, largura, altura = tabela.bbox(item_id, coluna)

        opcoes = ["Mão Direita", "Mão Esquerda", "Costas", "Cinto", "Cabeça", "Corpo"]
        cb_slot = ttk.Combobox(tabela, values=opcoes, state="readonly")
        cb_slot.place(x=x, y=y, width=largura, height=altura)
        cb_slot.focus()

        def fechar_e_salvar(event):
            if not cb_slot.winfo_exists(): return

            novo_local = cb_slot.get()
            novos_v = list(tabela.item(item_id, 'values'))
            novos_v[6] = novo_local
            tabela.item(item_id, values=novos_v)

            InventarioDAO.atualizar_equipado(item_id, 1, novo_local)
            cb_slot.destroy()

        cb_slot.bind("<<ComboboxSelected>>", fechar_e_salvar)
        cb_slot.bind("<FocusOut>", lambda e: cb_slot.destroy() if cb_slot.winfo_exists() else None)

    tooltip = TooltipRPG(tabela)

    def monitorar_mouse(event):
        item_id = tabela.identify_row(event.y)
        if item_id:
            res = InventarioDAO.obter_detalhes_item(item_id)
            if res:
                info = f"Dano: {res['Dado_dano']} ({res['Tipo_dano']})\nPropriedades: {res['Propriedades']}"
                tooltip.esconder()
                tooltip.mostrar(info, event.x_root, event.y_root)
        else:
            tooltip.esconder()

    def usar_item_consumivel(id_inventario, valores, id_p, c_max):
        qtd_atual = int(valores[1])
        if qtd_atual > 0:
            nova_qtd = qtd_atual - 1
            if nova_qtd > 0:
                InventarioDAO.atualizar_quantidade(id_inventario, nova_qtd)
            else:
                InventarioDAO.remover_item(id_inventario)
            atualizar_inventario_e_peso_ui(id_p, tabela, lbl_peso_status, c_max)

    def ao_dar_duplo_clique(event, id_p, c_max):
        item_id = tabela.focus()
        coluna = tabela.identify_column(event.x)
        if not item_id: return

        valores = list(tabela.item(item_id, 'values'))
        tipo = valores[4]

        if tipo == "Consumivel":
            if messagebox.askyesno("Usar", f"Deseja consumir 1x {valores[0]}?"):
                usar_item_consumivel(item_id, valores, id_p, c_max)
            return

        if coluna == "#7" and valores[5] == "☑":
            abrir_seletor_slot(event, item_id)

    def ao_clicar_tabela(event, id_p, c_max):
        item_id = tabela.identify_row(event.y)
        coluna = tabela.identify_column(event.x)
        if not item_id or coluna != "#6": return

        valores = list(tabela.item(item_id, 'values'))
        status = 0
        slot = ""
        if valores[5] == "☐":
            valores[5] = "☑"
            valores[6] = "Mão Direita"
            status = 1
            slot = "Mão Direita"
        else:
            valores[5] = "☐"
            valores[6] = ""
            status = 0
            slot = ""

        tabela.item(item_id, values=valores)
        InventarioDAO.atualizar_equipado(item_id, status, slot)

    tabela.bind("<ButtonRelease-1>", lambda e: ao_clicar_tabela(e, id_personagem, p['Carga_max']))
    tabela.bind("<Double-1>", lambda e: ao_dar_duplo_clique(e, id_personagem, p['Carga_max']))
    tabela.bind("<Motion>", monitorar_mouse)
    tabela.bind("<Leave>", lambda e: tooltip.esconder())

    # ------------------------------------------- Aba Magias---------------------------------------

    def carregar_magias_personagem(id_p, tree):
        for i in tree.get_children():
            tree.delete(i)

        magias = MagiaDAO.listar_magias_conhecidas(id_p)
        for m in magias:
            tree.insert("", "end", values=(
                m['id_magia'], m['nome_magia'], m['nivel'],
                m['escola'], m['tempo_conjuracao'], m['alcance'], m['dano_cura']
            ))

    def realizar_descanso_longo(id_p, tree_magias):
        if not messagebox.askyesno("Descanso Longo", "Deseja realizar um Descanso Longo?\nIsso restaurará todo o HP e Slots de Magia."):
            return

        try:
            MagiaDAO.restaurar_slots_max(id_p)
            PersonagemDAO.restaurar_hp_max(id_p)
            carregar_magias_personagem(id_p, tree_magias)
            messagebox.showinfo("Descanso", "O herói descansou! Recursos totalmente restaurados.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar descanso: {e}")

    def realizar_conjuracao(id_p, tree):
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

        res = MagiaDAO.buscar_slots(id_p, nivel_m)

        if res and res['slots_atuais'] > 0:
            novo_valor = res['slots_atuais'] - 1
            MagiaDAO.atualizar_slots(id_p, nivel_m, novo_valor)
            messagebox.showinfo("Sucesso", f"{nome_m} conjurado! Restam {novo_valor} slots de nível {nivel_m}.")
        else:
            messagebox.showerror("Esgotado", f"Sem espaços de magia de nível {nivel_m}!")

    def abrir_janela_busca_magias(id_p, tree_principal):
        janela = tk.Toplevel()
        janela.title("Aprender Magia")
        janela.geometry("700x500")
        janela.columnconfigure(0, weight=1)
        janela.rowconfigure(1, weight=1)

        f_busca = tk.Frame(janela)
        f_busca.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        f_busca.columnconfigure(1, weight=1)

        tk.Label(f_busca, text="Filtro:").grid(row=0, column=0)
        ent_f = tk.Entry(f_busca)
        ent_f.grid(row=0, column=1, sticky="ew", padx=5)

        cols = ("ID", "Nome", "Nível", "Escola")
        t_res = ttk.Treeview(janela, columns=cols, show="headings")
        for c in cols:
            t_res.heading(c, text=c)
            t_res.column(c, width=100, anchor="center")
        t_res.grid(row=1, column=0, sticky="nsew", padx=10)

        def pesquisar(event=None):
            for i in t_res.get_children(): t_res.delete(i)
            resultados = MagiaDAO.buscar_magias_por_nome(ent_f.get())
            for r in resultados:
                t_res.insert("", "end", values=(r['id_magia'], r['nome_magia'], r['nivel'], r['escola']))

        ent_f.bind("<KeyRelease>", pesquisar)

        def aprender():
            sel = t_res.selection()
            if not sel: return
            val = t_res.item(sel)['values']
            try:
                MagiaDAO.aprender_magia(id_p, val[0])
                carregar_magias_personagem(id_p, tree_principal)
                messagebox.showinfo("Sucesso", f"{val[1]} aprendida!")
            except:
                messagebox.showwarning("Erro", "Você já conhece esta magia.")

        tk.Button(janela, text="Aprender Selecionada", bg="#28a745", fg="white", command=aprender).grid(row=2, column=0, pady=10)
        pesquisar()

    aba_magias.columnconfigure(0, weight=1)
    aba_magias.rowconfigure(1, weight=1)

    frame_topo = tk.Frame(aba_magias)
    frame_topo.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

    tk.Button(frame_topo, text="📖 Aprender Magia", bg="#17a2b8", fg="white",
            command=lambda: abrir_janela_busca_magias(id_personagem, tabela_magias)).grid(row=0, column=0, padx=5)

    colunas_m = ("ID", "Nome", "Nível", "Escola", "Tempo", "Alcance", "Dano")
    tabela_magias = ttk.Treeview(aba_magias, columns=colunas_m, show="headings")

    for col in colunas_m:
        tabela_magias.heading(col, text=col)
        tabela_magias.column(col, width=90, anchor="center")

    tabela_magias.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    scroll_m = ttk.Scrollbar(aba_magias, orient="vertical", command=tabela_magias.yview)
    tabela_magias.configure(yscrollcommand=scroll_m.set)
    scroll_m.grid(row=1, column=1, sticky="ns")

    btn_cast = tk.Button(aba_magias, text="⚡ CONJURAR", bg="#007bff", fg="white", font=("Arial", 11, "bold"),
                        command=lambda: realizar_conjuracao(id_personagem, tabela_magias))
    btn_cast.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

    btn_rest = tk.Button(
        aba_magias,
        text="⛺ DESCANSO LONGO (RESTAURAR TUDO)",
        bg="#28a745",
        fg="white",
        font=("Arial", 11, "bold"),
        command=lambda: realizar_descanso_longo(id_personagem, tabela_magias)
    )
    btn_rest.grid(row=3, column=0, sticky="ew", padx=20, pady=(5, 15))
    carregar_magias_personagem(id_personagem,tabela_magias)

# Exibe Ficha do Monstro
def mostra_monstro(id_monstro):
    p = MonstroDAO.buscar_por_id(id_monstro)

    ficha = tk.Toplevel(janela)
    ficha.title(f"Inimigo: {p['nome']}")
    ficha.geometry("540x450")
    ficha.grid_rowconfigure(0,weight=1)
    ficha.grid_columnconfigure(0,weight=1)

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

    frame_acoes = tk.LabelFrame(ficha,text="Ações:")
    frame_acoes.grid(row=0,column=1,padx=(3,3),pady=(3,3),sticky="nsew")

    resultado = MonstroDAO.obter_descricao_acoes(id_monstro)

    if resultado and resultado['descricao_acoes']:
        texto_acoes = resultado['descricao_acoes']
    else:
        texto_acoes = "Este monstro não possui ações especiais registradas."

    lbl_desc = tk.Label(frame_acoes, text=texto_acoes, wraplength=250, justify="left", anchor="nw")
    lbl_desc.pack(padx=5, pady=5, expand=True, fill="both")

# Função auxiliar para buscar os dados (coloque fora da criar_tela_inicio) ---
def obter_contagens_resumo():
    try:
        total_herois = PersonagemDAO.contar_herois()
        total_monstros = MonstroDAO.contar_monstros()
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
    for i in tabela_treeview.get_children():
        tabela_treeview.delete(i)

    itens = InventarioDAO.listar_inventario_personagem(id_personagem)

    peso_total_acumulado = 0.0

    for item in itens:
        p_total = item['quantidade'] * item['Peso']
        peso_total_acumulado += p_total

        simbolo = "☑" if item['equipado'] else "☐"
        slot = item['local_equipado'] if item['local_equipado'] else ""

        tabela_treeview.insert("", "end", iid=item['id_inventario'], values=(
            item['Nome_equi'],
            item['quantidade'],
            item['Peso'],
            p_total,
            item['Tipo_equi'],
            simbolo,
            slot
        ))

    InventarioDAO.atualizar_carga_atual(id_personagem, peso_total_acumulado)

    lbl_peso_status.config(text=f"Pes: {peso_total_acumulado:.1f} / {carga_max}kg")

    if peso_total_acumulado > carga_max:
        lbl_peso_status.config(fg="red")
    else:
        lbl_peso_status.config(fg="black")

# Adicionar Item inventario
def abrir_janela_selecao(id_personagem, tabela_inventario_principal, lbl_peso_status, carga_max):
    janela_busca = tk.Toplevel()
    janela_busca.title("Adicionar Item ao Inventário")
    janela_busca.geometry("500x400")
    janela_busca.grab_set()

    frame_busca = tk.Frame(janela_busca, pady=10)
    frame_busca.pack(fill="x")

    tk.Label(frame_busca, text="Buscar Item:").pack(side="left", padx=5)
    ent_busca = tk.Entry(frame_busca)
    ent_busca.pack(side="left", fill="x", expand=True, padx=5)

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

    def pesquisar_itens(event=None):
        for i in tabela_busca.get_children():
            tabela_busca.delete(i)

        resultados = InventarioDAO.buscar_equipamentos_por_nome(ent_busca.get())

        for item in resultados:
            tabela_busca.insert("", "end", values=(
                item['id_equipamento'], item['Nome_equi'], item['Tipo_equi'], item['Peso']
            ))

    ent_busca.bind("<KeyRelease>", pesquisar_itens)

    def confirmar_selecao():
        selecionado = tabela_busca.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item da lista!")
            return

        valores = tabela_busca.item(selecionado)['values']
        id_item = valores[0]
        nome_item = valores[1]

        quantidade = simpledialog.askinteger(
            "Quantidade",
            f"Quantas unidades de {nome_item} deseja adicionar?",
            parent=janela_busca,
            minvalue=1,
            initialvalue=1
        )

        if quantidade is None:
            return

        try:
            InventarioDAO.adicionar_item(id_personagem, id_item, quantidade)
            atualizar_inventario_e_peso_ui(id_personagem, tabela_inventario_principal, lbl_peso_status, carga_max)
            janela_busca.destroy()
            messagebox.showinfo("Sucesso", f"{quantidade}x {nome_item} adicionado ao inventário!")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao adicionar: {e}")

    btn_confirmar = tk.Button(janela_busca, text="Adicionar Selecionado",
                             bg="#28a745", fg="white", command=confirmar_selecao)
    btn_confirmar.pack(pady=10)

    pesquisar_itens()

# Remove item inventario
def remover_item_selecionado(id_personagem, tabela_treeview, lbl_peso_status, carga_max):
    item_selecionado = tabela_treeview.selection()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um item para remover!")
        return

    id_inv = item_selecionado[0]

    if messagebox.askyesno("Confirmar", "Deseja remover este item do inventário?"):
        InventarioDAO.remover_item(id_inv)
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
raca = ReferenciaDAO.lista_racas()
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
alinhamentos = ReferenciaDAO.lista_alinhamentos()
combo_alinhamentos = ttk.Combobox(criacao,values = alinhamentos, state= "readonly", width= 12)
combo_alinhamentos.grid(row= 3, column= 1,padx=(1,1),pady= (2,2),sticky= "w")

# Label Informativa Classe
tk.Label(criacao,text = 'Classe:', font=("Arial",8,"bold")).grid(row = 4, column = 0,padx=(1,1),pady= (2,2),sticky= "w")

# Combo Classes
classe = ReferenciaDAO.lista_classes()
combo_classe = ttk.Combobox(criacao, values=classe,state="readonly", width = 12)
combo_classe.grid(row = 4,column = 1,padx=(1,1),pady= (2,2),sticky= "w")

# Label Informativa Sub-Classe
tk.Label(criacao,text = 'Arquetipos:', font=("Arial",8,"bold")).grid(row = 4, column = 2,pady= (2,2),sticky= "w")

# Combo Sub-Classes
Sub_Classe = ReferenciaDAO.lista_sub_classes()
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
    raca_escolhida = combo_racas.get()
    id_raca = ReferenciaDAO.obter_id_raca(raca_escolhida)

    sracas = ReferenciaDAO.obter_sub_racas_por_raca(id_raca)

    lista_sracas = [sracas[0] for sracas in sracas]
    combo_s_racas['values'] = lista_sracas
    combo_s_racas.set("")

    print(f'O jogador escolheu: {raca_escolhida}')

# Função de click ao selecionar a Classe desejada.
def classe_selecionada(event):
    classe_escolhida = combo_classe.get()
    id = ReferenciaDAO.obter_id_classe(classe_escolhida)

    sub_classes = ReferenciaDAO.obter_sub_classes_por_classe(id)

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