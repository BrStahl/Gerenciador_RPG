import requests
import mysql.connector
from deep_translator import GoogleTranslator

# 1. Função de Tradução (Mantendo sua lógica original)
def traduzir_rpg(texto):
    if not texto or texto == "N/A":
        return ""
    try:
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except Exception:
        return texto

# 2. Mapeamento de Tipos para o seu ENUM (Arma, Armadura, etc.)
MAPEAMENTO_TIPOS = {
    'Simple Melee Weapons': 'Arma',
    'Martial Melee Weapons': 'Arma',
    'Simple Ranged Weapons': 'Arma',
    'Martial Ranged Weapons': 'Arma',
    'Light Armor': 'Armadura',
    'Medium Armor': 'Armadura',
    'Heavy Armor': 'Armadura',
    'Shield': 'Armadura'
}

def popular_equipamentos(endpoint="weapons", limite=20):
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "rpg"
    }

    url = f"https://api.open5e.com/v1/{endpoint}/?limit={limite}"
    
    try:
        print(f"Buscando {endpoint} na API...")
        resposta = requests.get(url, timeout=20)
        resposta.raise_for_status()
        dados_api = resposta.json()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for equip in dados_api['results']:
            # --- TRADUÇÃO E LIMPEZA DOS CAMPOS ---
            nome_pt = traduzir_rpg(equip['name'])
            
            # Mapeia a categoria da API para o seu ENUM local
            tipo_original = equip.get('category', '')
            tipo_final = MAPEAMENTO_TIPOS.get(tipo_original, 'Arma' if endpoint == "weapons" else 'Armadura')

            # Limpeza de valores numéricos (Custo e Peso)
            # Remove letras (gp, lb) para manter apenas o número para colunas DECIMAL/FLOAT
            custo_limpo = ''.join(filter(lambda x: x.isdigit() or x == '.', equip.get('cost', '0'))) or "0"
            peso_limpo = ''.join(filter(lambda x: x.isdigit() or x == '.', equip.get('weight', '0'))) or "0"

            # Tratamento de propriedades e descrição
            prop_lista = [traduzir_rpg(p) for p in (equip.get('properties') or [])]
            prop_texto = ", ".join(prop_lista) if prop_lista else "Nenhuma"

            # --- CAMPOS ESPECÍFICOS (Dano ou Defesa) ---
            dado_dano = equip.get('damage_dice', None)
            tipo_dano_pt = traduzir_rpg(equip.get('damage_type', ''))
            
            # Se for armadura, extraímos o bônus de CA da string (ex: "13 + Dex" vira 13)
            defesa_bonus = 0
            if 'ac_string' in equip:
                ac_str = equip['ac_string'].split()[0]
                defesa_bonus = int(''.join(filter(str.isdigit, ac_str))) if any(str.isdigit(c) for c in ac_str) else 0

            # --- INSERT NO BANCO (Sem passar o ID para usar AUTO_INCREMENT) ---
            sql = """
                INSERT INTO equipamentos 
                (nome_equi, tipo_equi, dado_dano, tipo_dano, defesa_bonus, custo, peso, propriedades)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores = (
                nome_pt, 
                tipo_final, 
                dado_dano, 
                tipo_dano_pt, 
                defesa_bonus,
                custo_limpo, 
                peso_limpo, 
                prop_texto,
            )
            
            cursor.execute(sql, valores)
            print(f"Salvo: {nome_pt} ({tipo_final})")
            
        conn.commit()
        print(f"\nSucesso! {len(dados_api['results'])} itens processados.")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Execução: Você pode chamar para armas ou armaduras
popular_equipamentos("weapons", 50)
# popular_equipamentos("armor", 10)