import requests
import mysql.connector
from deep_translator import GoogleTranslator
import os
import sys

# Adiciona o diretório pai ao path para importar dao
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dao import MonstroDAO

def traduzir_rpg(texto):
    if not texto:
        return ""
    try:
        # Traduz de Inglês (en) para Português (pt)
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except Exception:
        return texto

def popular_bestiario_local(limite=200):
    url = f"https://api.open5e.com/monsters/?limit={limite}"

    try:
        # 2. Busca os dados na API com timeout seguro
        print("Buscando monstros na API... Aguarde.")
        resposta = requests.get(url, timeout=20)
        resposta.raise_for_status()
        dados_api = resposta.json()

        print(f"Inserindo {len(dados_api['results'])} monstros no banco...")

        for monstro in dados_api['results']:
            # TRADUÇÃO DOS CAMPOS SELECIONADOS
            nome_pt = traduzir_rpg(monstro['name'])
            tipo_pt = traduzir_rpg(monstro['type'])

            # O campo 'actions' da API é uma lista complexa.
            # Podemos pegar apenas o nome da primeira ação para simplificar agora.
            acao_desc = ""
            if monstro.get('actions'):
                primeira_acao = monstro['actions'][0]['name'] + ": " + monstro['actions'][0]['desc']
                acao_desc = traduzir_rpg(primeira_acao)

            # Preparar dados para o DAO
            dados_monstro = {
                'nome': nome_pt,
                'tipo': tipo_pt,
                'ca': monstro['armor_class'],
                'hp_max': monstro['hit_points'],
                'nivel_desafio': monstro['challenge_rating'],
                'forca': monstro['strength'],
                'destreza': monstro['dexterity'],
                'constituicao': monstro['constitution'],
                'descricao_acoes': acao_desc
            }

            # INSERT NO BANCO LOCAL VIA DAO
            MonstroDAO.inserir_monstro(dados_monstro)

        print(f"Finalizado! Monstros traduzidos e salvos no banco local.")

    except requests.exceptions.RequestException as e:
        print(f"Erro na API: {e}")
    except mysql.connector.Error as err:
        print(f"Erro no Banco de Dados: {err}")
    except Exception as e:
        print(f"Erro geral: {e}")


# Executa a função
popular_bestiario_local(50)
