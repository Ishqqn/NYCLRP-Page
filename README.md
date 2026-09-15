# NYCLRP Site

A single-file website for an ER:LC (Emergency Response: Liberty County) roleplay community — hero, join steps, a live-editable staff roster, and a staff application blurb.

## Files

- `index.html` — the entire site: markup, styles, and behavior in one file.
- `CNAME` — tells GitHub Pages which custom domain to serve (currently `nyclrp.com`). Delete this file if you don't want a custom domain.

## Editing text and links

Everything is plain HTML — open `index.html` in any editor and search (Ctrl+F) for the text below.

| What | Find this in the file | Notes |
|---|---|---|
| Browser tab title | `<title>` near the top | Shown in the browser tab and search results. |
| Header brand name | `NYCLRP DISPATCH` inside `<div class="brand">` | Next to the "NYC" badge icon. |
| Hero heading | `New York City<br><span class="accent">Liberty Roleplay</span>` | The big headline. |
| Hero description | the `<p class="lede">` right after the heading | One paragraph under the headline. |
| Dispatch log box | the four `<div class="dp-line">` lines in `.dispatch-panel` | The little terminal-style box next to the hero. |
| Stat numbers | `.stats` block (`24/7`, `10-99`, etc.) | The four tiles under the hero. |
| "How to join" steps | the three `.step` blocks inside `<section id="join">` | Each has a `step-no`, a heading, and a sentence. |
| Staff applications | `<section id="apply">` | Requirements text and the three requirement cards. |
| Footer disclaimer | `<footer>` at the bottom | Legal-style disclaimer line. |

**Discord and Roblox links:** don't hardcode these in the HTML — set them from the live site itself. Open the site, click **Staff Manager** (bottom-right corner), and paste your invite links under "Server Links." They're saved automatically and immediately update both buttons in the hero.

## Managing staff (ranks)

Click **Staff Manager** in the bottom-right corner of the page:

- **Add to roster** — fill in name, Roblox username, Discord tag, badge number (optional), and pick a rank, then save.
- **Edit** a staff card — click the "Edit" button that appears in the top-right of that card, change the fields, and save.
- **Remove** — click the "Remove" button on a staff card.
- Ranks are fixed to seven tiers (Owner → Trial Moderator) in the `<select id="f-rank">` dropdown. To rename a rank or add a tier, edit the `RANK_ORDER` array near the top of the `<script>` block and the matching `<option>` list in the Staff Manager form — both need the same numeric keys (7 = highest).

**Important:** staff data and the Discord/Roblox links are saved in the browser's `localStorage`, not to a shared server. That means:
- Changes you make persist for you, on that browser, across reloads.
- A visitor on a different computer, or you in a different browser, won't see your edits — each browser has its own copy.
- Clearing browser data/cookies for the site will erase the saved roster.

If you want every visitor to see the same live roster (true shared state across devices), you'll need a small backend or database behind the page — ask if you want that built out.

## Colors, fonts, and layout

All design tokens live at the top of the `<style>` block in `:root { ... }`:

- `--accent` — the amber highlight color (buttons, headings, stat numbers).
- `--bg`, `--surface`, `--surface-2` — background layers.
- `--ink`, `--ink-dim` — text colors.
- A second copy of these values under `@media (prefers-color-scheme: dark)` controls dark mode — change both if you want a color to look the same in light and dark.

Fonts are loaded from Google Fonts in the `<link rel="stylesheet" ...>` tag near the top:
- **Oswald** — headings (condensed, all-caps look).
- **Inter** — body text.
- **JetBrains Mono** — badge numbers, ranks, and the dispatch log (monospace).

To change a font, swap the Google Fonts URL and update the matching `--font-display` / `--font-body` / `--font-mono` variable.

## Deploying to GitHub Pages with a custom domain

1. **Push this folder to a GitHub repo:**
   ```
   git init
   git add .
   git commit -m "NYCLRP site"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
2. **Enable Pages:** repo → Settings → Pages → Source: "Deploy from a branch" → Branch: `main`, folder `/ (root)` → Save.
3. **DNS records** at your domain registrar for `nyclrp.com`:

   | Type | Name | Value |
   |---|---|---|
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | `<your-username>.github.io` |

4. Back in Settings → Pages, enter `nyclrp.com` under "Custom domain" and save. Once DNS propagates, check **Enforce HTTPS**.

If you ever change the domain, update the `CNAME` file to match — it must contain exactly the domain you want (no `http://`, no trailing slash).
