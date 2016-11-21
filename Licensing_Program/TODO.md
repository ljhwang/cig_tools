- Add a remove/replace command that takes a license name so that it can create a
  header_text to find and compare against (and remove high-confidence matches).
- Config needs better error handling.
- More modularization. software_dmv.py still does stuff it shouldn't.
- Config default values are a mess currently.
- Add --ignore-shebang CLI option to config -a.
- Handle files with different copyright dates (Impossible?)
