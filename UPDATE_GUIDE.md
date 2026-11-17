# Update your existing GitHub Pages dashboard (Mac)

**Do not upload the enclosing `hlth-news-dashboard-v3` folder.** The files need to be at the top level of your repository.

## Easiest method: replace just two files

1. Download and unzip `hlth-news-dashboard-v3.zip` on your Mac (double-click in Finder).
2. In your browser, open your existing GitHub repository and choose the **Code** tab.
3. Click **index.html**, then the pencil icon (**Edit this file**).
4. In Finder, open the new `index.html` in TextEdit (right-click > Open With > TextEdit). If TextEdit shows a rendered page instead of code, use a plain-text editor such as VS Code or TextEdit's plain-text mode. Select all and copy the complete HTML source.
5. In GitHub's file editor, select all existing text, paste the new HTML source, and click **Commit changes** (twice if prompted).
6. Repeat steps 3–5 for `fetch_news.py`, using the new version of that file.
7. On GitHub, choose **Actions > Update HLTH news > Run workflow**. Wait for a green checkmark.
8. Open **Settings > Pages > Visit site**. Refresh your page (Command + Shift + R) to load the new design.

Alternatively, on the repository Code page choose **Add file > Upload files**, and drag `index.html` and `fetch_news.py` from the unzipped folder into the repository root. GitHub should show them as replacements; check the destination carefully before committing.

## What to expect

- The header shows today's date based on the viewer's computer.
- Articles with a future **listed article date** are shown in **Upcoming Events / Future Dates** and excluded from the six standard bucket views until that date arrives. They still appear in **All News**.
- The date field is **not** an extracted event date. An announcement published today about a future event will not be identified as upcoming automatically.
- You can drag cards onto the dashed category buttons, or use the **Move to category** dropdown. Manual assignments replace automatic assignments for that article and are labeled accordingly. **Restore automatic categories** removes a manual assignment.
- Manual assignments persist in **this browser only**, using local storage. They are not shared across browsers, devices, or colleagues. Use **Export my category changes** and **Import changes** to transfer assignments manually. The downloaded JSON contains article URLs and category names; treat it as data, not a secret.
- The page checks the latest saved news file every five minutes while open. GitHub Actions still attempts to fetch source articles every 15 minutes, but its schedule can be delayed.
- The fetch script uses expanded keyword rules, so run the workflow again after replacing it to update classifications. The site will only show new classifications once `data/news.json` has been regenerated.
- The data file should be at `data/news.json` at the repository root. Do not move the `.github` or `data` folders.

## Sharing manual category choices with everyone

This version does **not** automatically sync manual changes across viewers. That requires a shared writable database or an approval workflow that commits a shared override file to the repository. A static GitHub Pages site cannot write to GitHub by itself without authentication and an appropriate backend.

## Troubleshooting

- If the page looks unchanged, check that you replaced the top-level `index.html`, wait a few minutes for GitHub Pages, and hard-refresh the browser.
- If new articles are missing, check **Actions > Update HLTH news** and inspect `data/news.json` in GitHub.
- If dragging is awkward on a trackpad or mobile, use the dropdown on each article.
