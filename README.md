# Gestor de Personagens de RPG

Bem-vindo ao **Gestor de Personagens de RPG**, uma aplicação desktop em Python (Tkinter) para criação e gerenciamento de fichas de personagens, magias, inventário e bestiário, integrado com banco de dados MySQL.

## 📋 Pré-requisitos

*   Python 3.x
*   Servidor MySQL (local ou remoto)

## 🚀 Instalação e Configuração (Ajustes de Curto Prazo)

Siga os passos abaixo para configurar o ambiente. Estas instruções refletem as melhorias recentes de segurança e configuração.

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure o Banco de Dados:**
    *   Certifique-se de ter um banco de dados MySQL criado (ex: `RPG`).
    *   Renomeie o arquivo `.env.example` para `.env` na raiz do projeto.
    *   Edite o arquivo `.env` com suas credenciais:
        ```ini
        DB_HOST=localhost
        DB_USER=seu_usuario
        DB_PASSWORD=sua_senha
        DB_NAME=RPG
        ```

3.  **Execute a aplicação:**
    ```bash
    python main.py
    ```

## 🛠️ Roadmap de Desenvolvimento (Ajustes de Médio Prazo)

Com base na análise técnica do sistema (`REVIEW.md`), os seguintes ajustes estão planejados para melhorar a arquitetura e manutenção do código:

### 1. Refatoração para Padrão MVC (Model-View-Controller)
O código atual (`main.py`) concentra lógica de interface e banco de dados. O objetivo é separar responsabilidades:
*   **Model:** Ressuscitar e utilizar `Personagem.py` para lógica de negócios (cálculos de HP, carga, etc).
*   **DAO (Data Access Object):** Mover todas as queries SQL de `main.py` para uma camada de acesso a dados isolada (ex: `dao/personagem_dao.py`).
*   **View:** Manter `main.py` focado apenas na construção da interface gráfica Tkinter.

### 2. Padronização de Código (PEP8)
*   Renomear variáveis e funções para seguir o padrão `snake_case` (ex: de `Nome_per` para `nome_personagem`).
*   Organizar importações e espaçamento.

### 3. Tratamento de Erros Robusto
*   Garantir que conexões com o banco sejam fechadas mesmo em caso de erro (uso de `try/finally` ou context managers em toda a camada DAO).

## 📄 Estrutura de Arquivos Atual

*   `main.py`: Arquivo principal da aplicação (Interface Gráfica e Lógica).
*   `database.py`: Gerenciamento de conexão com o banco de dados.
*   `API/`: Scripts para popular o banco de dados com monstros via API externa.
*   `requirements.txt`: Lista de bibliotecas Python necessárias.
*   `.env`: Arquivo de configuração (não comitado).
*   `REVIEW.md`: Relatório detalhado da análise do sistema.
