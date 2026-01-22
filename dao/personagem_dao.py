import database as db

class PersonagemDAO:
    @staticmethod
    def atribuir_slots_por_nivel(id_personagem, nivel_personagem):
        conn = db.conexao()
        cursor = conn.cursor()

        PROGRESSAO_FULLCASTER = {
            1: [2],
            2: [3],
            3: [4, 2],
            4: [4, 3],
            5: [4, 3, 2],
        }

        slots = PROGRESSAO_FULLCASTER.get(nivel_personagem, [0])

        for i, qtd_max in enumerate(slots):
            nivel_magia = i + 1
            sql = """INSERT INTO Espacos_Magia (id_personagem, nivel_magia, slots_max, slots_atuais)
                     VALUES (%s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE slots_max=%s, slots_atuais=%s"""
            cursor.execute(sql, (id_personagem, nivel_magia, qtd_max, qtd_max, qtd_max, qtd_max))

        conn.commit()
        conn.close()

    @staticmethod
    def criar_personagem(dados):
        conn = db.conexao()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO
                        Personagens (id_personagem,nome,raca,sub_raca,classe,sub_classe,alinhamento,Forca,Inteligencia,Destreza,Constituicao,Carisma,Sabedoria,Vida_Max,Vida_Atual,defesa,Iniciativa,Carga_max,Carga_atual,XP,Lvl,Ouro)
                    VALUES (
                        '', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
            """
            valores = (
                dados['nome'], dados['raca'], dados['sub_raca'], dados['classe'], dados['sub_classe'], dados['alinhamento'],
                dados['forca'], dados['inteligencia'], dados['destreza'], dados['constituicao'], dados['carisma'], dados['sabedoria'],
                dados['vida_max'], dados['vida_atual'], dados['defesa'], dados['iniciativa'], dados['carga_max'], dados['carga_atual'], dados['xp'], dados['lvl'], dados['ouro']
            )
            cursor.execute(sql, valores)
            conn.commit()
            id_novo_personagem = cursor.lastrowid
            return id_novo_personagem
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def listar_herois():
        conn = db.conexao()
        cursor = conn.cursor()
        query = "SELECT id_Personagem, nome, Vida_Max, Defesa, classe, sub_classe, raca, Lvl FROM Personagens"
        cursor.execute(query)
        herois = cursor.fetchall()
        conn.close()
        return herois

    @staticmethod
    def buscar_por_id(id_personagem):
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
        resultado = cursor.fetchone()
        conn.close()
        return resultado

    @staticmethod
    def atualizar_foto(id_personagem, dados_binarios):
        conn = db.conexao()
        cursor = conn.cursor()
        sql = "UPDATE Personagens SET foto_personagem = %s WHERE id_personagem = %s"
        cursor.execute(sql, (dados_binarios, id_personagem))
        conn.commit()
        conn.close()

    @staticmethod
    def obter_descricao_raca(id_personagem):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT racas.descricao FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
        cursor.execute(query, (id_personagem,))
        res = cursor.fetchone()
        conn.close()
        return res

    @staticmethod
    def obter_detalhes_raca(id_personagem):
        # Agregando queries de detalhes de raça
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)

        queries = {
            'idade': "SELECT racas.Idade FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s",
            'altura': "SELECT racas.Altura FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s",
            'alinhamento': "SELECT racas.Alinhamentos FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s",
            'visao': "SELECT racas.Visao FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s",
            'idiomas': "SELECT racas.Linguas FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s",
            'habilidades': "SELECT racas.Habilidades FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s",
            'velocidade': "SELECT racas.Velocidade_desc FROM personagens P JOIN racas ON racas.nome_raca = P.raca WHERE P.id_personagem = %s"
        }

        resultados = {}
        for chave, sql in queries.items():
            cursor.execute(sql, (id_personagem,))
            resultados[chave] = cursor.fetchone()

        conn.close()
        return resultados

    @staticmethod
    def obter_detalhes_classe(id_personagem):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)

        queries = {
            'armadura': "SELECT C.armadura FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s",
            'ferramentas': "SELECT C.ferramentas FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s",
            'salvaguardas': "SELECT C.salvaguardas FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s",
            'pericias': "SELECT C.pericias FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s",
            'equipamento_inicial': "SELECT C.equipamento_inicial FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s",
            'atributo_conjuracao': "SELECT C.atributo_conjuracao FROM personagens P JOIN Classes C ON C.nome_classe = P.classe WHERE P.id_personagem = %s"
        }

        resultados = {}
        for chave, sql in queries.items():
            cursor.execute(sql, (id_personagem,))
            resultados[chave] = cursor.fetchone()

        conn.close()
        return resultados

    @staticmethod
    def obter_descricao_subclasse(id_personagem):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)

        # Obter nome da subclasse
        cursor.execute("SELECT sub_classe FROM personagens WHERE id_personagem = %s", (id_personagem,))
        res_sub = cursor.fetchone()

        if res_sub:
            cursor.execute("SELECT descricao FROM sub_classes WHERE nome_subclasse = %s", (res_sub['sub_classe'],))
            descricao = cursor.fetchone()
            conn.close()
            return descricao

        conn.close()
        return None

    @staticmethod
    def atualizar_hp_atual(id_personagem, novo_hp):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Personagens SET Vida_Atual = %s WHERE id_personagem = %s", (novo_hp, id_personagem))
        conn.commit()
        conn.close()

    @staticmethod
    def restaurar_hp_max(id_personagem):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Personagens SET Vida_Atual = Vida_Max WHERE id_personagem = %s", (id_personagem,))
        conn.commit()
        conn.close()

    @staticmethod
    def contar_herois():
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Personagens")
        total = cursor.fetchone()[0]
        conn.close()
        return total
