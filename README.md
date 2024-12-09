# Data Scraping
Simple data scraping on brazilian real state site. Real State Brasília - DF website.

URL: https://www.dfimoveis.com.br/venda/df/brasilia/imoveis

## Requirements
```
pip3 install requests
pip3 install beautifulsoup4
pip3 install selenium
```
Open Google Chrome and verify it's version: Google Chrome -> Definitions -> About Chrome
Install compatible ChromeDriver to use Selenium: https://googlechromelabs.github.io/chrome-for-testing/#stable

## Libs
- Requests: get HTML from the URL.
- Beautiful Soup: scraping data. Finds all matching tags and classes from HTML.
- CSV: export data to .csv
- Selenium packages: handle dynamic JavaScript pages. Wait until pages loads.
- Time: sleep between requests. Avoid beign blocked from the site.
