import ansi
import sys
import pages
import os
import shutil


class Arguments:
    SORTCHNUM: str = "sortchapternum"
    SORTPGNUM: str = "sortpagenum"
    CHREG: str = "chapter_regex="
    PGREG: str = "page_regex="
    TEMPLATE: str = "template="
    IN: str = "in="
    OUT: str = "out="


help_string: str = f"""{ansi.fore16.cyan}HAKUNEKO TO HTML (By LackoPotato :3)

        {ansi.font.bold}REQUIRED Arguments--{ansi.clear}

        {ansi.fore16.red}{Arguments.IN}[path/to/input]{ansi.clear}
        \tThe input directory used

        {ansi.fore16.red}{Arguments.OUT}[path/to/output]{ansi.clear}
        \tThe file it saves the HTML file and resources to

        {ansi.fore16.cyan}Optional Arguments--{ansi.clear}

        {ansi.fore16.red}{Arguments.SORTCHNUM}[regex expression]{ansi.clear}
        \tThe Regular Expression used to mask the chapter directory name (used for sorting)

        {ansi.fore16.red}{Arguments.PGREG}[regex expression]{ansi.clear}
        \tThe Regular Expression used to mask the page directory name (used for sorting)

        {ansi.fore16.red}{Arguments.CHREG}{ansi.clear}
        \tSorts chapters numerically, raises Exception if fails to do so.

        {ansi.fore16.red}{Arguments.SORTPGNUM}{ansi.clear}
        \tSorts pages numerically, raises Exception if fails to do so.

        {ansi.fore16.red}{Arguments.TEMPLATE}[path/to/template]{ansi.clear}
        \tThe template file used to make the output html file.
        \tUSES PYTHON's STRING FORMATTING TO ADD
        \t\t%images
        \t\t\tImage elements in the manga
        \tBy default this is ./template.html
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
        case Arguments.SORTCHNUM:
            sortchapternum = True
        case Arguments.SORTPGNUM:
            sortpagenum = True
        case _:
            if argument.startswith(Arguments.CHREG):
                chapter_expression = argument.removeprefix(Arguments.CHREG)
            elif argument.startswith(Arguments.PGREG):
                page_expression = argument.removeprefix(Arguments.PGREG)
            elif argument.startswith(Arguments.IN):
                manga_path = argument.removeprefix(Arguments.IN)
            elif argument.startswith(Arguments.OUT):
                out_path = argument.removeprefix(Arguments.OUT)
            elif argument.startswith(Arguments.TEMPLATE):
                template = argument.removeprefix(Arguments.TEMPLATE)


if manga_path == "":
    raise Exception(ansi.qformat(
        "Path to manga is not provided.", ansi.fore16.cyan))
elif not os.path.exists(manga_path):
    raise Exception(
        ansi.qformat(
            f"Manga Directory [{manga_path}] does not exist", ansi.fore16.cyan)
    )
elif out_path == "":
    raise Exception(ansi.qformat(
        "No output path is provided", ansi.fore16.cyan))
elif not os.path.exists(os.path.dirname(manga_path)):
    raise Exception(
        ansi.qformat(
            f"Output Directory [{os.path.dirname(manga_path)}] does not exist",
            ansi.fore16.cyan,
        )
    )
elif not os.path.exists(template):
    raise Exception(
        ansi.qformat(
            f"Template file [{template}] does not exist", ansi.fore16.cyan)
    )

out_path = out_path.format(
    DIRECTORY=os.path.split(manga_path.removesuffix("/"))[1])

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
    image_tag_list += image_tag_template.format(
        source=os.path.join("./img", filename))

with open(os.path.join(out_path, "index.html"), "w") as html_file:
    html_file.write(html_page.replace("{text}", image_tag_list))
print("DONE!")
