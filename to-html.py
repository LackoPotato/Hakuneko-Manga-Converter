import ansi
import sys
import pages
import os
import shutil


class ARGS:
    SORTCHNUM: str = "sortchapternum"
    SORTPGNUM: str = "sortpagenum"
    HELP: str = "help"
    CHREG: str = "chapter_regex="
    PGREG: str = "page_regex="
    PRESETCH: str = "chpreset="
    PRESETPG: str = "pgpreset="
    TEMPLATE: str = "template="
    IN: str = "in="
    OUT: str = "out="


class PRESETS:
    ch: dict[str, str] = {"ch": r"(?<=Ch.)[\d\.]*", "1num": r"(?=\d)[\d\.]*"}
    pg: dict[str, str] = {"1num": r"(?=\d)[\d\.]*"}


help_string: str = f"""{ansi.fore16.cyan}HAKUNEKO TO HTML (By LackoPotato :3)

        {ansi.font.bold}REQUIRED Arguments--{ansi.clear}

        {ansi.fore16.red}{ARGS.IN}[path/to/input]{ansi.clear}
        \tThe input directory used

        {ansi.fore16.red}{ARGS.OUT}[path/to/output]{ansi.clear}
        \tThe file it saves the HTML file and resources to

        {ansi.fore16.cyan}Optional Arguments--{ansi.clear}

        {ansi.fore16.red}{ARGS.HELP}{ansi.clear}
          \t Shows this help page

        {ansi.fore16.red}{ARGS.SORTCHNUM}[regex expression]{ansi.clear}
        \tThe Regular Expression used to mask the chapter directory name (used for sorting)

        {ansi.fore16.red}{ARGS.SORTPGNUM}{ansi.clear}
        \tSorts pages numerically, raises Exception if fails to do so.

        {ansi.fore16.red}{ARGS.TEMPLATE}[path/to/template]{ansi.clear}
        \tThe template file used to make the output html file.
        \tUSES PYTHON's STRING FORMATTING TO ADD
        \t\t%images
        \t\t\tImage elements in the manga
        \tBy default this is ./template.html

        {ansi.fore16.red}{ARGS.CHREG}[regex expression]{ansi.clear}
        \tThe Regular Expression used to mask the chapter directory name (used for sorting)
        \tUse {ansi.qformat(ARGS.PRESETCH, ansi.fore16.red)} if you want a preset

        {ansi.fore16.red}{ARGS.PRESETCH}[Chapter Preset Option]{ansi.clear}
        \tPresets Options:
        \t\tch
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.ch["ch"]}
        \t\t\tGets the first number after Ch. in the directory name (example: Vol 2 Ch.01 returns 01)
        
        \t\t1num
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.ch["1num"]}
        \t\t\tGets the first number in the directory name (example: Chapter 02 returns 02)

        {ansi.fore16.red}{ARGS.PGREG}[regex expression]{ansi.clear}
        \tThe Regular Expression used to mask the page directory name (used for sorting)
        \tUse {ansi.qformat(ARGS.PRESETPG, ansi.fore16.red)} if you want a preset

        {ansi.fore16.red}{ARGS.PRESETPG}[Page Preset Option]{ansi.clear}
        \tPresets Options:
        \t\t1num
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.pg["1num"]}
        \t\t\tGets the first number in the filename (example: Name of the Page 03 returns 03)


"""


manga_path = ""
page_expression: str = ""
out_path = ""
chapter_expression: str = ""
sortchapternum: bool = False
sortpagenum: bool = False
template: str = os.path.join(os.path.dirname(sys.argv[0]), "template.html")

if len(sys.argv) == 1:
    raise Exception(f"No arguments provided\n{help_string}")

