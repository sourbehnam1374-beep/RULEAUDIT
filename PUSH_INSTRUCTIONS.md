# Push to GitHub — three commands

Repo is fully initialized as **Behnam Sour <sourbehnam1374@gmail.com>** on branch `main`, tagged `v0.1.0`. The local git work is done.

## Step 1 — Create the empty GitHub repo

Go to **https://github.com/new** and fill it out:

- **Repository name:** `ruleaudit`
- **Description:** `A data-free structural audit protocol for expert-derived clinical decision rules`
- **Visibility:** **Public** (recommended — needed if you later submit to JOSS)
- ⚠️ **Do NOT** tick "Add a README", "Add .gitignore", or "Choose a license" — yours already has them
- Click **Create repository**

## Step 2 — Push from your computer

Unzip the package somewhere, open a terminal inside the `ruleaudit-pkg/` folder, and paste:

```bash
git remote add origin https://github.com/sourbehnam1374-beep/ruleaudit.git
git push -u origin main
git push origin v0.1.0
```

When git asks for credentials:

- **Username:** `sourbehnam1374-beep`
- **Password:** paste a **Personal Access Token**, not your GitHub password (GitHub stopped accepting passwords for git push in 2021)

If you don't have a token: https://github.com/settings/tokens → **Generate new token (classic)** → tick the `repo` scope → generate → copy. Tokens look like `ghp_xxxxxxxxxxxx`.

## Step 3 — Update the manuscript

Once the repo is live, the placeholder URL in the manuscript becomes real:

> Source code and synthetic datasets for both worked examples are released under a permissive license at **https://github.com/sourbehnam1374-beep/ruleaudit**

I can rebuild the .docx with that URL substituted in once you confirm the push succeeded.

## Optional — Zenodo DOI

For a citable software artifact (recommended before submitting the methods paper):

1. Log in at https://zenodo.org/ with your GitHub account
2. Find `ruleaudit` in the repository list and flip the toggle to enable Zenodo
3. Back on GitHub, go to **Releases** → **Draft a new release** → pick tag `v0.1.0` → publish
4. Zenodo will mint a DOI within a few minutes — paste it into the manuscript

## If anything errors

Paste the exact error here and I'll get you unstuck.
