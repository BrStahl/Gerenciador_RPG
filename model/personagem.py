
class Personagem:

    # Criação do Personagens
    def __init__(self,nome,raca,classe,sub_classe,alinhamento,forca,destreza,constituicao,inteligencia,sabedoria,carisma):
        dado_vida = {
            'Bárbaro': 12,
            'Bardo': 8,
            'Clérico': 8,
            'Druida': 8,
            'Lutador': 10,
            'Monge': 8,
            'Paladino': 10,
            'Caçador': 10,
            'Assassino': 8,
            'Mago': 6,
            'Warlock': 6,
            'Bruxo': 6
        }

        # Identidade e Progressão de Lvl
        self.nome = nome
        self.raca = raca
        self.classe = classe.title()
        self.sub_classe = sub_classe
        self.alinhamento = alinhamento
        self.xp = 0
        self.lvl = 1

        # Modificadores
        self.mod_vida = (constituicao - 10 ) // 2
        self.mod_des =  (destreza - 10 ) // 2

        # Atributos
        self.forca = forca
        self.destreza = destreza
        self.constituicao = constituicao
        self.inteligencia = inteligencia
        self.sabedoria = sabedoria
        self.carisma = carisma
        self.defesa = self.mod_des + 10
        self.iniciativa = self.mod_des

        # Inventario
        self.ouro = 0
        self.carga_max = self.forca * 7
        self.carga_atual = 0.00

        vida_base = dado_vida.get(self.classe,8)

        # Vida e Defesa
        self.vida_max = self.mod_vida + vida_base
        self.vida_atual = self.vida_max

    def to_dict(self):
        return {
            'nome': self.nome,
            'raca': self.raca,
            'classe': self.classe,
            'sub_classe': self.sub_classe,
            'alinhamento': self.alinhamento,
            'forca': self.forca,
            'destreza': self.destreza,
            'constituicao': self.constituicao,
            'inteligencia': self.inteligencia,
            'sabedoria': self.sabedoria,
            'carisma': self.carisma,
            'vida_max': self.vida_max,
            'vida_atual': self.vida_atual,
            'defesa': self.defesa,
            'iniciativa': self.iniciativa,
            'carga_max': self.carga_max,
            'carga_atual': self.carga_atual,
            'xp': self.xp,
            'lvl': self.lvl,
            'ouro': self.ouro
        }
