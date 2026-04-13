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


out_dirname = ""
manga_path = ""
out_path = ""

chapter_expression = ""
chapter_sort_number = False
page_expression = ""
page_sort_number = False

if len(sys.argv) == 1:
    raise Exception(f"""No arguments provided\n{ansi.fore16.cyan}HAKUNEKO TO PDF (By LackoPotato :3)

          {ansi.font.bold}REQUIRED Arguments--{ansi.clear}

          {ansi.fore16.red}in=[path/to/input]{ansi.clear}
          \tThe input directory used

          {ansi.fore16.red}out=[path/to/output]{ansi.clear}
          \tThe file it saves the PDF as

          {ansi.fore16.cyan}Optional Arguments--{ansi.clear}

          {ansi.fore16.red}chapter_regex=[regex expression]{ansi.clear}
          \tThe Regular Expression used to mask the chapter directory name (used for sorting)

          {ansi.fore16.red}page_regex=[regex expression]{ansi.clear}
          \tThe Regular Expression used to mask the page directory name (used for sorting)

          {ansi.fore16.red}sortchapternum{ansi.clear}
          \tSorts chapters numerically if possible

          {ansi.fore16.red}sortpagenum{ansi.clear}
          \tSorts pages numerically if possible

    """)

for command in sys.argv[1:]:
    if command.startswith("chapter_regex="):
        chapter_expression = command.removeprefix("chapter_regex=")
    elif command.startswith("page_regex="):
        page_expression = command.removeprefix("page_regex=")
    elif command.startswith("in="):
        manga_path = command.removeprefix("in=")
    elif command.startswith("out="):
        out_path = command.removeprefix("out=")
    elif command == "sortchapternum":
        chapter_sort_number = True
    elif command == "sortpagenum":
        page_sort_number = True
    else:
        raise Exception(
            f"{ansi.qformat('Unknown argument: ', ansi.fore16.red)}{command}"
        )

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

out_path = out_path.format(
    DIRECTORY=os.path.split(manga_path.removesuffix("/"))[1])

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
    ansi.qformat(
        f"Making a PDF of {len(images)} pages at {out_path}", ansi.fore16.cyan)
)

images[0].save(
    out_path,
    "PDF",
    resolution=100.0,
    save_all=True,
    append_images=images[1:],
)
print(ansi.qformat("DONE!!!", ansi.fore16.red, ansi.font.bold))
