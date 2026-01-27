---

name: novafon\_api

description: Novafon Data API и Call API интеграция и примеры запросов — работа с данными, отчётами и управлением звонками через JSON-RPC.

metadata: {"clawdbot":{"emoji":"📞","always":true,"requires":{"bins":\["curl","jq"]}}}

---



\# Novafon API 📞



Novafon предоставляет два JSON-RPC API — \*\*Data API\*\* для доступа к данным и отчётам, и \*\*Call API\*\* для создания и управления звонками. :contentReference\[oaicite:1]{index=1}



\## 🔑 Настройка



\### 📦 Переменные окружения



| Variable | Description | Required |

|----------|-------------|----------|

| `NOVAFON\_DATA\_API\_URL` | Base URL Data API (обычно dataapi-jsonrpc.novofon.ru/v2.0) | Yes |

| `NOVAFON\_CALL\_API\_URL` | Base URL Call API (обычно callapi-jsonrpc.novofon.ru/v4.0) | Yes |

| `NOVAFON\_API\_TOKEN` | Доступный \*\*access\_token\*\* (ключ API или сессия) | Yes |



---



\## 🧠 Общие сведения



📌 Обе API используют \*\*JSON-RPC 2.0\*\* (метод POST, тело запроса JSON). :contentReference\[oaicite:2]{index=2}  

📌 Все параметры и поля — \*\*snake\_case\*\*. :contentReference\[oaicite:3]{index=3}  

📌 Требуется добавление IP в белый список в админ-панели. :contentReference\[oaicite:4]{index=4}



---



\## 🗂 Data API — работа с данными и отчётами



\### 📌 Основные принципы



\- Базовый URL: `${NOVAFON\_DATA\_API\_URL}` → JSON-RPC запросы. :contentReference\[oaicite:5]{index=5}  

\- Обработка ошибок подробно описана (коды, мнемоники). :contentReference\[oaicite:6]{index=6}  

\- Поддерживаются фильтрация, сортировка и пагинация. :contentReference\[oaicite:7]{index=7}



---



\### 📊 📈 📉 Базовые запросы



```bash

\# Пример базового запроса Data API

curl -s "${NOVAFON\_DATA\_API\_URL}" \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{

&nbsp;   "jsonrpc":"2.0",

&nbsp;   "id":"req1",

&nbsp;   "method":"get.account",

&nbsp;   "params":{

&nbsp;     "access\_token":"'"${NOVAFON\_API\_TOKEN}"'"

&nbsp;   }

&nbsp; }' | jq '.'



