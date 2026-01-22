import requests
import mysql.connector
from deep_translator import GoogleTranslator

# --- CONFIGURAÇÃO DE TRADUÇÃO ---
def traduzir_rpg(texto):
    if not texto or texto == "null": return ""
    try:
        # Traduz de Inglês para Português
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except:
        return texto

# --- MAPEAMENTO PARA O SEU ENUM LOCAL ---
# Filtramos categorias que NÃO são Arma nem Armadura
MAPEAMENTO_CATEGORIAS = {
    "potion": "Consumivel",
    "scroll": "Consumivel",
    "food-and-drink": "Consumivel",
    "wondrous-item": "Acessorio",
    "tools": "Ferramenta",
    "adventuring-gear": "Ferramenta",
    "gear": "Ferramenta"
}

def popular_itens_gerais(limite=50):
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "rpg"
    }

    # Endpoint focado em Itens (v2)
    url = f"https://api.open5e.com/v2/items/?limit={limite}"
    
    try:
        print("Buscando Itens Gerais na API Open5e v2...")
        resposta = requests.get(url, timeout=20)
        dados_api = resposta.json()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for item in dados_api['results']:
            cat_info = item.get('category')
            cat_key = cat_info['key'] if cat_info else "other"

            # PULO DO GATO: Ignora o que você já tem em outros módulos
            if cat_key in ["weapon", "armor"]:
                continue

            # Define o tipo com base no nosso mapeamento
            tipo_final = MAPEAMENTO_CATEGORIAS.get(cat_key, "Outros")

            # Tratamento de Peso e Custo
            peso = float(item['weight']) if item['weight'] else 0.0
            custo = float(item['cost']) if item['cost'] else 0.0

            # Tradução do Nome e Descrição (Lore/Propriedades)
            nome_pt = traduzir_rpg(item['name'])
            desc_pt = traduzir_rpg(item['desc'][:250]) # Limite para evitar erros de API

            # Ícone padrão por categoria para a sua API de Ícones
            icones_padrao = {
                "Consumivel": "delapouite/health-potion.png",
                "Acessorio": "delapouite/ring.png",
                "Ferramenta": "delapouite/hammer-nails.png",
                "Outros": "delapouite/backpack.png"
            }
            icone = icones_padrao.get(tipo_final, "delapouite/pouch.png")

            # Inserção na Tabela Universal
            sql = """
                INSERT INTO equipamentos 
                (Nome_equi, Tipo_equi, Dado_dano, Tipo_dano, Custo,Peso, Propriedades, Defesa_bonus)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Para itens gerais, dano e defesa são nulos ou zero
            valores = (nome_pt, tipo_final, None, None, custo, peso, desc_pt,0)
            
            try:
                cursor.execute(sql, valores)
                print(f"Importado: {nome_pt} ({tipo_final})")
            except mysql.connector.Error as err:
                print(f"Erro ao inserir {item['name']}: {err}")
            
        conn.commit()
        print(f"\nConcluído! A tabela 'equipamento' foi alimentada com itens gerais.")

    except Exception as e:
        print(f"Erro na conexão/extração: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Executa o script
if __name__ == "__main__":
    popular_itens_gerais(100)