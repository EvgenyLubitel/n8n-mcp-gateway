# 🤖 n8n MCP Gateway

MCP-сервер на Python + FastAPI + AITUNNEL для управления n8n через AI-оркестратор.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-teal)](https://fastapi.tiangolo.com)
[![n8n](https://img.shields.io/badge/n8n-2.6.3-blue)](https://n8n.io)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

---

## 📌 О проекте

**n8n MCP Gateway** — это MCP-совместимый сервер, который позволяет AI-агентам (Claude, Cursor, Goose) управлять n8n-воркфлоу через естественный язык.

**Что умеет:**
- 📋 Просмотр всех воркфлоу
- ▶️ Запуск воркфлоу с данными
- 🔄 Активация/деактивация воркфлоу
- 📊 История выполнений
- 🧠 AI-оркестратор через AITUNNEL

---

## 🏗️ Архитектура

**Компоненты:**

| Компонент | Технология |
|-----------|------------|
| MCP-сервер | Python 3.11 + FastAPI |
| AI-оркестратор | AITUNNEL (OpenAI) |
| Оркестрация | n8n 2.6.3 |
| Деплой | Amvera Cloud |

---

## 🚀 Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/EvgenyLubitel/n8n-mcp-gateway.git
cd n8n-mcp-gateway
```

### 2. Настройка переменных

Скопируй `.env.example` в `.env` и заполни:

```env
AITUNNEL_API_KEY=sk-aitunnel-...
AITUNNEL_BASE_URL=https://api.aitunnel.ru/v1

N8N_BASE_URL=https://your-n8n.amvera.io
N8N_API_KEY=ваш-ключ-из-n8n
N8N_WRITE_MODE=false
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Запуск

```bash
python mcp_server.py
```

---

## 🔌 API Эндпоинты

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/` | GET | Информация о сервере |
| `/health` | GET | Проверка здоровья n8n |
| `/ask` | POST | Запрос к AI-оркестратору |
| `/mcp` | POST | MCP-совместимый эндпоинт |
| `/list-tools` | GET | Список всех инструментов |

---

## 🧪 Тестирование

### Проверка здоровья

```powershell
Invoke-RestMethod -Uri "https://mcp-evgenylubitel.amvera.io/health"
```

### AI-запрос

```powershell
$body = @{query = "Покажи все мои workflow"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://mcp-evgenylubitel.amvera.io/ask" -Method POST -Body $body -ContentType "application/json"
```

### Прямой запрос к воркфлоу

```powershell
Invoke-RestMethod -Uri "https://langchain-evgenylubitel.amvera.io/webhook/hello-mcp"
```

### Запрос с данными (сумма чисел)

```powershell
$body = @{action = "sum"; data = @{a = 10; b = 20}} | ConvertTo-Json
Invoke-RestMethod -Uri "https://langchain-evgenylubitel.amvera.io/webhook/mcp-demo" -Method POST -Body $body -ContentType "application/json"
```

### Список задач

```powershell
$body = @{action = "tasks"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://langchain-evgenylubitel.amvera.io/webhook/mcp-demo" -Method POST -Body $body -ContentType "application/json"
```

---

## 📁 Структура репозитория

```
n8n-mcp-gateway/
├── README.md
├── mcp_server.py
├── requirements.txt
├── .env.example
├── amvera.yaml
└── screenshots/
    ├── health-check.png
    ├── ai-request.png
    └── workflow-demo.png
```

---

## 🎯 Что показывает этот проект

- ✅ MCP-сервер на Python (FastAPI)
- ✅ AI-оркестратор через AITUNNEL
- ✅ Полный REST-интерфейс к n8n
- ✅ 9 MCP-инструментов для управления n8n
- ✅ Production-ready деплой (Amvera)

---

## 🔗 Ссылки

- **GitHub:** [github.com/EvgenyLubitel/n8n-mcp-gateway](https://github.com/EvgenyLubitel/n8n-mcp-gateway)
- **Демо:** [mcp-evgenylubitel.amvera.io](https://mcp-evgenylubitel.amvera.io)
- **n8n:** [langchain-evgenylubitel.amvera.io](https://langchain-evgenylubitel.amvera.io)

---

## 📄 Лицензия

MIT
