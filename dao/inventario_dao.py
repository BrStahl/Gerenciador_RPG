import database as db

class InventarioDAO:
    @staticmethod
    def buscar_itens_iniciais(id_raca):
        conn = db.conexao()
        cursor = conn.cursor()
        query = "SELECT nome_item, quantidade FROM Itens_Iniciais WHERE id_raca = %s"
        cursor.execute(query, (id_raca,))
        itens = cursor.fetchall()
        conn.close()
        return itens

    @staticmethod
    def listar_inventario_personagem(id_personagem):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT IP.id_inventario, E.Nome_equi, IP.quantidade, E.Peso, E.Tipo_equi,
                   IP.equipado, IP.local_equipado, E.id_equipamento
            FROM Inventario_Personagem IP
            JOIN equipamento E ON IP.id_equipamento = E.id_equipamento
            WHERE IP.id_personagem = %s
        """
        cursor.execute(query, (id_personagem,))
        itens = cursor.fetchall()
        conn.close()
        return itens

    @staticmethod
    def atualizar_equipado(id_inventario, status, slot):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Inventario_Personagem SET equipado = %s, local_equipado = %s WHERE id_inventario = %s",
                       (status, slot, id_inventario))
        conn.commit()
        conn.close()

    @staticmethod
    def atualizar_quantidade(id_inventario, nova_qtd):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Inventario_Personagem SET quantidade = %s WHERE id_inventario = %s",
                       (nova_qtd, id_inventario))
        conn.commit()
        conn.close()

    @staticmethod
    def remover_item(id_inventario):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Inventario_Personagem WHERE id_inventario = %s", (id_inventario,))
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar_item(id_personagem, id_equipamento, quantidade):
        conn = db.conexao()
        cursor = conn.cursor()
        sql = "INSERT INTO Inventario_Personagem (id_personagem, id_equipamento, quantidade) VALUES (%s, %s, %s)"
        cursor.execute(sql, (id_personagem, id_equipamento, quantidade))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_equipamentos_por_nome(termo):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id_equipamento, Nome_equi, Tipo_equi, Peso FROM equipamento WHERE Nome_equi LIKE %s"
        cursor.execute(query, (f"%{termo}%",))
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    @staticmethod
    def obter_detalhes_item(id_inventario):
        conn = db.conexao()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT E.Propriedades, E.Dado_dano, E.Tipo_dano
            FROM Inventario_Personagem IP
            JOIN equipamentos E ON IP.id_equipamento = E.id_equipamento
            WHERE IP.id_inventario = %s
        """
        cursor.execute(query, (id_inventario,))
        res = cursor.fetchone()
        conn.close()
        return res

    @staticmethod
    def atualizar_carga_atual(id_personagem, novo_peso):
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE Personagens SET Carga_atual = %s WHERE id_personagem = %s",
                       (novo_peso, id_personagem))
        conn.commit()
        conn.close()

    @staticmethod
    def contar_equipamentos():
        conn = db.conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipamentos")
        total = cursor.fetchone()[0]
        conn.close()
        return total
