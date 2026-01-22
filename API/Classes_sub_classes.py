import requests
import mysql.connector
from deep_translator import GoogleTranslator

# Função de tradução já utilizada no seu projeto
def traduzir_rpg(texto):
    if not texto: return ""
    try:
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except:
        return texto

def popular_classes_e_subclasses():
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "rpg"
    }

    url = "https://api.open5e.com/v1/classes/"
    
    try:
        print("Buscando classes na API... Aguarde as traduções.")
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()
        dados_api = resposta.json()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for classe in dados_api['results']:
            # 1. PROCESSAMENTO DA CLASSE PRINCIPAL
            nome_classe_pt = traduzir_rpg(classe['name'])
            
            sql_classe = """
                INSERT INTO Classes 
                (nome_classe, dado_vida, hp_1_nivel, hp_niveis_altos, armadura, 
                 armas, ferramentas, salvaguardas, pericias, 
                 equipamento_inicial, atributo_conjuracao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores_classe = (
                nome_classe_pt,
                classe['hit_dice'],
                traduzir_rpg(classe['hp_at_1st_level']),
                traduzir_rpg(classe['hp_at_higher_levels']),
                traduzir_rpg(classe['prof_armor']),
                traduzir_rpg(classe['prof_weapons']),
                traduzir_rpg(classe['prof_tools']),
                traduzir_rpg(classe['prof_saving_throws']),
                traduzir_rpg(classe['prof_skills']),
                traduzir_rpg(classe['equipment']),
                traduzir_rpg(classe['spellcasting_ability'])
            )
            
            cursor.execute(sql_classe, valores_classe)
            
            # 2. PEGAR O ID DA CLASSE RECÉM INSERIDA
            id_classe_pai = cursor.lastrowid
            
            # 3. PROCESSAMENTO DOS ARQUÉTIPOS (Subclasses)
            arquetipos = classe.get('archetypes', [])
            if arquetipos:
                print(f"-> Traduzindo arquétipos de {nome_classe_pt}...")
                for arq in arquetipos:
                    sql_sub = """
                        INSERT INTO Sub_Classes (id_classe, nome_subclasse, descricao)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_sub, (
                        id_classe_pai,
                        traduzir_rpg(arq['name']),
                        traduzir_rpg(arq['desc'])
                    ))
            
            print(f"Classe {nome_classe_pt} finalizada.")

        conn.commit()
        print("\nSucesso! Classes e Arquétipos populados com vínculo.")

    except Exception as e:
        print(f"Erro no processo: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Executar a carga
popular_classes_e_subclasses()