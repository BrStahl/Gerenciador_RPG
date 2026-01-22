import random
import tkinter as tk
from tkinter import ttk, messagebox
import database as db

# Classe e metodos do "Personagem"
class Personagem:
    
    # Criação do Personagens
    def __init__(self,Nome,Raca,Classe,Sub_Classe,Alinhamento,Forca,Destreza,Constituicao,Inteligencia,Sabedoria,Carisma):        
        Dado_vida = {
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
        self.Nome = Nome
        self.Raca = Raca
        self.Classe = Classe.title()
        self.Sub_Classe = Sub_Classe
        self.Alinhamento = Alinhamento
        self.XP = 0
        self.Level = 1

        # Modificadores
        Mod_Vida = (Constituicao - 10 ) // 2
        Mod_Des =  (Destreza - 10 ) // 2

        # Atributos
        self.Forca = Forca
        self.Destreza = Destreza
        self.Constituicao = Constituicao
        self.Inteligencia = Inteligencia
        self.Sabedoria = Sabedoria
        self.Carisma = Carisma
        self.Defesa = Mod_Des + 10
        self.Iniciativa = Mod_Des

        # Inventario
        self.Inventario = []
        self.Ouro = 0
        self.Arma_Dir = None
        self.Arma_Esq = None
        self.Armadura = None
        self.Carga_Max = self.Forca * 7
        self.Carga_Atual = 0.00
        
        Vida_Base = Dado_vida.get(self.Classe,8)

        # Vida e Defesa
        self.HP_Max = Mod_Vida + Vida_Base
        self.HP_Atual = self.HP_Max

    # Exibe dados do Personsagem
    def exibe(self):
        print(f'{"="*40}')
        print(f' FICHA DE PERSONAGEM '.center(40, '='))
        print(f'{"="*40}')
        print(f'Nome: {self.Nome} | Level: {self.Level}')
        print(f'Raça: {self.Raca}')
        print(f'Classe: {self.Classe} | Sub-Classe: {self.Sub_Classe}')
        print(f'Natureza: {self.Alinhamento} | XP: {self.XP}')
        print(f'{"="*40}')
        print(f'Status de Combate '.center(40,'='))
        print(f'{"="*40}')  
        print(f'Vida: {self.HP_Atual} / {self.HP_Max}')
        print(f'Defesa: {self.Defesa} | Iniciativa: {self.Iniciativa}')     
        print('''Atributos''')
        print(f'FOR: {self.Forca} | DES: {self.Destreza} | Inteligencia: {self.Inteligencia}')
        print(f'SAB: {self.Sabedoria} | Carisma: {self.Carisma} | Constituição: {self.Constituicao}')
        print(f'{"="*40}')
        print(f'Inventario / Carga '.center(40,'='))
        print(f'{"="*40}')
        qtd_Inv = len(self.Inventario)
        if qtd_Inv == 0:
            print(f'Inventário Vazio!')
        else:
            print(f'Items: {self.Inventario}')
        print(f'Ouro: {self.Ouro:.2f}')

        status_carga = "Sobrecarregado" if self.Carga_Atual > (self.Carga_Max * 0.8) else 'Normal'
        print(f'Carga: {self.Carga_Atual}Kg / {self.Carga_Max}Kg | Status Carga: {status_carga}')
        print(f'{"="*40}')

    # Remove Item Inventario
    def remove_item(self,nome,peso):
        if not self.Inventario:
            print("Inventário vazio!")
            return
        try:
            x = 1
       
            for item in self.Inventario:   
                print(f'[{x}] - {item[0]} ({item[1]}Kg)')
                x +=1

            escolha = int(input('Qual item deseja soltar: '))
            indice = escolha - 1
            item_removido = self.Inventario.pop(indice)
            peso_removido = item_removido[1]

            self.Carga_Atual -= peso_removido

            print(f'{item_removido} jogado Fora!.')

            if self.Carga_Atual < (self.Carga_Max * 0.8):
                self.Iniciativa = (self.Destreza - 10) // 2
                print('Voce esta sentindo mais leve, iniciativa restaurada!')
                self.adiciona_item_inv(nome,peso)
        except:
            print('Escolha Invalida!')

    # Adiciona Item ao Inventario
    def adiciona_item_inv(self,nome,peso) :
        if self.Carga_Atual + peso <= self.Carga_Max:
            self.Inventario.append([nome,peso])
            self.Carga_Atual += peso

            if self.Carga_Atual >= (self.Carga_Max * 0.8):
                mod_des = (self.Destreza - 10) // 2
                self.Iniciativa = mod_des //2 
                print(f'{nome} adicionado ao Inventario!')
                print('Seu personagem está pesado,iniciativa reduzida pela metade!')
            else:
                print(f'{nome} adicionado ao Inventario!')
                self.Iniciativa = (self.Destreza - 10) // 2
        else:
            print(f'{nome} item não adicionado, peso excessivo')
            escolha = input('Deseja jogar fora algum item? [S]im [N]ão: ').lower()

            if escolha == 's':
                self.remove_item(nome,peso)
            else:
                print(f'{nome} Não foi Equipado!')

