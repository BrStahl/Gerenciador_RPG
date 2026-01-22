import database as db

class ReferenciaDAO:
    @staticmethod
    def lista_racas():
        return db.lista_racas()

    @staticmethod
    def lista_classes():
        return db.lista_classes()

    @staticmethod
    def lista_alinhamentos():
        return db.lista_alinhamentos()

    @staticmethod
    def lista_sub_classes():
        return db.lista_Sub_Classe()

    @staticmethod
    def obter_id_raca(nome_raca):
        return db.id_raca(nome_raca)

    @staticmethod
    def obter_id_classe(nome_classe):
        return db.id_classe(nome_classe)

    @staticmethod
    def obter_bonus_raca(nome_raca):
        conn = db.conexao()
        cursor = conn.cursor()
        query = "SELECT Forca, Inteligencia, Constituicao, Destreza, Sabedoria, Carisma FROM Racas WHERE nome_raca = %s"
        cursor.execute(query, (nome_raca,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado

    @staticmethod
    def obter_dado_vida_classe(nome_classe):
        conn = db.conexao()
        cursor = conn.cursor()
        query = "SELECT dado_vida FROM Classes WHERE nome_classe = %s"
        cursor.execute(query, (nome_classe,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado

    @staticmethod
    def obter_sub_racas_por_raca(id_raca):
        conn = db.conexao()
        cursor = conn.cursor()
        query = "SELECT nome_subraca FROM Sub_racas WHERE id_raca = %s"
        cursor.execute(query, (id_raca,))
        resultado = cursor.fetchall()
        conn.close()
        return resultado

    @staticmethod
    def obter_sub_classes_por_classe(id_classe):
        conn = db.conexao()
        cursor = conn.cursor()
        query = "SELECT nome_subclasse FROM Sub_Classes WHERE id_classe = %s"
        cursor.execute(query, (id_classe,))
        resultado = cursor.fetchall()
        conn.close()
        return resultado
