# Repository Setup Guide

Anleitung zur Einrichtung eines neuen Home Assistant Add-on Repositories mit automatischem Release-Workflow.

## Voraussetzungen

### GitHub CLI Token Scopes

Für die vollständige Verwaltung benötigt das `gh` CLI Token folgende Scopes:

```bash
gh auth refresh -s read:packages,write:packages,delete:packages
```

**Benötigte Scopes:**
- `repo` - Repository-Zugriff
- `workflow` - Workflow-Berechtigungen
- `delete_repo` - Zum Löschen von Repos (optional)
- `read:packages` - Packages auflisten
- `write:packages` - Packages erstellen/aktualisieren
- `delete:packages` - Packages löschen

## Neues Repository erstellen

### 1. Repository erstellen

```bash
gh repo create helix-git/<repo-name> --public --clone
cd <repo-name>
```

### 2. Workflow Permissions setzen

```bash
gh api repos/helix-git/<repo-name>/actions/permissions/workflow \
  --method PUT \
  -f default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true
```

### 3. DISPATCH_TOKEN Secret hinzufügen

Das Secret wird für Cross-Repository-Dispatch (Sync zu haos-apps) benötigt:

```bash
gh secret set DISPATCH_TOKEN --repo helix-git/<repo-name>
# Dann den PAT eingeben
```

## Wichtige Namenskonventionen

### Image-Name = Repository-Name

**KRITISCH:** Der Image-Name in `release.yaml` MUSS dem Repository-Namen entsprechen!

```yaml
# release.yaml - Build Step
- name: Build add-on
  uses: home-assistant/builder@2025.02.0
  with:
    args: |
      --${{ matrix.arch }} \
      --target . \
      --image "<repo-name>/{arch}" \    # MUSS dem Repo-Namen entsprechen!
      --docker-hub "ghcr.io/${{ github.repository_owner }}" \
      --addon
```

### config.yaml Image-Pfad

```yaml
# config.yaml
image: "ghcr.io/helix-git/<repo-name>/{arch}"
```

**Beide müssen übereinstimmen!** Sonst werden die Packages unter falschem Namen erstellt.

## Package-Probleme beheben

### Symptom: "403 denied" beim Installieren

```
DockerError(403, 'denied')
```

**Ursachen:**
1. Package nicht public
2. Package existiert nicht unter erwartetem Namen
3. Alte Ghost-Packages von gelöschtem Repo

### Packages auflisten

```bash
gh api "user/packages?package_type=container" --jq '.[] | "\(.name) - \(.visibility)"'
```

### Packages löschen

```bash
# Einzelnes Package löschen (URL-encoded für Slash)
gh api -X DELETE "user/packages/container/<package-name>%2Famd64"
gh api -X DELETE "user/packages/container/<package-name>%2Faarch64"
```

### Alle Packages löschen

```bash
# Alle Container-Packages auflisten und löschen
for pkg in $(gh api "user/packages?package_type=container" --jq '.[].name'); do
  gh api -X DELETE "user/packages/container/$(echo $pkg | sed 's|/|%2F|g')"
  echo "Deleted: $pkg"
done
```

## Repository umbenennen

Wenn ein Repo umbenannt wird:

### 1. Image-Namen anpassen

In `release.yaml`:
```yaml
--image "<neuer-repo-name>/{arch}" \
```

In `config.yaml`:
```yaml
image: "ghcr.io/helix-git/<neuer-repo-name>/{arch}"
```

### 2. Alte Packages löschen

```bash
gh api -X DELETE "user/packages/container/<alter-name>%2Famd64"
gh api -X DELETE "user/packages/container/<alter-name>%2Faarch64"
```

### 3. Submodule in haos-apps aktualisieren

```bash
cd haos-apps
git submodule deinit -f <submodule-name>
rm -rf .git/modules/<submodule-name>
git rm -f <submodule-name>
git submodule add https://github.com/helix-git/<neuer-repo-name>.git <submodule-name>
git add .gitmodules <submodule-name>
git commit -m "fix: Update submodule URL after repo rename"
git push
```

## Troubleshooting

### Build erfolgreich, aber Upload fehlgeschlagen

```
[WARNING] Upload failed on attempt #1
[FATAL] Upload failed on attempt #3
```

**Mögliche Ursachen:**

1. **Ghost-Packages:** Wenn ein Repo gelöscht und neu erstellt wurde, können alte Package-Verknüpfungen Probleme verursachen.
   - Lösung: Alle zugehörigen Packages löschen

2. **Falscher Image-Name:** Image-Name in release.yaml stimmt nicht mit Repo-Name überein.
   - Lösung: `--image` Parameter korrigieren

3. **Package nicht mit Repo verknüpft:**
   - Manuell verknüpfen unter: https://github.com/helix-git?tab=packages
   - Package auswählen → Package settings → Manage Actions access → Repository hinzufügen

### Package nicht public

Nach dem ersten Push ist ein Package standardmäßig private. Entweder:

1. **Manuell:** GitHub → Packages → Package settings → Change visibility → Public
2. **Via API:** (nur für Org-Packages möglich)

## Checkliste für neues Add-on

- [ ] Repository erstellt
- [ ] Workflow Permissions gesetzt
- [ ] DISPATCH_TOKEN Secret hinzugefügt
- [ ] Image-Name in release.yaml = Repository-Name
- [ ] Image-Pfad in config.yaml korrekt
- [ ] Erster Release erfolgreich
- [ ] Packages sind public
- [ ] Submodule in haos-apps hinzugefügt
