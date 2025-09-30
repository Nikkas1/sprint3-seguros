Sistema de Seguros (Sprint 3)
Nomes dos Integrantes:
Carlos Bucker - RM 555812
Alexandre Ferreira - RM 565626
Filipe Melo - RM 564571
Luca Tiepolo Schmidt Morete - RM 560255
Mayara Mota - RM 563887

O foco desta fase foi transformar o projeto em uma aplicação robusta com banco de dados e ferramentas para análise de negócio.


Implementamos a persistência e relatórios gerenciais:

Dados Guardados (SQLite): Todos os clientes, apólices, sinistros e usuários agora são salvos em um banco de dados SQLite, usando o SQLAlchemy. Com isso, os dados não se perdem.

Migração Automática: Criamos o script src/migrations.py que lê seus arquivos JSON antigos (da Sprint 2) e os carrega automaticamente para o novo banco de dados.

Relatórios Úteis: Adicionamos quatro relatórios gerenciais essenciais:

Soma do Valor Total Segurado por Cliente (apólices ativas).

Contagem de Apólices Ativas por Tipo (Auto, Residencial, Vida).

Status dos Sinistros.

Ranking dos Clientes com mais Apólices Ativas.

Exportação CSV: Todos os relatórios podem ser salvos em arquivos CSV para que você possa analisá-los no Excel ou em outras ferramentas.

Segurança e Confirmação: Agora é obrigatório confirmar o cancelamento de uma apólice, evitando erros.

Preparação do Ambiente
Para rodar, só precisa ter o Python 3.x.

1. Crie seu ambiente virtual
python -m venv venv
source venv/bin/activate  # No Linux/macOS
.\venv\Scripts\activate   # No Windows

2. Instale as bibliotecas
pip install -r requirements.txt

(Lembre-se: Você deve ter um requirements.txt com as dependências, como SQLAlchemy.)

🔄 Passo Crucial: Migrar Seus Dados Antigos
Se você tem dados da Sprint 2 em JSON, siga este passo:

1. Coloque os JSONs no lugar certo
Crie a pasta e coloque os três arquivos JSON lá:

.
└── data/
    └── sprint2/
        ├── clientes.json
        ├── apolices.json
        └── sinistros.json

2. Execute a migração
Isso irá criar o arquivo do banco de dados (seguros.db) e carregar os dados.

python -m src.migrations

Aguarde a mensagem --- Migração Concluída ---.

"Para Entrar no Sistema"
O usuário inicial é sempre:

Usuário :admin

Senha :Sompo123

Perfil: admin

"Para Rodar"
Inicie a aplicação principal :

python -m src.main


Exemplos Rápidos de Uso
O fluxo básico do sistema após o login.

1. Emissão de uma Apólice
O processo exige que o cliente já esteja cadastrado.

Acesse o Menu: Após o login como admin, selecione a opção 2. Apólices.

Selecione o Fluxo: Selecione a opção 1. Emitir nova Apólice.

Insira os Dados: Informe o CPF de um cliente existente, escolha o Tipo de Apólice (e.g., AUTO) e preencha as informações do bem segurado (e.g., valor do veículo, ano).

Confirmação: O sistema exibirá o prêmio calculado e o número da apólice gerada.

2. Registro de um Sinistro
Acesse o Menu: Após o login, selecione a opção 3. Sinistros.

Selecione o Fluxo: Escolha a opção 1. Registrar Sinistro.

Insira os Dados: Digite o Número da Apólice ativa para a qual o sinistro será registrado e informe os detalhes (data, descrição, valor estimado).

Status Inicial: O sinistro será registrado com o status inicial de PENDENTE DE ANÁLISE.

3. Geração de Relatório e Exportação CSV
Acesse o Menu: Após o login, selecione a opção 4. Relatórios.

Selecione o Relatório: Escolha um dos quatro relatórios disponíveis, por exemplo, 4. Ranking de Clientes com Mais Apólices.

Visualização: O resultado será exibido na tela do terminal.

Exportação: O sistema perguntará: Deseja exportar este relatório para CSV? (s/N). Se responder s, o arquivo será salvo na pasta relatorios/.

Arquivo gerado: relatorios/ranking_clientes_[DATA_HORA].csv

Como Usar os Relatórios
Ao escolher um relatório no menu, o sistema mostra a tabela na tela e pergunta se você quer exportar para CSV. Se disser 'sim', o arquivo é salvo na pasta relatorios/.