for argument in sys.argv:
    match argument:
        case ARGS.SORTCHNUM:
            sortchapternum = True
        case ARGS.SORTPGNUM:
            sortpagenum = True
        case ARGS.HELP:
            raise Exception(help_string)
        case _:
            if argument.startswith(ARGS.CHREG):
                chapter_expression = argument.removeprefix(ARGS.CHREG)
            elif argument.startswith(ARGS.PGREG):
                page_expression = argument.removeprefix(ARGS.PGREG)
            elif argument.startswith(ARGS.PRESETCH):
                preset: str = argument.removeprefix(ARGS.PRESETCH)
                if preset not in PRESETS.ch:
                    raise Exception(
                        f"{ansi.qformat('Unknown chapter preset: ', ansi.fore16.red)}{preset}, available: {PRESETS.ch.keys()}"
                    )
                chapter_expression = PRESETS.ch[preset]
            elif argument.startswith(ARGS.PRESETPG):
                preset: str = argument.removeprefix(ARGS.PRESETPG)
                if preset not in PRESETS.pg:
                    raise Exception(
                        f"{ansi.qformat('Unknown chapter preset: ', ansi.fore16.red)}{preset}, available: {PRESETS.pg.keys()}"
                    )
                chapter_expression = PRESETS.pg[preset]
            elif argument.startswith(ARGS.IN):
                manga_path = argument.removeprefix(ARGS.IN)
            elif argument.startswith(ARGS.OUT):
                out_path = argument.removeprefix(ARGS.OUT)
            elif argument.startswith(ARGS.TEMPLATE):
                template = argument.removeprefix(ARGS.TEMPLATE)


if manga_path == "":
    raise Exception(ansi.qformat("Path to manga is not provided.", ansi.fore16.cyan))
elif not os.path.exists(manga_path):
    raise Exception(
        ansi.qformat(f"Manga Directory [{manga_path}] does not exist", ansi.fore16.cyan)
    )
elif out_path == "":
    raise Exception(ansi.qformat("No output path is provided", ansi.fore16.cyan))
elif not os.path.exists(os.path.dirname(manga_path)):
    raise Exception(
        ansi.qformat(
            f"Output Directory [{os.path.dirname(manga_path)}] does not exist",
            ansi.fore16.cyan,
        )
    )
elif not os.path.exists(template):
    raise Exception(
        ansi.qformat(f"Template file [{template}] does not exist", ansi.fore16.cyan)
    )

out_path = out_path.format(DIRECTORY=os.path.split(manga_path.removesuffix("/"))[1])

if (
    os.path.exists(out_path)
    and input(
        ansi.qformat(
            f"Output directory [{out_path}] already exists! Continue anyways? (N/y) ",
            ansi.fore16.red,
        )
    )
    != "y"
):
    raise Exception("Aborted")

print(
    f"{ansi.qformat('Writing file: ', ansi.fore16.cyan)}{out_path}\n{ansi.qformat('Reading Manga Directory: ', ansi.fore16.cyan)}{manga_path}"
)

print(f"{ansi.qformat('Reading Manga: ', ansi.fore16.cyan)}{manga_path}")
image_paths = pages.read(
    manga_path,
    chapter_expression,
    page_expression,
    sortpagenum,
    sortchapternum,
)

print(
    f"{ansi.qformat('Writing ', ansi.fore16.cyan)}{ansi.qformat(str(len(image_paths)), ansi.fore16.red)}{ansi.qformat(' pages!')}"
)
html_page: str = open(template, "r").read()
print(html_page)
root_image_path: str = os.path.join(out_path, "img")
image_tag_template: str = "<img src='{source}'>"
image_tag_list: str = ""
if not os.path.exists(root_image_path):
    os.makedirs(root_image_path)
for i, path in enumerate(image_paths):
    filename = f"{i}{os.path.splitext(path)[1]}"
    shutil.copy(path, os.path.join(root_image_path, filename))
    image_tag_list += image_tag_template.format(source=os.path.join("./img", filename))

with open(os.path.join(out_path, "index.html"), "w") as html_file:
    html_file.write(html_page.replace("{text}", image_tag_list))
print("DONE!")
