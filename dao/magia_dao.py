import database as db

class MagiaDAO:
    @staticmethod
    def buscar_slots(id_personagem, nivel_magia):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT slots_atuais FROM Espacos_Magia WHERE id_personagem = %s AND nivel_magia = %s", (id_personagem, nivel_magia))
        res = cursor.fetchone()
        conn.close()
        return res

    @staticmethod
    def atualizar_slots(id_personagem, nivel_magia, novo_valor):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Espacos_Magia SET slots_atuais = %s WHERE id_personagem = %s AND nivel_magia = %s",
                       (novo_valor, id_personagem, nivel_magia))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_magias_conhecidas(id_personagem):
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
        cursor.execute(query, (id_personagem,))
        magias = cursor.fetchall()
        conn.close()
        return magias

    @staticmethod
    def listar_top3_magias(id_personagem):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT m.id_magia, m.nome_magia, m.nivel
            FROM magias m
            JOIN magias_conhecidas mc ON m.id_magia = mc.id_magia
            WHERE mc.id_personagem = %s
            ORDER BY m.nivel ASC LIMIT 3
        """
        cursor.execute(query, (id_personagem,))
        magias = cursor.fetchall()
        conn.close()
        return magias

    @staticmethod
    def restaurar_slots_max(id_personagem):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Espacos_Magia SET slots_atuais = slots_max WHERE id_personagem = %s", (id_personagem,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_magias_por_nome(termo):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_magia, nome_magia, nivel, escola FROM magias WHERE nome_magia LIKE %s", (f"%{termo}%",))
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    @staticmethod
    def aprender_magia(id_personagem, id_magia):
        conn = db.conexao()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO magias_conhecidas (id_personagem, id_magia) VALUES (%s, %s)", (id_personagem, id_magia))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
