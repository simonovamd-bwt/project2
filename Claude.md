# Claude.md — Pre-legal Manifesto

Цей файл — "закон" проекту. Будь-яка робота (людини чи агента) звіряється з ним. Якщо код і цей файл розходяться — файл оновлюється в тому ж PR, що і код.

## 1. Огляд проекту

**Pre-legal** — SaaS-платформа для генерації юридичних угод на основі шаблонів.
Користувач обирає тип угоди → заповнює параметри → отримує згенерований юридичний документ (draft-рівень, не заміна юриста).

- **Бекенд:** FastAPI (Python), проект під `uv`
- **Фронтенд:** Next.js (App Router)
- **База даних:** SQLite (файлова, для v1; шлях до Postgres лишаємо відкритим на майбутнє, але не реалізуємо завчасно)
- **Розгортання:** Docker, єдиний образ (`backend/Dockerfile`, multistage: Next.js static export → FastAPI віддає його як static files), `docker-compose.yml` піднімає один сервіс `app` на порту 8000

## 2. Технічний дизайн (v1 — фундамент)

### 2.1 Структура репозиторію

```
/
├── Claude.md              # цей файл
├── .env                   # секрети (у git не комітиться)
├── .env.example           # шаблон секретів
├── docker-compose.yml
├── backend/
│   ├── pyproject.toml     # uv-проект
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py        # entrypoint FastAPI
│   │   ├── api/           # роути
│   │   ├── core/          # конфіг, налаштування, security
│   │   ├── models/        # ORM-моделі (SQLAlchemy)
│   │   ├── schemas/       # Pydantic-схеми
│   │   ├── services/      # бізнес-логіка (генерація угод, LLM-виклики)
│   │   └── db/            # сесії, підключення до SQLite
│   └── tests/
│       ├── unit/
│       └── integration/
└── frontend/
    ├── package.json      # Next.js, output: "export" у next.config.mjs
    ├── app/
    ├── components/
    ├── lib/
    └── public/
```

Немає окремого `frontend/Dockerfile` — фронтенд збирається як перший стейдж
`backend/Dockerfile` (`next build` → статичні файли в `frontend/out/`), а
FastAPI сам віддає їх (`app/main.py::_mount_frontend`, SPA-fallback на
`index.html` для будь-якого шляху, що не починається з `api/`).

### 2.2 Стандарти коду

- **Python:** типізація обов'язкова (type hints), Pydantic для валідації I/O, PEP 8. Залежності — тільки через `uv` (`pyproject.toml`, `uv.lock`).
- **TypeScript/Next.js:** строгий `tsconfig` (`strict: true`), без `any` без явного обґрунтування.
- **Комміти:** Conventional Commits (`feat:`, `fix:`, `chore:`, `test:` тощо).
- **Секрети:** ніколи не хардкодяться, тільки через `.env` / оточення. `.env` в `.gitignore`.
- Без передчасних абстракцій: не будуємо шар під гіпотетичне майбутнє (напр. Postgres-міграцію) поки не буде реальної потреби.

### 2.3 LLM-виклики та навички (skills)

**AI design.** Коли пишеш код, що робить виклики до LLM, використовуй навичку
`cerebras` (`.claude/skills/cerebras/skill.md`): виклик через **LiteLLM →
OpenRouter → Cerebras** як inference-провайдер, модель
`openai/gpt-oss-120b`. Один **non-streaming** виклик зі **structured output**,
щоб одночасно отримати текст відповіді для чату та екстраговані поля для
документа (Cerebras достатньо швидкий, тож стрімінг не потрібен).
Ключ: `OPENROUTER_API_KEY` у `.env`.

**Каталог документів.** Доступні типи документів описані у `catalog.json` в
корені проекту (id, назва, опис, поля). Асистент обирає тип і збирає його поля
через діалог. Вміст каталогу:

@catalog.json

**Додаткова навичка.** `.claude/skills/legal-template-drafting/skill.md` —
робота над самими шаблонами угод (структура пунктів, плейсхолдери); може
використовувати стандартний Anthropic API (`ANTHROPIC_API_KEY`), опційно.

