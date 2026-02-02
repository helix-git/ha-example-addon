# Home Assistant Add-on Entwicklung

Diese Dokumentation beschreibt, wie ein Home Assistant Add-on mit Ingress, Authentifizierung und Supervisor-API erstellt wird.

## Projektstruktur

```
example-addon/
├── .github/
│   └── workflows/
│       ├── release.yaml      # Release, Build & Sync Workflow
│       └── lint.yaml         # YAML Linting
├── app/
│   ├── app.py               # Flask Application
│   ├── requirements.txt     # Python Dependencies
│   └── templates/
│       └── index.html       # Jinja2 Template
├── config.yaml              # Add-on Konfiguration
├── Dockerfile               # Docker Build
├── run.sh                   # Startskript
├── build.yaml               # Home Assistant Builder Config
├── CHANGELOG.md             # Automatisch generiert
├── CONTRIBUTING.md          # Entwickler-Guide
└── README.md                # Benutzer-Dokumentation
```

## config.yaml - Add-on Konfiguration

```yaml
---
name: "Example Add-on"
description: "Beschreibung des Add-ons"
version: 0.2.0
slug: "example-addon"
image: "ghcr.io/helix-git/ha-example-addon/{arch}"
init: false
arch:
  - aarch64
  - amd64
ingress: true           # Aktiviert Ingress (Web-UI im HA Panel)
ingress_entry: /        # Einstiegspunkt
homeassistant_config: true  # Zugriff auf HA Config-Verzeichnis
auth_api: true          # Authentifizierung über HA
```

### Wichtige Optionen

| Option | Beschreibung |
|--------|--------------|
| `ingress: true` | Aktiviert Web-UI Integration in Home Assistant |
| `ingress_port: 8099` | Port auf dem die App lauscht (intern) |
| `ingress_entry: /` | URL-Pfad für den Einstieg |
| `auth_api: true` | Aktiviert Authentifizierung - Benutzer muss in HA eingeloggt sein |
| `homeassistant_config: true` | Zugriff auf `/config` Verzeichnis |

## Ingress & Authentifizierung

### Ingress Headers

Wenn `auth_api: true` gesetzt ist, sendet Home Assistant diese Headers bei jedem Request:

```
X-Remote-User-Id: <user-uuid>
X-Remote-User-Name: <username>
X-Remote-User-Display-Name: <Anzeigename>
```

### Python/Flask Beispiel

```python
from flask import request

@app.route('/')
def index():
    # Benutzer-Informationen aus Ingress Headers
    user_id = request.headers.get('X-Remote-User-Id')
    user_name = request.headers.get('X-Remote-User-Name')
    user_display_name = request.headers.get('X-Remote-User-Display-Name')

    return f"Hallo {user_display_name}!"
```

## Supervisor API

### SUPERVISOR_TOKEN

Das Token wird automatisch als Umgebungsvariable bereitgestellt:

```python
import os
SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
```

### API Calls

```python
import requests

CORE_API_URL = "http://supervisor/core/api"

headers = {
    "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
    "Content-Type": "application/json",
}

# Alle States abfragen
response = requests.get(f"{CORE_API_URL}/states", headers=headers)
states = response.json()

# Einen spezifischen State
response = requests.get(f"{CORE_API_URL}/states/person.john", headers=headers)
```

### Profilbild des Benutzers

Das Profilbild ist im `person.*` Entity gespeichert:

```python
def get_user_picture(user_id, headers):
    response = requests.get(f"{CORE_API_URL}/states", headers=headers)
    states = response.json()

    for state in states:
        if state.get('entity_id', '').startswith('person.'):
            attrs = state.get('attributes', {})
            if attrs.get('user_id') == user_id:
                return attrs.get('entity_picture')
    return None
```

## Dockerfile

```dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# Alpine Packages installieren
RUN apk add --no-cache \
    bash \
    python3 \
    py3-pip

# App kopieren
COPY app /app/
COPY run.sh /

# Python Dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt --break-system-packages \
    && chmod a+x /run.sh

CMD [ "/run.sh" ]
```

### Wichtig

- `ARG BUILD_FROM` / `FROM $BUILD_FROM` - Home Assistant Builder setzt das Base Image
- `--break-system-packages` - Erforderlich für neuere Python/pip Versionen

## run.sh - Startskript

```bash
#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Add-on..."

# Optional: Konfiguration aus options.json lesen
# CONFIG_VALUE=$(bashio::config 'my_option')

exec python3 /app/app.py
```

### Bashio Funktionen

```bash
bashio::log.info "Info Nachricht"
bashio::log.warning "Warnung"
bashio::log.error "Fehler"

# Config aus options.json lesen
MY_VALUE=$(bashio::config 'my_config_key')

# Prüfen ob Option gesetzt ist
if bashio::config.has_value 'my_option'; then
    ...
fi
```

## Templates mit Dark Mode

Home Assistant injiziert CSS-Variablen für das aktuelle Theme:

```html
<style>
    :root {
        /* Fallback-Werte falls HA nichts injiziert */
        --primary-text-color: #212121;
        --primary-background-color: #fafafa;
        --card-background-color: #ffffff;
    }

    /* Fallback Dark Mode */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-text-color: #e1e1e1;
            --primary-background-color: #111111;
        }
    }

    body {
        background-color: var(--primary-background-color);
        color: var(--primary-text-color);
    }
</style>
```

## build.yaml

```yaml
build_from:
  aarch64: ghcr.io/home-assistant/aarch64-base:3.21
  amd64: ghcr.io/home-assistant/amd64-base:3.21
```

## Lokales Testen

### Mit Docker

```bash
docker build \
  --build-arg BUILD_FROM="ghcr.io/home-assistant/amd64-base:3.21" \
  -t test-addon .

docker run -it --rm \
  -e SUPERVISOR_TOKEN="test" \
  -p 8099:8099 \
  test-addon
```

### In Home Assistant (Dev)

1. Repository als lokales Add-on hinzufügen
2. Add-on installieren
3. Logs prüfen unter Einstellungen → Add-ons → [Add-on] → Log

## Nützliche Links

- [Home Assistant Add-on Dokumentation](https://developers.home-assistant.io/docs/add-ons)
- [Supervisor API](https://developers.home-assistant.io/docs/api/supervisor/endpoints)
- [Ingress](https://developers.home-assistant.io/docs/add-ons/presentation#ingress)
