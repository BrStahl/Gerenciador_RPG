import requests
import mysql.connector
from deep_translator import GoogleTranslator

# 1. Configuração de Tradução
def traduzir_rpg(texto):
    if not texto or texto == "null": return ""
    try:
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except:
        return texto

def popular_biblioteca_magias(limite=30):
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "rpg"
    }

    # Endpoint v2 específico para Spells
    url = f"https://api.open5e.com/v2/spells/?limit={limite}"
    
    try:
        print("Conectando à API Open5e v2 (Magias)...")
        resposta = requests.get(url, timeout=20)
        dados_api = resposta.json()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for magia in dados_api['results']:
            # --- Extração v2 ---
            nome_en = magia['name']
            nivel = magia['level'] # A v2 já traz o nível como inteiro
            
            # Escola é um objeto na v2: magia['school']['name']
            escola_en = magia['school']['name'] if magia['school'] else "Universal"
            
            tempo_en = magia['casting_time']
            alcance_en = magia['range']
            desc_en = magia['desc'][:500] # Limitamos para não estourar a tradução

            # --- Tradução Técnica ---
            print(f"Importando e Traduzindo: {nome_en}...")
            nome_pt = traduzir_rpg(nome_en)
            escola_pt = traduzir_rpg(escola_en)
            tempo_pt = traduzir_rpg(tempo_en)
            alcance_pt = traduzir_rpg(alcance_en)
            desc_pt = traduzir_rpg(desc_en)

            # --- Lógica de Dano ---
            # Algumas magias v2 têm o campo 'damage', outras não.
            dano = "N/A"
            if 'damage' in magia and magia['damage']:
                dano = magia['damage'].get('damage_at_character_level', "Efeito variado")

            # --- Inserção ---
            sql = """
                INSERT INTO magias 
                (nome_magia, nivel, escola, tempo_conjuracao, alcance, descricao, dano_cura)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # Escolha de ícone baseada na escola de magia
            icones = {
                "Evocação": "delapouite/fire-ball.png",
                "Cura": "delapouite/health-normal.png",
                "Necromancia": "delapouite/skull-mask.png"
            }
            icone = icones.get(escola_pt, "delapouite/magic-swirl.png")

            valores = (nome_pt, nivel, escola_pt, tempo_pt, alcance_pt, desc_pt, dano)
            cursor.execute(sql, valores)
            
        conn.commit()
        print(f"\nSucesso! {len(dados_api['results'])} magias traduzidas e salvas.")

    except Exception as e:
        print(f"Erro no processo: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Rodar a importação
popular_biblioteca_magias(50)