> **Стан у v1:** реальні LLM-виклики вимкнені (немає ключа) — чат працює на
> детермінованому моку `services/chat.py`, форма відповіді якого вже дзеркалить
> structured-output контракт скіла `cerebras`, тож перехід на живу модель не
> потребує змін API. Див. розділ «ШІ чат-інтерфейс — мок-реалізація».

## 3. Робочий процес (обов'язковий для кожної фічі)

1. **GitHub Issue спочатку.** Перед кодом — прочитати відповідний issue через `gh issue view <номер> --repo simonovamd-bwt/project2`. Якщо issue не вказано або недоступний — це блокер, і про це треба сказати прямо, а не вигадувати вміст завдання.
2. **Технічний дизайн перед кодом.** Для кожної нетривіальної фічі — короткий опис підходу, узгодження з людиною, і тільки потім реалізація.
3. **Тести обов'язкові.** Unit-тести (`backend/tests/unit`) + інтеграційні (`backend/tests/integration`) для кожної нової фічі. Без тестів — фіча не вважається завершеною.
4. **Pull Request.** Після реалізації — PR у GitHub з описом, що змінилось і чому, з посиланням на issue (`Closes #<номер>`).
5. **Гігієна після merge.** Одразу після мержу PR — закрити issue (якщо не закрився автоматично) і оновити секцію "Статус проекту" нижче в цьому файлі, щоб не втрачати контекст між сесіями.

## 4. Статус проекту

> Оновлюється після кожного змердженого PR.

**🎉 Проєкт завершено (2026-07-10).** Усі 10 GitHub Issues закрито, відкритих PR немає, **67/67 тестів зелені**. Беклог порожній.

| Дата | Issue | Що зроблено | PR |
|---|---|---|---|
| 2026-07-09 | — | Створено фундамент репозиторію: структура папок, Claude.md, .env.example, навичка legal-template-drafting | — (не мерджено, локальна ініціалізація) |
| 2026-07-09 | #3 | Авторизація: bcrypt + серверні session-токени в httpOnly cookie (register/login/logout/me). Попутно виправлено баг подвоєння шляху в `DATABASE_URL` | #11 |
| 2026-07-09 | #4 | Історія документів: моделі/схеми + `/api/documents` (list/create/get), ізоляція між юзерами, 404 (не 403) на чужий документ, сортування newest-first | #12 |
| 2026-07-09 | #5 | Єдиний Docker-контейнер: Next.js static export, FastAPI віддає його зі SPA-fallback; multistage `Dockerfile`, `docker-compose.yml` згорнуто до одного сервісу `app` | #13, #14 |
| 2026-07-10 | #9 | Адаптивний DB-engine: `db/session.py::_make_engine` обирає connect-args за URL (in-memory SQLite → `StaticPool`, файлова → `check_same_thread=False`, інша БД → `pool_pre_ping`); тести переведено на `sqlite://` in-memory | #15 |
| 2026-07-10 | #6 | Розширено backend-тести: +16 (auth/deps, documents, security), реальні прогалини; мутаційна перевірка `.strip()`; 50/50 зелені | #16 |
| 2026-07-10 | #7, #10 | Юридичний дисклеймер (банер «Draft only… subject to legal review» + футер) і dev-скрипти `scripts/` (dev/start/stop/test) | #17 |
| 2026-07-10 | #8 | SaaS UI polish: дизайн-токени (`:root`), градієнт/тіні, брендований header, auth-екран (Sign In/Up), картки історії; акцент королівський синій #2563eb | #18 |
| 2026-07-10 | #1 | Базова інфраструктура (PL4): інфраструктурні критерії виконано/перевиконано (auth — реальний замість placeholder). Статична NDA-форма свідомо мігрувала у #2 (чат) + #8 (UI) — закрито з обґрунтуванням | — (закрито коментарем) |
| 2026-07-10 | #2 | ШІ чат-інтерфейс на **моках** (без LLM): `services/chat.py` — детермінований діалог (4 запитання) + structured output; `POST /api/chat` (public, stateless); фронтенд `ChatInterface` з live-preview і Download PDF (`window.print`) | #19 |

