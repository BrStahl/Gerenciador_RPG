import pymysql
import cryptography

# Dados da sua imagem do Aiven
config = {
    'host': 'mysql-26f15578-gerenciadorpg.h.aivencloud.com',
    'port': 27709,
    'user': 'avnadmin',
    'password': 'AVNS_fHhJBTLozzp1NCcTNa7', # Olhe na imagem image_3b81ef.png
    'database': 'defaultdb',
    'cursorclass': pymysql.cursors.DictCursor,
    'ssl': {'ssl_mode': 'REQUIRED'} # O Aiven exige SSL
}

try:
    print("Conectando ao Aiven...")
    connection = pymysql.connect(**config)
    
    with connection.cursor() as cursor:
        print("Lendo o arquivo bkp_RPG.sql...")
        with open('bkp_RPG.sql', 'r', encoding='utf-8') as f:
            # Divide o arquivo por ';' para executar comando por comando
            sql_file = f.read()
            commands = sql_file.split(';')
            
        print("Subindo tabelas para a nuvem...")
        for command in commands:
            if command.strip():
                cursor.execute(command)
        
        connection.commit()
        print("✅ SUCESSO! Seu banco de RPG agora está na nuvem do Aiven.")

except Exception as e:
    print(f"❌ Erro ao subir: {e}")

finally:
    if 'connection' in locals():
        connection.close()