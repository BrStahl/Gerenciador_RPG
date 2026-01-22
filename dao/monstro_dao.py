import database as db

class MonstroDAO:
    @staticmethod
    def listar_monstros():
        conn = db.conexao()
        cursor = conn.cursor()
        query = "SELECT id_inimigo, nome, tipo, hp_max, ca, forca, nivel_desafio FROM inimigos"
        cursor.execute(query)
        monstros = cursor.fetchall()
        conn.close()
        return monstros

    @staticmethod
    def buscar_por_id(id_monstro):
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
        monstro = cursor.fetchone()
        conn.close()
        return monstro

    @staticmethod
    def obter_descricao_acoes(id_monstro):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT descricao_acoes FROM inimigos WHERE id_inimigo = %s"
        cursor.execute(query, (id_monstro,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado

    @staticmethod
    def contar_monstros():
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inimigos")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    @staticmethod
    def inserir_monstro(dados):
        conn = db.conexao()
        cursor = conn.cursor()
        sql = """
            INSERT INTO inimigos
            (nome, tipo, ca, hp_max, nivel_desafio, forca, destreza, constituicao, descricao_acoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados['nome'], dados['tipo'], dados['ca'], dados['hp_max'],
            dados['nivel_desafio'], dados['forca'], dados['destreza'],
            dados['constituicao'], dados['descricao_acoes']
        )
        cursor.execute(sql, valores)
        conn.commit()
        conn.close()
