# Beget VPS Kazakhstan Monitor

Мониторинг появления сервера в Казахстане (kz1) на [beget.com/ru/vps](https://beget.com/ru/vps).

Проверяет раз в час через GitHub Actions. Когда `kz1` станет доступен — отправляет уведомление в Telegram.

## Настройка

1. Добавь секреты в Settings → Secrets and variables → Actions:
   - `TELEGRAM_BOT_TOKEN` — токен бота из @BotFather
   - `TELEGRAM_CHAT_ID` — твой chat ID (см. ниже)

2. Workflow запускается автоматически каждый час.

3. Ручной запуск: Actions → "Beget KZ Monitor" → Run workflow.

4. После покупки сервера: Actions → "Beget KZ Monitor" → ⋯ → Disable workflow.

## Как получить TELEGRAM_CHAT_ID

1. Напиши `/start` боту @project_kk_bot
2. Открой в браузере: `https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/getUpdates`
3. Найди `"chat":{"id": 123456789}` — это твой chat ID
