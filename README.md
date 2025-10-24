# predicting maimai DX Achievement rate

## Before begining

* Without filtering *outlier*(debatable) data:
  * Very sensitive to `train_test_split()` `random_state` 
  * Linear Regression: $R^2 \leq 0.1$
  * Random Forest Regression: $R^2 \leq 0.2$
* With filtering *outlier* data (e.g. `Chart Constant >= 10.5, Achv >= 85`):
  * Still somewhat fluctuating depending on training or testing data distribution
  * Linear Regression: $R^2 \leq 0.3$
  * Random Forest Regression: $R^2 \leq 0.4$
* Key predictors missing
  * When the player played the songs
  * Number of retries
  * Player's physical and mental condition when playing the songs (e.g. `Heart Rate`, `Fatigue Level`, `# of hours played continuously before playing the song`, etc)
  * `noteCount` data missing for some songs
  * (Data limitation) Only best scores are recorded, not all of the attempts. This might skew results towards [Extreme Value Theorem](https://en.wikipedia.org/wiki/Fisher%E2%80%93Tippett%E2%80%93Gnedenko_theorem).

## How to obtain the CSV dataset

### maimai.csv

This is your personal score.

Install the following bookmarklet and go to your <https://maimaidx-eng.com/maimai-mobile/home/>, and run it:

```javascript
javascript:(function(d){if(["https://maimaidx.jp","https://maimaidx-eng.com"].indexOf(d.location.origin)>=0){var s=d.createElement("script");s.src="https://myjian.github.io/mai-tools/scripts/all-in-one.js?t="+Math.floor(Date.now()/60000);d.body.append(s);}})(document)
```

![Main page buttons](./assets/export-personal-score.png)

Then click "Load all scores", copy the results, and paste it into your spreadsheet software (e.g. Excel), and export it as CSV (Comma-Separated Values, UTF-8) format.

### bpm.csv, songs.csv, etc

Thanks <https://github.com/zetaraku/arcade-songs-fetch> for the effort!

Run the maimai-related scripts, and export the SQLite databases to CSV files (e.g. by using an VSCode SQLite extension).

## How to run

This project uses the [`uv`](https://docs.astral.sh/uv/) package manager. If you don't understand what does it mean, please simply run the following commands:

```bash
git clone https://github.com/eric15342335/maimai-dx-regression
cd maimai-dx-regression
uv sync
```

Then, open `model.ipynb` in VSCode, and run the cells step by step.

## Some other visualizations

![Chart Constant vs Achievement Rate scatter plot](./assets/chart-constant-vs-Achv-scatterplot.png)

## Todo

* Add more details about the instructions on this README.md
* Write a blog on my personal website, talking about how'd I get till here~

Discussions are welcome! ~~I love Salt, do you?~~

[Back to top](#predicting-maimai-dx-achievement-rate)
