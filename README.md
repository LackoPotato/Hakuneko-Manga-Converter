# Hakuneko Compiler!
Turns downloaded Hakuneko Manga into PDF and HTML files!

To print help page run `python3 compile.py help` or run the script (compile.py) without any arguments.

Example Commands
(to-pdf):
```python3 ./compiler.py out="./{NAME}.pdf" sortchapternum sortpagenum pgpreset=1num chpreset=ch in=/path/to/file```
(to-pdf multiple)
```python3 ./compiler.py out="./{NAME}.pdf" multiple ignore_auto_fail sortchapternum sortpagenum pgpreset=1num chpreset=auto overwrite_duplicate in=/path/to/folder```
(to-html)
```python3 ./compiler.py out="./{NAME}" sortchapternum sortpagenum pgpreset=1num chpreset=ch html in=/path/to/file```
# Depends on the following libraries 
img2pdf: [Link](https://pypi.org/project/img2pdf/)  
Regex: [Link](https://pypi.org/project/regex/)



