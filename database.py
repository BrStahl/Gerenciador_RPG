import mysql.connector
from tkinter import ttk, messagebox

# Remove Caracateres Especias
def remove_caracter(str):
    novo_valor = str.replace('(','').replace(')','').replace("'","").replace(',','')

    return novo_valor

# Realiza Conexão com Banco
def conexao():
    try:
        return mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "RPG"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Conexão", f"Erro: {err}")
        return None     

# Buscas as Raças Cadastradas.
def lista_racas():
    racas_formatada = []
    conn = conexao()

    if conn:
        cursor = conn.cursor()

        query = 'SELECT nome_raca FROM Racas'

        cursor.execute(query)
        racas = cursor.fetchall()

        for i in racas:
            raca_formatada = remove_caracter(str(i))
            racas_formatada.append(raca_formatada)

        cursor.close()
        conn.close()

        return racas_formatada
    return []

# Busca as Classe Cadastradas.
def lista_classes():
    classes_formatada = []
    conn = conexao()

    if conn:
        cursor = conn.cursor()

        query = 'SELECT nome_classe FROM Classes'

        cursor.execute(query)
        classes = cursor.fetchall()

        for i in classes:
            classe_formatada = remove_caracter(str(i))
            classes_formatada.append(classe_formatada)

        cursor.close()
        conn.close()

        return classes_formatada
    return []

# Busca os Alinhamentos
def lista_alinhamentos():
    alinhamentos_formatado = []
    conn = conexao()

    if conn:
        cursor = conn.cursor()

        query = 'SELECT nome_alinhamento FROM Alinhamento'

        cursor.execute(query)
        alinhamentos = cursor.fetchall()

        for i in alinhamentos:
            alinhamento_formatado = remove_caracter(str(i))
            alinhamentos_formatado.append(alinhamento_formatado)

        cursor.close()
        conn.close()

        return alinhamentos_formatado
    return []

# Lista as Sub Classes da Classe Selecionada
def lista_Sub_Classe():
    Sub_classes_formatada = []
    conn = conexao()

    if conn:
        cursor = conn.cursor()

        query = f"SELECT nome_subclasse FROM Sub_Classes WHERE id_classe = 0"

        cursor.execute(query)
        Sub_classes = cursor.fetchall()

        for i in Sub_classes:
            Sub_classe_formatada = remove_caracter(str(i))
            Sub_classes_formatada.append(Sub_classe_formatada)

        cursor.close()
        conn.close()

        return Sub_classes_formatada
    return []

# Função para pegar Id da Classe para usar no WHERE da função lista_Sub_Classe()
def id_classe(classe):
    conn = conexao()

    if conn:
        cursor = conn.cursor()

        query = f"SELECT id_classe FROM Classes WHERE nome_classe = '{classe}'"

        cursor.execute(query)
        id_classe = cursor.fetchall()
        id_formatado = str(id_classe).replace('(','').replace(')','').replace("'","").replace(',','').replace("[","").replace("]","")

        return id_formatado
    return []

# Funcção para buscar o id_Raca para aplicar os Bonus da Raca nos ATR
def id_raca(raca):
    conn = conexao()

    if conn:
        cursor = conn.cursor()

        query = f"SELECT id_raca FROM Racas WHERE nome_raca = '{raca}'"

        cursor.execute(query)
        id_classe = cursor.fetchall()
        id_formatado = str(id_classe).replace('(','').replace(')','').replace("'","").replace(',','').replace("[","").replace("]","")

        return id_formatado
    return []