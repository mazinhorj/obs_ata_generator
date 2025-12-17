# 🏫 Gerador de Observações Automatizado para ATAS de Resultados Finais (Duque de Caxias/RJ)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

Aplicação desenvolvida para automatizar e padronizar a geração de observações nos **Resultados Finais (ATAS)** das escolas da **Rede Municipal de Duque de Caxias**.

A ferramenta processa o arquivo "Livro de Matrícula" (XLSX), aplica regras de negócio específicas (como Progressão Parcial para turmas específicas) e gera um PDF formatado pronto para impressão.

---

## ✨ Funcionalidades

* **Processamento de Excel:** Leitura inteligente do arquivo exportado pelo sistema *e-duque* (cabeçalho na linha 9).
* **Regras de Negócio Automáticas:**
    * Detecção automática de turmas elegíveis para **Progressão Parcial (PP)** (apenas turmas 601 a 999).
    * Bloqueio de duplicidade na escolha de disciplinas de PP.
    * Renumeração dinâmica do menu de opções.
* **Tipos de Observação Suportados:**
    1.  Retenção por frequência (ano anterior/atual).
    2.  Progressão Parcial (Notas e Disciplinas).
    3.  AEE (Atendimento Educacional Especializado).
    4.  Classificação e Reclassificação (com data do ato).
* **Multi-usuário & Privacidade:**
    * Sistema *Stateless* (sem banco de dados físico).
    * Cada usuário tem sua própria sessão e fila de impressão.
    * Dados são apagados automaticamente ao fechar o navegador/atualizar a página.
* **Geração de PDF:** Arquivo final limpo e padronizado usando `fpdf2`.

---

## 📂 Estrutura do Arquivo Excel

Para que o sistema funcione corretamente, o arquivo `.xlsx` deve seguir o padrão de exportação:

* **Cabeçalho:** Linha 9.
* **Dados:** A partir da linha 10.
* **Coluna E:** Turma.
* **Coluna G:** Nome do Aluno.
* **Célula B4:** Nome da Escola (opcional, para cabeçalho).

---

## 🚀 Como Rodar

### Opção 1: Via Docker (Recomendado)

Se você tem o Docker instalado, basta rodar:

```bash
# 1. Construir a imagem
docker build -t ata-generator .
```

# 2. Rodar o container
```bash
docker run -p 8501:8501 ata-generator
Acesse em seu navegador: http://localhost:8501
```

### Opção 2: Rodando Localmente (Python)

Certifique-se de ter o Python 3.10+ instalado.

1. Clone este repositório.

2. Instale as dependências:

```Bash

pip install streamlit pandas openpyxl fpdf2
```
3. Execute a aplicação:

```Bash
streamlit run app.py
```
### Opção 3: Compartilhando via Ngrok
Para testar com colegas remotamente:

1. Inicie a aplicação (via Docker ou Local).

2. Em outro terminal, inicie o ngrok:

```Bash
ngrok http 8501
```
3. Compartilhe o link gerado (ex: https://xxxx.ngrok-free.app).

## 🛠️ Tecnologias Utilizadas
> Streamlit: Interface web interativa e rápida.

> Pandas: Manipulação e limpeza de dados do Excel.

> FPDF2: Geração de relatórios em PDF.

> Docker: Containerização para fácil deploy.

## 🎨 Personalização
O arquivo style.css contém as diretrizes visuais, incluindo o rodapé fixo e ajustes de layout. O arquivo .streamlit/config.toml define as cores institucionais (Azul e Cinza).

## 👨‍💻 Autor
Desenvolvido com carinho por **MazinhoBigDaddy** 📅 2025

_Este projeto é de uso livre para fins educacionais e administrativos._
