# Example Add-on

Ein Beispiel-Add-on als Vorlage für eigene Entwicklungen.

## Installation

Dieses Add-on ist Teil des Home Assistant Add-on Repositories.

## Konfiguration

Aktuell sind keine Konfigurationsoptionen verfügbar.

## Verwendung

Nach der Installation startet das Add-on automatisch und gibt periodische Log-Meldungen aus.

---

## Entwicklung

### Conventional Commits

Dieses Repository verwendet [Conventional Commits](https://www.conventionalcommits.org/) für automatische Versionierung.

#### Commit-Typen

| Typ | Beschreibung | Version-Bump |
|-----|--------------|--------------|
| `fix:` | Bugfix | Patch (0.0.x) |
| `feat:` | Neues Feature | Minor (0.x.0) |
| `feat!:` oder `BREAKING CHANGE:` | Breaking Change | Major (x.0.0) |
| `docs:` | Dokumentation | Kein Release |
| `chore:` | Wartung | Kein Release |
| `refactor:` | Code-Refactoring | Kein Release |
| `test:` | Tests | Kein Release |

#### Beispiele

```bash
# Bugfix - Version 0.1.4 -> 0.1.5
git commit -m "fix: Korrigiere Fehler bei der Authentifizierung"

# Neues Feature - Version 0.1.5 -> 0.2.0
git commit -m "feat: Füge Dark Mode hinzu"

# Breaking Change - Version 0.2.0 -> 1.0.0
git commit -m "feat!: Ändere API-Format komplett"
```

### Release-Workflow

```
1. Code ändern
2. Commit mit Conventional Commit Message
3. Push nach `latest` Branch
4. Release-Please erstellt automatisch einen PR
5. PR reviewen und mergen
6. Automatisch:
   - Release wird erstellt
   - Docker Images werden gebaut (aarch64, amd64)
   - config.yaml Version wird aktualisiert
   - haos-apps Repository wird synchronisiert
```

### Pull Requests

1. Branch von `latest` erstellen:
   ```bash
   git checkout latest
   git pull origin latest
   git checkout -b feature/mein-feature
   ```

2. Änderungen committen (Conventional Commits!):
   ```bash
   git add .
   git commit -m "feat: Beschreibung des Features"
   ```

3. Push und PR erstellen:
   ```bash
   git push origin feature/mein-feature
   gh pr create --base latest
   ```

4. Nach Review: PR mergen (Squash empfohlen)

### Lokale Entwicklung

```bash
# Repository klonen
git clone https://github.com/helix-git/ha-example-addon.git
cd ha-example-addon

# Auf latest Branch wechseln
git checkout latest

# Änderungen testen
# ... (lokales Home Assistant oder Docker)
```
