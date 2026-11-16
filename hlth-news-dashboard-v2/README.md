# HLTH News Intelligence v2

A static, shareable healthcare news dashboard with six domain filters, search, newest-first sorting, and automated previews. No Render or running web server needed after publishing.

## Deploy with GitHub Pages

1. Create a new GitHub repository (for example `hlth-news-dashboard`). Upload **all** files, including `.github/workflows/update-news.yml` and `.nojekyll`, preserving folders. A public repository is the simplest option; anyone can view the resulting site.
2. Under **Settings → Actions → General → Workflow permissions**, allow **Read and write permissions** for GitHub Actions if your repository permits this setting. If an organization policy blocks it, ask an administrator.
3. Under **Actions → Update HLTH news → Run workflow**, trigger the initial fetch. Check the workflow logs. It should commit `data/news.json` with real articles. If it fails, the HLTH website structure or access restrictions may require adapting the parser.
4. Under **Settings → Pages → Build and deployment**, choose **Deploy from a branch**, branch **main**, folder **/(root)**, and save.
5. Once Pages finishes publishing, your shareable URL should resemble `https://YOUR_USERNAME.github.io/hlth-news-dashboard/`.

## How updates work

GitHub Actions attempts to fetch up to 35 linked articles every 15 minutes. GitHub may delay or skip scheduled jobs, especially during high load; schedules on public repositories may be disabled after prolonged inactivity. The webpage also reloads its published JSON every 15 minutes, but new data only appears after the scheduled workflow completes and GitHub Pages publishes the commit. You can manually run the workflow anytime.

The dashboard uses short extracted previews (metadata or article paragraphs), **not AI-generated summaries**. Its classification uses transparent keyword matching, may be imperfect, and may assign up to three domains per article. Unmatched articles appear under **Uncategorized**. The site intentionally does not invent a detailed “Why it matters” claim. Article dates are used when found; missing dates sort last.

## Test locally

```bash
pip install -r requirements.txt
python fetch_news.py
python -m http.server 8000
```

Open `http://localhost:8000`. The script requires network access to HLTH. It will refuse to overwrite existing data if it extracts zero articles. For a quick UI-only test, serve the included empty JSON; the page will display an empty state.

## Limitations

The website's HTML structure may change, or it may block automated requests. Respect the source site's terms, robots guidance, and content rights. The dashboard links to the original articles and only uses short previews. Do not present previews as verified AI-generated analysis. This project does not require an API key, but an AI summarization service could be added later.
