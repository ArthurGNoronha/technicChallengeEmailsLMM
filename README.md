# Analisador de Emails com IA

Aplicação full-stack (Flask + Frontend estático) para:
- Classificar e-mails em Produtivo ou Improdutivo.
- Gerar resumo, pontos-chave e nível de urgência (1–5).
- Armazenar histórico (SQLite).
- Sugerir respostas com diferentes tons (Profissional, Amigável, Direto).
- Extrair texto de anexos `.pdf` e `.txt`.
- Gerar múltiplas respostas usando Google Gemini.

---

## Arquitetura

Backend (Flask):
- Rotas em [backend/routes.py](backend/routes.py)
- App principal em [backend/app.py](backend/app.py)
- Integração IA: [`utils.AI_API.analyzeEmail`](backend/utils/AI_API.py), [`utils.AI_API.generateReply`](backend/utils/AI_API.py)
- NLP / pré-processamento: [`utils.nlp.preprocessText`](backend/utils/nlp.py)
- Extração de arquivos: [`utils.extractor.extractText`](backend/utils/extractor.py), [`utils.extractor.extractPdf`](backend/utils/extractor.py), [`utils.extractor.extractTxt`](backend/utils/extractor.py)
- Banco de dados SQLite:  
  - Inicialização: [`utils.database.initDB`](backend/utils/database.py)  
  - Inserção: [`utils.database.addHistoryEntry`](backend/utils/database.py)  
  - Listagem: [`utils.database.getHistory`](backend/utils/database.py)  
  - Remoção: [`utils.database.deleteHistoryEntry`](backend/utils/database.py)  
  - Atualização parcial: [`utils.database.patchHistoryEntry`](backend/utils/database.py)

Frontend (HTML/CSS/JS):
- Estrutura: [frontend/index.html](frontend/index.html)
- Lógica principal: [frontend/assets/js/scripts.js](frontend/assets/js/scripts.js)
- ToastAlert: [frontend/assets/js/toastAlert.js](frontend/assets/js/toastAlert.js)
- Estilos: [frontend/assets/css/styles.css](frontend/assets/css/styles.css), [frontend/assets/css/toastAlert.css](frontend/assets/css/toastAlert.css)

Utilidades:
- Download NLTK: [backend/utils/download_nltk.py](backend/utils/download_nltk.py)
- Verificação de modelos Gemini: [backend/checkModels.py](backend/checkModels.py)

Configuração / Deploy:
- Dependências: [requirements.txt](requirements.txt)
- Runtime: [runtime.txt](runtime.txt)
- Procfile (Heroku): [Procfile](Procfile)
- Exemplo de env: [.env.example](.env.example)
- Setup package: [setup.py](setup.py)
- Ignore: [.gitignore](.gitignore)

---

## Stack

| Camada      | Tecnologia |
|-------------|------------|
| Backend     | Flask (Python 3.11) |
| IA          | Google Gemini (API Generative AI) |
| NLP         | NLTK (tokenização + stopwords pt-BR) |
| Banco       | SQLite (arquivo `history.db`) |
| Frontend    | HTML + CSS + JS Vanilla |
| Deploy      | Heroku + Gunicorn + Procfile |

---

## Pré-requisitos

1. Python 3.11 (ver [runtime.txt](runtime.txt))
2. Chave válida Gemini API (`GEMINI_API_KEY`) disponível em: [https://aistudio.google.com/app/api-keys](https://aistudio.google.com/app/api-keys)
3. Dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Criar `.env`:
   ```bash
   cp .env.example .env
   # Edite e inclua sua GEMINI_API_KEY
   ```

---

## Instalação & Execução Local

```bash
# Pode-se utilizar uma venv.
python -m venv venv
venv\Scripts\activate
```

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Baixar NLTK (primeira vez)
python -m backend.utils.download_nltk

# 3. Rodar servidor
python backend/app.py
# Acesse: http://localhost:5000
```

O banco (`history.db`) é criado automaticamente por [`utils.database.initDB`](backend/utils/database.py).

---

## Variáveis de Ambiente

| Nome            | Descrição |
|-----------------|-----------|
| GEMINI_API_KEY  | Chave da API Gemini |

Arquivo de exemplo: [.env.example](.env.example)

---

## Fluxo de Funcionamento

1. Usuário insere texto e/ou anexo.
2. Backend monta conteúdo combinado (corpo + anexo) em [`routes.getContent`](backend/routes.py).
3. Texto é pré-processado por [`utils.nlp.preprocessText`](backend/utils/nlp.py).
4. IA analisa via [`utils.AI_API.analyzeEmail`](backend/utils/AI_API.py) e retorna JSON.
5. Registro é salvo no histórico (`SQLite`).
6. Respostas são geradas sob demanda via [`utils.AI_API.generateReply`](backend/utils/AI_API.py).
7. Frontend exibe histórico com edição inline (classificação / urgência).

---

## Endpoints REST

Rotas principais da API:

- POST /api/analyze  
  Analisa o conteúdo do e-mail (texto e opcionalmente anexo) e retorna classificação, resumo, pontos-chave e nível de urgência.

- POST /api/reply  
  Gera múltiplas sugestões de resposta com base no conteúdo analisado, tipo (classificação) e tom desejado.

- GET /api/history  
  Retorna a lista de registros do histórico (análises anteriores).

- DELETE /api/history/{id}  
  Remove um item específico do histórico.

- PATCH /api/history/{id}  
  Atualiza parcialmente um registro (campos: classification, urgency).

- GET /  
  Servido para a interface web (frontend).

---

## Frontend

Abrir interface em `/` (servido por [backend/app.py](backend/app.py)).  
Funcionalidades:
- Upload `.pdf` / `.txt` (extração: [`utils.extractor.extractText`](backend/utils/extractor.py))
- Histórico
- Prioridade e classificações editáveis.
- Geração de múltiplas respostas automâticas
- Copiar para clipboard / abrir Gmail / Outlook (ver [frontend/assets/js/scripts.js](frontend/assets/js/scripts.js))

---

## NLP

Pré-processamento:
- Tokenização + remoção de stopwords (pt-BR) em [`utils.nlp.preprocessText`](backend/utils/nlp.py)

---

## IA (Gemini)

Modelo configurado em [`utils.AI_API.model`](backend/utils/AI_API.py).  
Script auxiliar de listagem: [backend/checkModels.py](backend/checkModels.py)

Fallback seguro: respostas padrão caso JSON não seja parseável.

---

## Deploy (Heroku)

Procfile: [Procfile](Procfile)  
Executa:
1. Download NLTK: [`backend/utils/download_nltk.py`](backend/utils/download_nltk.py)
2. Gunicorn: `gunicorn --pythonpath backend app:app`

Ajustar variável `PORT` se necessário.

---

## Scripts Úteis

```bash
# Ver modelos Gemini disponíveis para sua chave API
python backend/checkModels.py

# Baixar NLTK
python -m backend.utils.download_nltk
```

---

## Estrutura

```
backend/
  app.py - Servidor da aplicação
  routes.py - Rotas disponíveis da API
  utils/
    AI_API.py - API para comunicação com a IA
    database.py - Arquivo para a criação do SQLite
    extractor.py - Extrator de texto em arquivos PDF e TXT
    nlp.py - Configurações de NLP
    download_nltk.py - Arquivo para o donwload de NLTK
frontend/
  index.html
  assets/css/*.css
  assets/js/*.js
```

---

## Dsenvolvido por Arthur Noronha.


---