### ШІ чат-інтерфейс — мок-реалізація (#2)

За рішенням власника проекту (немає `ANTHROPIC_API_KEY`, свідома відмова від платних зовнішніх API на цьому етапі) чат реалізовано **без жодного LLM-виклику**:

- `backend/app/services/chat.py` — чиста, детермінована логіка: 4 захардкоджені запитання по черзі (NDA), білдер live-preview markdown, structured-output форма (`ChatTurn`). Коли всі поля зібрано → `complete=True` + готовий документ.
- `backend/app/api/chat.py` — `POST /api/chat`, **публічний** (freemium: чат без логіну; збереження — через авторизований `/api/documents`), **stateless** (фронтенд щоразу шле повний map відповідей).
- Форма відповіді дзеркалить те, що повернув би реальний non-streaming structured-output модель, тож заміна мока на живий LLM згодом не потребує змін контракту.
- Фронтенд: `ChatInterface` (chat log + live preview), `lib/markdown.ts` (мінімальний md→html із екрануванням), Download PDF через `window.print()` (`@media print` друкує лише прев'ю).

### Локальний запуск (скрипти)

Стандартний спосіб запуску — тонкі обгортки в `scripts/` (усі: `set -euo pipefail`, `cd` у корінь):

- `scripts/dev.sh` — локальний backend з auto-reload (`uv run uvicorn --reload`), без Docker/Postgres.
- `scripts/start.sh` — `docker compose up --build` (єдиний контейнер, порт 8000).
- `scripts/stop.sh` — `docker compose down`.
- `scripts/test.sh` — `uv sync --extra dev && uv run pytest` (in-memory SQLite, без Docker).

### Стан оточення та відомі обмеження (оновлено 2026-07-10)

- ✅ **uv встановлено** (`~/.local/bin`), `uv sync --extra dev` та `uv run pytest` виконано успішно: **67/67 тести проходять** (auth, documents, chat, chat-service, frontend-mount, security, health, app-boot, db-engine).
- ✅ **Docker перевірено** — `docker compose build` + `docker compose up` пройдено локально. Єдиний контейнер `project2-app` віддає і API, і фронтенд на порту 8000: перевірено `/health`, `/` (Next.js index), `/_next/static/*`, SPA-fallback, а також повний auth+documents флоу (register → cookie → /me → create → list). `next build` докачує платформенний SWC-бінарник під час збірки, тож у мережево-ізольованому оточенні build потребує проксі (`--build-arg HTTP_PROXY=...`); у звичайній мережі build проходить без додаткових аргументів.
- ✅ **Репозиторій підключено до GitHub** — `simonovamd-bwt/project2`, `gh` авторизовано. Усі задачі відстежувались через GitHub Issues (заміна Jira за рекомендацією курсу); усі 10 issues закрито.

#### Свідомі обмеження v1 (не баги — зафіксовані рішення)

- **Немає реальних LLM-викликів.** `ANTHROPIC_API_KEY` порожній у `.env` за рішенням власника (відмова від платних зовнішніх API на цьому етапі). Чат (#2) працює на детермінованому моку `services/chat.py`. Навичка `legal-template-drafting` не робитиме реальних викликів, поки ключ не вставлять вручну. Контракт `ChatResponse` вже у формі structured-output, тож заміна мока на живий LLM не потребує змін API.
- **Фронтенд auth-UI та історія документів — статичні (на мок-даних).** Бекенд-ендпоінти (`/api/auth`, `/api/documents`) реальні й покриті тестами, але UI ще не підключено до них наживо — це наступний крок розвитку, не поточний скоуп.
- **PDF-експорт через `window.print()`**, а не серверна генерація — свідомо простий zero-dep підхід для v1.

Це не production-ready система, а завершений навчальний прототип (v1). Наведені вище пункти — відомі напрями розвитку, а не незакриті TODO.
