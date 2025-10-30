# 🛡️ Sistema de Seguros - Sprint 4: Persistência Híbrida e Padronização

## 👥 Nomes dos Integrantes e RMs

| Nome | RM |
| :--- | :--- |
| Carlos Bucker | 555812 |
| Alexandre Ferreira | 565626 |
| Filipe Melo | 564571 |
| Luca Tiepolo Schmidt Morete | 560255 |
| Mayara Mota | 563887 |

## 🚀 Visão Geral do Sprint 4

O objetivo deste Sprint foi migrar a persistência de dados para uma arquitetura híbrida robusta, utilizando o **MySQL (AWS RDS)** como núcleo relacional do negócio e o **MongoDB (Atlas)** para log de auditoria e dados semiestruturados.

Também foram implementados testes automatizados e ferramentas de padronização de código (`black` e `ruff`).

## ⚙️ Requisitos e Configuração do Ambiente

Para rodar a aplicação, é necessário configurar as variáveis de ambiente ou garantir que as credenciais estejam hardcoded nos arquivos `database/db_mysql.py` e `database/db_mongo.py`.

### 1. Dependências Python

```bash
pip install -r requirements.txt 
# O requirements.txt deve incluir: mysql-connector-python, pymongo, pytest, pytest-cov, black, ruff