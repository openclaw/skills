# Apple Mail Moltbot Skill 📧

En Moltbot skill som gör det möjligt att läsa och interagera med Apple Mail via osascript på macOS.

## Funktioner

- ✅ Lista alla mailkonton
- ✅ Lista mailboxar (mappar) för ett specifikt konto
- ✅ Hämta lista över mail från en mailbox med filtrering
- ✅ Läsa det fullständiga innehållet i specifika mail

## Krav

- **macOS** (Apple Mail finns endast på macOS)
- **Python 3.x** (ingår i macOS)
- **Apple Mail** installerat och konfigurerat med minst ett konto
- **Apple Mail måste vara igång** när skripten används

## Installation för Moltbot

1. Klona eller ladda ner denna skill till din Moltbot skills-mapp:
```bash
cd ~/clawd/skills/  # eller din skills-mapp
git clone https://github.com/latisen/apple-mail-moltbot-skill.git apple-mail
```

2. Se till att skripten är körbara:
```bash
chmod +x apple-mail/scripts/*.py
```

3. Starta om Moltbot eller kör "refresh skills" för att ladda den nya skillen.

## Användning

När skillen är installerad kommer Moltbot automatiskt att använda den när du ställer frågor om mail, t.ex.:

- "Lista mina mailkonton"
- "Visa mina senaste mail från INBOX"
- "Vilka mappar finns i mitt Gmail-konto?"
- "Läs mailet med ID 123456"

## Manuell testning

Du kan också testa skripten direkt:

### Lista konton
```bash
python3 scripts/list_accounts.py
```

### Lista mailboxar
```bash
python3 scripts/list_mailboxes.py "iCloud"
```

### Hämta mail från en mailbox
```bash
# Hämta 10 senaste (standard)
python3 scripts/get_messages.py "iCloud" "INBOX"

# Hämta 20 senaste
python3 scripts/get_messages.py "iCloud" "INBOX" --limit 20
```

### Läs ett specifikt mail
```bash
python3 scripts/get_message_content.py "123456"
```

## Struktur

```
apple-mail-moltbot-skill/
├── SKILL.md              # Skill-definition för Moltbot
├── README.md             # Denna fil
└── scripts/              # Körbara Python-skript
    ├── list_accounts.py
    ├── list_mailboxes.py
    ├── get_messages.py
    └── get_message_content.py
```

## Felsökning

**Problem:** "Failed to communicate with Mail app"
- **Lösning:** Starta Apple Mail-appen

**Problem:** "No mailboxes found" eller "Message not found"
- **Lösning:** Kontrollera att konto- och mailbox-namn är korrekt stavade (skiftlägeskänsligt)

**Problem:** Behörighetsfel vid första körningen
- **Lösning:** Du kan behöva ge Terminal eller VS Code behörighet i:
  - Systeminställningar > Sekretess & säkerhet > Automatisering
  - Tillåt åtkomst till Mail

**Problem:** Hittar inte rätt mailbox
- **Lösning:** Använd först `list_mailboxes.py` för att se exakta namn. Vissa mappar kan heta "Skickat" istället för "Sent" beroende på språkinställningar.

## Begränsningar

- **Endast macOS**: Fungerar bara med Apple Mail på macOS
- **Läsoperationer**: Kan inte skicka, ta bort eller ändra mail
- **Enkla mailboxar**: Stödjer endast mailboxar direkt under konton (vissa nästlade mappar kanske inte är tillgängliga)
- **Mail måste vara igång**: Apple Mail måste köras i bakgrunden

## Säkerhet

⚠️ **Viktigt:** Denna skill ger åtkomst till dina mail. Se till att:
- Endast använda med betrodda AI-modeller
- Vara medveten om vilka mail som delas med AI:n
- Granska känslig information innan den delas

## Licens

MIT

## Författare

Latisen