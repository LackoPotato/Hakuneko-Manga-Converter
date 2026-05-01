from PIL import Image
import ansi
import os
import sys
import pages


def listdir(path: str) -> list[str]:
    files: list[str] = []
    for file in os.listdir(path):
        if not file.startswith("."):
            files.append(file)
    return files


class ARGS:
    IN: str = "in="
    OUT: str = "out="
    CHREG: str = "chapter_regex="
    PGREG: str = "page_regex="
    SORTCHNUM: str = "sortchapternum"
    SORTPGNUM: str = "sortpagenum"
    PRESETCH: str = "chpreset="
    PRESETPG: str = "pgpreset="
    HELP: str = "help"


class PRESETS:
    ch: dict[str, str] = {"ch": r"(?<=Ch.)[\d\.]*", "1num": r"(?=\d)[\d\.]*"}
    pg: dict[str, str] = {"1num": r"(?=\d)[\d\.]*"}


out_dirname = ""
manga_path = ""
out_path = ""

chapter_expression = ""
chapter_sort_number = False
page_expression = ""
page_sort_number = False


help_string: str = f"""{ansi.fore16.cyan}HAKUNEKO TO PDF (By LackoPotato :3)

          {ansi.font.bold}REQUIRED Arguments--{ansi.clear}

          {ansi.fore16.red}{ARGS.IN}[path/to/input]{ansi.clear}
          \tThe input directory used

          {ansi.fore16.red}{ARGS.OUT}[path/to/output]{ansi.clear}
          \tThe file it saves the PDF as

          {ansi.fore16.cyan}Optional Arguments--{ansi.clear}

          {ansi.fore16.red}{ARGS.HELP}{ansi.clear}
          \t Shows this help page

          {ansi.fore16.red}{ARGS.SORTCHNUM}{ansi.clear}
          \tSorts chapters numerically if possible

          {ansi.fore16.red}{ARGS.SORTPGNUM}{ansi.clear}
          \tSorts pages numerically if possible

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


if len(sys.argv) == 1:
    raise Exception(f"No argument provided!\n\n{help_string}")

for argument in sys.argv[1:]:
    match argument:
        case ARGS.SORTCHNUM:
            chapter_sort_number = True
        case ARGS.SORTPGNUM:
            page_sort_number = True
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
            else:
                raise Exception(
                    f"{ansi.qformat('Unknown argument: ', ansi.fore16.red)}{argument}\nUse {ansi.qformat(ARGS.HELP, ansi.fore16.blue)} if you want to view the help page"
                )

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

out_path = out_path.format(DIRECTORY=os.path.split(manga_path.removesuffix("/"))[1])

if (
    os.path.exists(out_path)
    and input(
        ansi.qformat(
            f"Output file [{out_path}] already exists! Overwrite? (N/y) ",
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
    page_sort_number,
    chapter_sort_number,
)
images: list = []

for page in image_paths:
    print(ansi.qformat(f"\t{page}", ansi.fore16.red))
    image = Image.open(page)
    if image.mode != "RGB":
        image = image.convert("RGB")
        print("CONVERTING")
    images.append(image.copy())

print(
    ansi.qformat(f"Making a PDF of {len(images)} pages at {out_path}", ansi.fore16.cyan)
)

images[0].save(
    out_path,
    "PDF",
    resolution=100.0,
    save_all=True,
    append_images=images[1:],
)
print(ansi.qformat("DONE!!!", ansi.fore16.red, ansi.font.bold))
