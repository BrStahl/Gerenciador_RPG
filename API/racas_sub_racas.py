import requests
import mysql.connector
from deep_translator import GoogleTranslator

# Função auxiliar para tradução
def traduzir_rpg(texto):
    if not texto: return ""
    try:
        # Traduz textos longos mantendo o sentido do RPG
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except:
        return texto

# Função para converter a lista ASI da API em colunas SQL
def processar_asi(lista_asi):
    stats = {
        "Strength": 0, "Intelligence": 0, "Constitution": 0, 
        "Dexterity": 0, "Wisdom": 0, "Charisma": 0
    }
    for bonus in lista_asi:
        for attr in bonus.get('attributes', []):
            if attr in stats:
                stats[attr] = bonus['value']
    return stats

# Popula tabela de Raças e Sub - Raças
def popular_sistema_raca(limite=50):
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "rpg"
    }

    url = f"https://api.open5e.com/v1/races/?limit={limite}"
    
    try:
        print("Iniciando carga de dados... Aguarde as traduções.")
        resposta = requests.get(url, timeout=20)
        dados_api = resposta.json()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for raca in dados_api['results']:
            # --- 1. PROCESSAMENTO DA RAÇA PAI ---
            nome_raca_pt = traduzir_rpg(raca['name'])
            stats_raca = processar_asi(raca.get('asi', []))
            
            # Extração de velocidade (valor numérico e texto)
            vel_num = raca.get('speed', {}).get('walk', 30)
            vel_desc = traduzir_rpg(raca.get('speed_desc'))

            sql_raca = """
                INSERT INTO Racas 
                (nome_raca, Forca, Inteligencia, Constituicao, Destreza, Sabedoria, Carisma, 
                 velocidade, velocidade_desc, descricao, Idade, Alinhamentos, Altura, Visao, Habilidades, Linguas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores_raca = (
                nome_raca_pt, stats_raca["Strength"], stats_raca["Intelligence"], stats_raca["Constitution"],
                stats_raca["Dexterity"], stats_raca["Wisdom"], stats_raca["Charisma"],
                vel_num, vel_desc, traduzir_rpg(raca.get('desc')), traduzir_rpg(raca.get('age')),
                traduzir_rpg(raca.get('alignment')), traduzir_rpg(raca.get('size')),
                traduzir_rpg(raca.get('vision')), traduzir_rpg(raca.get('traits')), traduzir_rpg(raca.get('languages'))
            )
            
            cursor.execute(sql_raca, valores_raca)
            
            # --- 2. VÍNCULO: PEGAR O ID GERADO ---
            id_pai = cursor.lastrowid
            
            # --- 3. PROCESSAMENTO DAS SUB-RAÇAS ---
            subraces_list = raca.get('subraces', [])
            if subraces_list:
                for sub in subraces_list:
                    nome_sub_pt = traduzir_rpg(sub['name'])
                    stats_sub = processar_asi(sub.get('asi', []))
                    
                    sql_sub = """
                        INSERT INTO Sub_Racas 
                        (id_raca, nome_subraca, Forca, Inteligencia, Constituicao, Destreza, Sabedoria, Carisma)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(sql_sub, (
                        id_pai, nome_sub_pt, stats_sub["Strength"], stats_sub["Intelligence"],
                        stats_sub["Constitution"], stats_sub["Dexterity"], stats_sub["Wisdom"], stats_sub["Charisma"]
                    ))
            
            print(f"Raça {nome_raca_pt} e suas sub-raças inseridas.")

        conn.commit()
        print("\nSucesso Total! Banco de dados atualizado.")

    except Exception as e:
        print(f"Erro crítico: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Inicie a carga
popular_sistema_raca(25)