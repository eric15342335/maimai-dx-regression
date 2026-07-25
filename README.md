# predicting maimai DX Achievement rate

## Before beginning

* Key predictors missing
  * When the player played the songs (currently only have the last played date)
  * Player's physical and mental condition when playing the songs
  * (Data limitation) Only best scores are recorded, not all of the attempts. This might skew results towards [Extreme Value Theorem](https://en.wikipedia.org/wiki/Fisher%E2%80%93Tippett%E2%80%93Gnedenko_theorem).
* We don't know the objective of the prediction:
  * Predict the next play? -> sort data by `Last Played` and perform a time series split
    * But this gives poor test set performance, because the test data will have unseen values of `Last Played`, and the model might not generalize well to unseen values.
  * Predict the songs that will be released in the future? -> sort data by `releaseDate` and perform a time series split
    * Then the model is useless for predicting songs that are already released, which are the majority of the songs in the dataset.

Not to mention that I smell some data leakage somewhere in our dataset and/or training code, as when I switch the sorting method, test set size, etc., the performance changes drastically.

Not sure if <https://github.com/google-research/tabfm> will improve the accuracy of the predictions, but if the above questions are not answered, the model will be useless in practice. My disclaimer: Better to treat this project as an Exploratory Data Analysis (EDA) project rather than a real score prediction project.

## How to obtain the CSV dataset

### maimai.csv

This is your personal score.

Install the following bookmarklet and go to your <https://maimaidx-eng.com/maimai-mobile/home/>, and run it:

```javascript
javascript:(function(d){if(["https://maimaidx.jp","https://maimaidx-eng.com"].indexOf(d.location.origin)>=0){var s=d.createElement("script");s.src="https://myjian.github.io/mai-tools/scripts/all-in-one.js?t="+Math.floor(Date.now()/60000);d.body.append(s);}})(document)
```

![Main page buttons](./assets/export-personal-score.png)

Then click "Load all scores", copy the results, and paste it into your spreadsheet software (e.g. Excel), and export it as CSV (Comma-Separated Values, UTF-8) format.

---

### bpm.csv, songs.csv

Thanks <https://github.com/zetaraku/arcade-songs-fetch> for the effort!

Run the maimai-related scripts, and export the SQLite databases to CSV files (e.g. by using an VSCode SQLite extension).

Steps:

* `pnpm install`
* `pnpm approve-builds` and pick `sqlite3`, `puppeteer` and allow them to run.
  If you forget to approve them, delete `pnpm-workspace.yaml` and run `pnpm approve-builds` again.
* Fill in the `.env`:

```ini
# required in maimai/fetch-intl-sheets
MAIMAI_INTL_SEGA_ID='fill in'
MAIMAI_INTL_SEGA_PASSWORD='fill in'
# required in maimai/fetch-internal-levels
GOOGLE_API_KEY='fill in'
# required in maimai/fetch-extras-v2 & maimai/fetch-intl-sheets
USER_AGENT='Windows 11 Node.JS github.com/zetaraku/arcade-songs-fetch'
```

* For Windows, `pnpm config set script-shell "/path/to/bash.exe"` is needed (using `pnpm` as an example here).
  * For example, replace `/path/to/bash.exe` with the output of `where.exe bash`.

* Comment out these in `tsconfig.json`:

```json
  // This is an alias to @tsconfig/node16: https://github.com/tsconfig/bases
  "extends": "ts-node/node16/tsconfig.json",
```

Otherwise you will encounter this error:

```ts
    return new TSError(diagnosticText, diagnosticCodes, diagnostics);
           ^
TSError: ⨯ Unable to compile TypeScript:
error TS6053: File '@tsconfig/node16/tsconfig.json' not found.
```

* Remove `maimai:fetch-images maimai:fetch-versions` from `maimai:all` in `package.json`, since they are slow to run:

```diff
diff --git a/package.json b/package.json
index 492cfd1..c45c095 100644
--- a/package.json
+++ b/package.json
@@ -8,7 +8,7 @@
     "all:gen-json": "npm-run-all maimai:gen-json chunithm:gen-json wacca:gen-json taiko:gen-json jubeat:gen-json sdvx:gen-json ongeki:gen-json gc:gen-json diva:gen-json popn:gen-json drs:gen-json ddr:gen-json nostalgia:gen-json crossbeats:gen-json rb:gen-json gitadora:gen-json polarischord:gen-json museca:gen-json && npm run any:gen-json",
     "all:upload-data": "npm-run-all maimai:upload-data chunithm:upload-data wacca:upload-data taiko:upload-data jubeat:upload-data sdvx:upload-data ongeki:upload-data gc:upload-data diva:upload-data popn:upload-data drs:upload-data ddr:upload-data nostalgia:upload-data crossbeats:upload-data rb:upload-data gitadora:upload-data polarischord:upload-data museca:upload-data any:upload-data",
     "# run-all scripts": "",
- "maimai:all": "npm-run-all maimai:fetch-songs maimai:gen-wiki-list maimai:fetch-images maimai:fetch-versions maimai:fetch-intl-versions maimai:fetch-intl-sheets maimai:fetch-cn-sheets maimai:fetch-extras-v2 maimai:fetch-internal-levels maimai:gen-json maimai:upload-data",
+ "maimai:all": "npm-run-all maimai:fetch-songs maimai:gen-wiki-list maimai:fetch-intl-versions maimai:fetch-intl-sheets maimai:fetch-cn-sheets maimai:fetch-extras-v2 maimai:fetch-internal-levels maimai:gen-json maimai:upload-data",
     "chunithm:all": "npm-run-all chunithm:fetch-songs chunithm:gen-wiki-list chunithm:fetch-images chunithm:fetch-intl-sheets chunithm:fetch-extras chunithm:fetch-sheet-extras-v2 chunithm:fetch-internal-levels chunithm:gen-json chunithm:upload-data",
     "wacca:all": "npm-run-all wacca:fetch-songs wacca:fetch-images wacca:gen-json wacca:upload-data",
     "taiko:all": "npm-run-all taiko:fetch-songs taiko:gen-json taiko:upload-data",
```

Then finally, you can run `pnpm run maimai:all` to generate the SQLite file.

If things does not work, e.g. you encountered:

```bash
arcade-songs-fetch\src\maimai\fetch-intl-versions.ts:81
    throw new Error('An error occurred while fetching the page.');
          ^
Error: An error occurred while fetching the page
```

Disabling any VPN/proxy/network interventing software might help.

After all fetching has finished, retrieve the data in `data/maimai/db.sqlite3`:

* `bpm.csv`: `SongExtras` table
* `songs.csv`: `SheetExtras` table

---

### playcount.csv

![Play Count export UI](./assets/playcount-export.png)

Go to <https://maimaidx-eng.com/maimai-mobile/record/musicGenre/search/?genre=99&diff=3> and run the following script in the browser console:

```js
(async function() {
    const REQUEST_DELAY = 100;
    const STORAGE_KEY = 'maimai_full_extraction_data';
    const DIFFS = [0, 1, 2, 3, 4];

    let cache = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {
        stage: 'discovery',
        diffIndex: 0,
        extractionQueue: [],
        extractionIndex: 0,
        results: []
    };

    const overlay = document.createElement('div');
    overlay.innerHTML = `
        <div id="scraper-ui" style="position:fixed;top:10px;right:10px;z-index:9999;background:rgba(0,0,0,0.9);color:#fff;padding:20px;border-radius:8px;width:320px;font-family:sans-serif;box-shadow:0 4px 12px rgba(0,0,0,0.5);border:1px solid #51bcf3;">
            <div style="margin-bottom:10px;font-weight:bold;color:#51bcf3;display:flex;justify-content:space-between;">
                <span>maimai Data Export</span>
                <span id="close-ui" style="cursor:pointer;opacity:0.5">✕</span>
            </div>
            <div id="status" style="font-size:13px;">Preparing discovery...</div>
            <div id="eta" style="font-size:12px;color:#aaa;margin-top:4px;">Calculating...</div>
            <div style="width:100%;background:#333;height:8px;margin:12px 0;border-radius:4px;overflow:hidden">
                <div id="bar" style="width:0%;background:#51bcf3;height:100%;transition:width 0.3s"></div>
            </div>
            <div id="stats" style="font-size:12px;margin-bottom:10px">Queue: 0 | Total Rows: 0</div>
            <div id="log" style="font-size:10px;height:100px;overflow-y:auto;background:#111;padding:8px;border:1px solid #333;color:#888;margin-bottom:10px;line-height:1.4;"></div>
            <div style="display:flex;gap:5px;">
                <button id="stop-btn" style="flex:2;background:#444;color:white;border:none;padding:8px;border-radius:4px;cursor:pointer;font-size:12px;">Save & Stop</button>
                <button id="reset-btn" style="flex:1;background:#552222;color:#ccc;border:none;padding:8px;border-radius:4px;cursor:pointer;font-size:12px;">Reset</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    const logEl = document.getElementById('log');
    const barEl = document.getElementById('bar');
    const statusEl = document.getElementById('status');
    const etaEl = document.getElementById('eta');
    const statsEl = document.getElementById('stats');
    
    let isRunning = true;
    let currentDelay = REQUEST_DELAY;
    let sessionStartTime = null;

    function updateLog(msg) {
        const div = document.createElement('div');
        div.innerText = msg;
        logEl.appendChild(div);
        logEl.scrollTop = logEl.scrollHeight;
    }

    function save() { localStorage.setItem(STORAGE_KEY, JSON.stringify(cache)); }

    function downloadCSV() {
        if (cache.results.length === 0) return;
        const headers = ["Name", "Version", "Difficulty", "Level", "Achievement", "Play Count", "Last Played"];
        const csv = [headers.join(","), ...cache.results.map(r => 
            `"${r.name.replace(/"/g, '""')}","${r.version}","${r.difficulty}","${r.level}","${r.achievement}",${r.play_count},"${r.last_played}"`
        )].join("\n");
        const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `maimai_export_${new Date().getTime()}.csv`;
        link.click();
    }

    document.getElementById('stop-btn').onclick = () => { isRunning = false; };
    document.getElementById('close-ui').onclick = () => { overlay.remove(); };
    document.getElementById('reset-btn').onclick = () => {
        if(confirm("Clear progress and cache?")) {
            localStorage.removeItem(STORAGE_KEY);
            location.reload();
        }
    };

    const request = async (url) => {
        try {
            const resp = await fetch(url);
            if (resp.status === 403 || resp.status === 503) {
                currentDelay = Math.min(currentDelay * 2, 10000);
                updateLog(`Rate limited. Adjusting delay: ${currentDelay}ms`);
                return { error: 'limit' };
            }
            currentDelay = REQUEST_DELAY;
            return { data: await resp.text() };
        } catch (e) { return { error: e.message }; }
    };

    if (cache.stage === 'discovery') {
        const queueSet = new Set(cache.extractionQueue);
        for (let i = cache.diffIndex; i < DIFFS.length; i++) {
            if (!isRunning) break;
            statusEl.innerText = `Phase 1: Discovering played songs (Diff ${i})`;
            const res = await request(`https://maimaidx-eng.com/maimai-mobile/record/musicGenre/search/?genre=99&diff=${DIFFS[i]}`);
            if (res.data) {
                const doc = new DOMParser().parseFromString(res.data, "text/html");
                doc.querySelectorAll('.w_450.m_15').forEach(el => {
                    if (el.querySelector('.music_score_block')) {
                        const idx = el.querySelector('input[name="idx"]')?.value;
                        if (idx) queueSet.add(idx);
                    }
                });
                cache.extractionQueue = Array.from(queueSet);
                cache.diffIndex = i + 1;
                if (cache.diffIndex === DIFFS.length) cache.stage = 'extraction';
                save();
                statsEl.innerText = `Queue: ${cache.extractionQueue.length} | Rows: 0`;
            }
            await new Promise(r => setTimeout(r, currentDelay));
        }
    }

    if (cache.stage === 'extraction' && isRunning) {
        const total = cache.extractionQueue.length;
        const startIndex = cache.extractionIndex;
        sessionStartTime = Date.now();

        // deduplication map to prevent exact row duplicates
        const seenSignatures = new Set(cache.results.map(r => `${r.name}|${r.version}|${r.difficulty}`));

        for (let i = startIndex; i < total; i++) {
            if (!isRunning) break;
            
            const currentNum = i + 1;
            statusEl.innerText = `Phase 2: Extracting ${currentNum} / ${total}`;
            barEl.style.width = `${(currentNum / total) * 100}%`;
            
            if (i > startIndex) {
                const elapsed = Date.now() - sessionStartTime;
                const avg = elapsed / (i - startIndex);
                const remainingMs = (total - currentNum) * avg;
                const mins = Math.floor(remainingMs / 60000);
                const secs = Math.floor((remainingMs % 60000) / 1000);
                etaEl.innerText = `Remaining: ${mins}m ${secs}s`;
            }

            const res = await request(`https://maimaidx-eng.com/maimai-mobile/record/musicDetail/?idx=${encodeURIComponent(cache.extractionQueue[i])}`);
            
            if (res.data) {
                const doc = new DOMParser().parseFromString(res.data, "text/html");
                const songName = doc.querySelector('.f_15.break')?.innerText.trim() || "Unknown";
                const isDx = doc.querySelector('img[src*="music_dx.png"]');
                const version = isDx ? "DX" : "Standard";

                doc.querySelectorAll('.music_master_score_back, .music_expert_score_back, .music_advanced_score_back, .music_basic_score_back, .music_remaster_score_back').forEach(block => {
                    const table = block.querySelector('.black_block table')?.innerText || "";
                    const playCountMatch = table.match(/PLAY COUNT：\s*(\d+)/);
                    
                    if (playCountMatch) {
                        const diff = block.querySelector('img[src*="diff_"]')?.src.split('diff_')[1].split('.png')[0];
                        const signature = `${songName}|${version}|${diff}`;

                        if (!seenSignatures.has(signature)) {
                            cache.results.push({
                                name: songName,
                                version: version,
                                difficulty: diff,
                                level: block.querySelector('.music_lv_back')?.innerText.trim(),
                                achievement: block.querySelector('.music_score_block.w_120')?.innerText.trim(),
                                play_count: playCountMatch[1],
                                last_played: (table.match(/Last played date：\s*([\d/: ]+)/) || [])[1] || "N/A"
                            });
                            seenSignatures.add(signature);
                        }
                    }
                });
                cache.extractionIndex = i + 1;
                save();
                updateLog(`Fetched: ${songName} (${version === "DX" ? "DX" : "STD"})`);
                statsEl.innerText = `Queue Index: ${currentNum} | Total Rows: ${cache.results.length}`;
            }
            await new Promise(r => setTimeout(r, currentDelay));
        }
    }

    if (cache.extractionIndex === cache.extractionQueue.length && cache.stage === 'extraction') {
        localStorage.removeItem(STORAGE_KEY);
        statusEl.innerText = "Complete";
        etaEl.innerText = "CSV Generated";
    }
    downloadCSV();
})();
```

## How to run

This project uses the [`uv`](https://docs.astral.sh/uv/) package manager.

```bash
git clone https://github.com/eric15342335/maimai-dx-regression
cd maimai-dx-regression
git submodule update --init --recursive --remote # You can skip this if you don't want to obtain the latest arcade-songs-fetch data
pip install -U uv
uv sync
```

> `--remote` in `git submodule update` uses the latest commit from the submodule repository instead of the pinned commit in this repository.

Then, open `model.ipynb` in VSCode, activate the `.venv` virtual environment, and run the notebook cells step by step.

## Some other visualizations

This visualization is generated via [this script](./visualization.py).

![Chart Constant vs Achievement Rate scatter plot](./assets/chart-constant-vs-Achv-scatterplot.png)

## Todo

* Write a blog on my personal website, talking about how'd I get till here~
* Tackle with the flawed assumptions of the data/ML pipeline itself (e.g. future data leakage for train/test split, missing timestamp data, etc)

Discussions are welcome! ~~I love Salt, do you?~~

[My player profile (maimai DX international)](https://otohi.me/dxi/p/eric15342335)

[Back to top](#predicting-maimai-dx-achievement-rate)
