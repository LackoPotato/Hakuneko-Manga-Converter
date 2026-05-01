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
    inp: str = "in="
    outp: str = "out="
    chreg: str = "chapter_regex="
    pgreg: str = "page_regex="
    chsortnum: str = "sortchapternum"
    pgsortnum: str = "sortpagenum"
    chpreset: str = "chpreset="
    pgpreset: str = "pgpreset="
    help: str = "help"


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


def get_help_page() -> str:
    return f"""{ansi.fore16.cyan}HAKUNEKO TO PDF (By LackoPotato :3)

          {ansi.font.bold}REQUIRED Arguments--{ansi.clear}

          {ansi.fore16.red}{ARGS.inp}[path/to/input]{ansi.clear}
          \tThe input directory used

          {ansi.fore16.red}{ARGS.outp}[path/to/output]{ansi.clear}
          \tThe file it saves the PDF as

          {ansi.fore16.cyan}Optional Arguments--{ansi.clear}

          {ansi.fore16.red}{ARGS.help}{ansi.clear}
          \t Shows this help page

          {ansi.fore16.red}{ARGS.chsortnum}{ansi.clear}
          \tSorts chapters numerically if possible

          {ansi.fore16.red}{ARGS.pgsortnum}{ansi.clear}
          \tSorts pages numerically if possible

          {ansi.fore16.red}{ARGS.chreg}[regex expression]{ansi.clear}
          \tThe Regular Expression used to mask the chapter directory name (used for sorting)
          \tUse {ansi.qformat(ARGS.chpreset, ansi.fore16.red)} if you want a preset

          {ansi.fore16.red}{ARGS.chpreset}[Chapter Preset Option]{ansi.clear}
          \tPresets Options:
          \t\tch
          \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.ch["ch"]}
          \t\t\tGets the first number after Ch. in the directory name (example: Vol 2 Ch.01 returns 01)
          
          \t\t1num
          \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.ch["1num"]}
          \t\t\tGets the first number in the directory name (example: Chapter 02 returns 02)

          {ansi.fore16.red}{ARGS.pgreg}[regex expression]{ansi.clear}
          \tThe Regular Expression used to mask the page directory name (used for sorting)
          \tUse {ansi.qformat(ARGS.pgpreset, ansi.fore16.red)} if you want a preset

          {ansi.fore16.red}{ARGS.pgpreset}[Page Preset Option]{ansi.clear}
          \tPresets Options:
          \t\t1num
          \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.pg["1num"]}
          \t\t\tGets the first number in the filename (example: Name of the Page 03 returns 03)


    """


if len(sys.argv) == 1:
    raise Exception(f"No argument provided!\n\n{get_help_page()}")

for command in sys.argv[1:]:
    if command.startswith(ARGS.chreg):
        chapter_expression = command.removeprefix(ARGS.chreg)
    elif command.startswith(ARGS.pgreg):
        page_expression = command.removeprefix(ARGS.pgreg)
    elif command.startswith(ARGS.chpreset):
        preset: str = command.removeprefix(ARGS.chpreset)
        if preset not in PRESETS.ch:
            raise Exception(
                f"{ansi.qformat('Unknown chapter preset: ', ansi.fore16.red)}{preset}, available: {PRESETS.ch.keys()}"
            )
        chapter_expression = PRESETS.ch[preset]
    elif command.startswith(ARGS.pgpreset):
        preset: str = command.removeprefix(ARGS.pgpreset)
        if preset not in PRESETS.pg:
            raise Exception(
                f"{ansi.qformat('Unknown chapter preset: ', ansi.fore16.red)}{preset}, available: {PRESETS.pg.keys()}"
            )
        chapter_expression = PRESETS.pg[preset]
    elif command.startswith(ARGS.inp):
        manga_path = command.removeprefix(ARGS.inp)
    elif command.startswith(ARGS.outp):
        out_path = command.removeprefix(ARGS.outp)
    elif command == ARGS.chsortnum:
        chapter_sort_number = True
    elif command == ARGS.pgsortnum:
        page_sort_number = True
    elif command == ARGS.help:
        raise Exception(get_help_page())
    else:
        raise Exception(
            f"{ansi.qformat('Unknown argument: ', ansi.fore16.red)}{command}\nUse {ansi.qformat(ARGS.help, ansi.fore16.blue)} if you want to view the help page"
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
