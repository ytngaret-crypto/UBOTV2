# UBot — Railway Ready

## Required Railway Variables
- `API_ID`
- `API_HASH`
- `SESSION_STRING`
- `OWNER_ID`
- `GEMINI_API_KEY` (untuk AI/Translate/Text Generator)
- `GEMINI_MODEL` (opsional, default `gemini-2.5-flash`)
- `TMDB_API_KEY` (opsional, untuk Movie)
- `OCR_API_KEY` (opsional, untuk OCR)
- `BOT_NAME` (opsional)

## Menu
`.menu` membuka menu utama dengan kategori inline. Setiap kategori berisi fitur UBot.

## Commands utama
`.ban`, `.unban`, `.mute`, `.unmute`
`.autoreply`, `.delreply`, `.listreply`
`.antispam on/off`
`.ai`, `.translate`, `.textgen`, `.ocr`
`.song`, `.movie`
`.game`, `.score`, `.quiz`, `.random`
`.texttools`, `.qr`
`.pay`, `.setpay`, `.setqris`
`.addtarget`, `.deltarget`, `.targets`, `.jashare`
`.settings`, `.set`, `.on`, `.off`
`.setadmin`, `.allow`, `.deny`

AI memakai `GEMINI_API_KEY`; tidak ada API key yang ditulis di source code.
