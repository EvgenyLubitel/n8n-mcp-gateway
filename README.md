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

```mermaid
flowchart LR
    A[AI-агент<br/>Claude/Cursor] --> B[MCP-клиент]
    B --> C[MCP-сервер<br/>Python + FastAPI]
    C --> D[n8n REST API]
    D --> E[Воркфлоу n8n]
    C --> F[AITUNNEL<br/>GPT-4]


Invoke-RestMethod -Uri "https://mcp-evgenylubitel.amvera.io/health"




