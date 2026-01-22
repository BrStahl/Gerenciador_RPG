import requests
import mysql.connector
from deep_translator import GoogleTranslator

def traduzir_rpg(texto):
    if not texto:
        return ""
    try:
        # Traduz de Inglês (en) para Português (pt)
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except Exception:
        return texto
    
def popular_bestiario_local(limite=200):
    # 1. Configurações de Conexão (Ajuste para seu banco local)
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "rpg"
    }

    url = f"https://api.open5e.com/monsters/?limit={limite}"
    
    try:
        # 2. Busca os dados na API com timeout seguro
        print("Buscando monstros na API... Aguarde.")
        resposta = requests.get(url, timeout=20)
        resposta.raise_for_status()
        dados_api = resposta.json()

        # 3. Conecta ao Banco Local
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

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

            # INSERT NO BANCO LOCAL
            sql = """
                INSERT INTO inimigos 
                (nome, tipo, ca, hp_max, nivel_desafio, forca, destreza, constituicao, descricao_acoes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                nome_pt, 
                tipo_pt, 
                monstro['armor_class'], 
                monstro['hit_points'], 
                monstro['challenge_rating'], 
                monstro['strength'], 
                monstro['dexterity'], 
                monstro['constitution'],
                acao_desc
            )
            cursor.execute(sql, valores)
            
        conn.commit()
        print(f"Finalizado! Monstros traduzidos e salvos no banco local.")  

    except requests.exceptions.RequestException as e:
        print(f"Erro na API: {e}")
    except mysql.connector.Error as err:
        print(f"Erro no Banco de Dados: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# Executa a função
popular_bestiario_local(50)
