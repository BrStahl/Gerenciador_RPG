# Análise do Sistema RPG e Sugestões de Melhoria

## 1. Visão Geral (Opinião)

O sistema apresenta uma boa base funcional para um gerenciador de personagens de RPG. A integração de uma interface gráfica completa (Tkinter) com um banco de dados relacional (MySQL) é um ponto forte, permitindo persistência de dados e funcionalidades complexas como gerenciamento de inventário, magias e bestiário.

O uso da API `open5e` (via scripts na pasta `API/`) para popular o banco de dados é uma excelente iniciativa para enriquecer o conteúdo do sistema sem entrada manual excessiva.

No entanto, o projeto sofre de problemas comuns em aplicações que crescem organicamente: código monolítico, mistura de responsabilidades (UI e lógica de banco de dados juntas) e falhas críticas de segurança que precisam ser endereçadas.

## 2. Pontos Críticos (Segurança e Estabilidade)

### 🔴 Vulnerabilidade a SQL Injection
O código faz uso extensivo de f-strings para construir consultas SQL. Isso permite que um usuário mal-intencionado (ou mesmo um erro de digitação com caracteres especiais) corrompa o banco de dados.

**Exemplo vulnerável (`main.py`):**
```python
query = f"SELECT nome_item,quantidade FROM Itens_Iniciais WHERE id_raca = '{id_raca}'"
```

**Correção sugerida:**
Sempre usar queries parametrizadas fornecidas pelo driver do MySQL.
```python
query = "SELECT nome_item,quantidade FROM Itens_Iniciais WHERE id_raca = %s"
cursor.execute(query, (id_raca,))
```

### 🔴 Credenciais Hardcoded
As credenciais do banco de dados (`root`, senha vazia) estão fixas no arquivo `database.py` e replicadas nos scripts da pasta `API/`. Isso dificulta a configuração em diferentes ambientes e expõe dados sensíveis se o código for compartilhado.

**Sugestão:** Usar variáveis de ambiente (arquivo `.env`) e a biblioteca `python-dotenv`.

### ⚠️ Tratamento de Erros
Muitas operações de banco de dados capturam exceções genéricas (`except Exception as e`) e apenas imprimem o erro ou mostram um popup, mas a conexão nem sempre é fechada corretamente em caso de falha (embora existam blocos `finally` em alguns lugares, não é consistente).

## 3. Arquitetura e Código

### "God Class" / Monólito (`main.py`)
O arquivo `main.py` tem cerca de 1000 linhas e é responsável por:
1.  Definir a interface gráfica (Widgets, Layouts).
2.  Gerenciar eventos de clique.
3.  Conectar ao banco de dados.
4.  Executar lógica de negócio (cálculo de modificadores, slots de magia).

Isso torna a manutenção difícil. Se você quiser mudar a interface para Web no futuro, terá que reescrever tudo.

### Código Morto / Duplicado (`Personagem.py`)
Existe um arquivo `Personagem.py` com uma classe `Personagem` que parece implementar lógica de RPG, mas ela é **ignorada** pelo `main.py`, que reimplementa a lógica (como cálculo de HP e carga) diretamente dentro das funções de UI e queries SQL.

### Gerenciamento de Estado Global
O `main.py` depende de variáveis globais (`Nome`, `combo_racas`, etc.) para funcionar. Isso torna o código frágil e difícil de testar.

## 4. Roteiro de Sugestões (Roadmap)

### Curto Prazo (Correções Rápidas)
1.  **Segurança:** Substituir todas as f-strings em queries SQL por parâmetros (`%s`).
2.  **Configuração:** Criar um arquivo `config.py` ou `.env` para as credenciais do banco.
3.  **Limpeza:** Centralizar a conexão de banco apenas em `database.py` (os scripts da API duplicam essa lógica).

### Médio Prazo (Refatoração)
1.  **Padrão MVC (Model-View-Controller):**
    *   **Model:** Classes que representam os dados (`Personagem`, `Item`, `Magia`) e a lógica de negócio (calcular modificador, validar peso). O arquivo `Personagem.py` deve ser ressuscitado para isso.
    *   **DAO (Data Access Object):** Uma camada separada apenas para SQL. Ex: `PersonagemDAO.salvar(personagem)`. O `main.py` nunca deve ter `cursor.execute`.
    *   **View:** O código Tkinter.
    *   **Controller:** Conecta a View ao Model/DAO.
2.  **Padronização:** Adotar PEP8 (nomes de variáveis em `snake_case`, classes em `CamelCase`). Atualmente há uma mistura (`Nome`, `pts_For`, `combo_racas`).

### Longo Prazo (Evolução)
1.  **ORM (Object-Relational Mapping):** Usar **SQLAlchemy** ou **Peewee**. Isso elimina a necessidade de escrever SQL manualmente e protege automaticamente contra injeção de SQL.
2.  **Testes Automatizados:** Com a lógica separada da interface, torna-se possível criar testes unitários para garantir que o cálculo de dano ou peso esteja correto.

## 5. Exemplo de Melhoria (DAO Pattern)

Em vez de SQL espalhado na UI:

**`dao/personagem_dao.py`**
```python
def buscar_por_id(id_personagem):
    conn = db.conexao()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Personagens WHERE id_personagem = %s"
    cursor.execute(query, (id_personagem,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado
```

**`main.py`**
```python
# A interface apenas pede os dados, não sabe o que é SQL
dados = personagem_dao.buscar_por_id(1)
lbl_nome.config(text=dados['nome'])
```
