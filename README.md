# predicting maimai DX Achievement rate

<!-- markdownlint-disable MD033 -->
<a target="_blank" href="https://colab.research.google.com/github/eric15342335/maimai-dx-regression/blob/main/model.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
<!-- markdownlint-enable MD033 -->

## Before begining

* R^2: ~0.1
  * Inconclusive analysis
* We don't have timestamp data regarding when the player played the songs, number of retries, etc.

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

### Todo

* Add more details about the instructions on this README.md

Discussions are welcome!

[Back to top](#predicting-maimai-dx-achievement-rate)
