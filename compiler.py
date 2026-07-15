#!/usr/bin/env python3

from PIL import Image
from PIL import ImageChops
import ansi
import os
import sys
import pages
import shutil


def listdir(path: str) -> list[str]:
    files: list[str] = []
    for file in os.listdir(path):
        if not file.startswith("."):
            files.append(file)
    return files


class AUTOFILLS:
    DIR: str = "{directory}"


class ARGS:
    IN: str = "in"
    OUT: str = "out"
    CHREG: str = "chapter_regex"
    PGREG: str = "page_regex"
    SORTCHNUM: str = "sortchapternum"
    SORTPGNUM: str = "sortpagenum"
    PRESETCH: str = "chpreset"
    PRESETPG: str = "pgpreset"
    HELP: str = "help"
    OPTIMISE: str = "optimise"
    GREYSCALE_THRESHOLD: str = "greyscale_threshold"
    FORCE_GREYSCALE: str = "greyscale"
    HTML: str = "html"
    TEMPLATE: str = "template"
    TAGTEMPLATE: str = "tag_template"
    RESOLUTION: str = "resolution"
    SINGLE_CHAPTER: str = "singlechapter"
    QUALITY: str = "quality"
    MULTIPLE: str = "multiple"

# PRESETS
# To add a new preset, add another entry into the corresponding dictionary with it's name as the key and it's regex as the value.
# ignore[] preset, Based off of this StackOverflow answer by Wiktor Stribiżew: https://stackoverflow.com/a/76529927


class PRESETS:
    AUTO: str = "auto"
    ch: dict[str, str] = {
        "ch": r"(?<=Ch.)[\d\.]*",
        "ignore[]": r"((?=\d)[\d\.]*)(?!(?<=\[[^][]*)[^][]*])",
        "1num": r"(?=\d)[\d\.]*"
    }
    pg: dict[str, str] = {"1num": r"(?=\d)[\d\.]*"}


out_dirname = ""
manga_path = ""
out_path = ""

chapter_expression = ""
chapter_sort_number = False
page_expression = ""
page_sort_number = False
template: str = os.path.join(os.path.dirname(sys.argv[0]), "template.html")
image_tag_template: str = "<img src='{source}'>"
export_as_html: bool = False
optimise: bool = False
greyscale_threshold: float = 0
resolution: float = 100.0
force_greyscale: bool = False
single_chapter: bool = False
quality: int = 75

auto_try_chapter_presets: bool = False
auto_try_page_presets: bool = False

help_string: str = f"""{ansi.fore16.cyan}HAKUNEKO COMPILER (By LackoPotato :3)
        If you want to export as HTML, use the argument {ansi.fore16.red}{ARGS.HTML}{ansi.fore16.cyan}

        {ansi.font.bold}REQUIRED Arguments--{ansi.clear}

        {ansi.fore16.red}{ARGS.IN}=[path/to/input]{ansi.clear}
        \tThe input directory used

        {ansi.fore16.red}{ARGS.OUT}=[path/to/output]{ansi.clear}
        \tThe file it saves the output as [Including the filename!], use the format string {AUTOFILLS.DIR} to use the name of the input directory by default.

        {ansi.fore16.cyan}Optional Arguments--{ansi.clear}

        {ansi.fore16.red}{ARGS.HELP}{ansi.clear}
        \tShows this help page

        {ansi.fore16.red}{ARGS.HTML}{ansi.clear}
        \tExports the file as a HTML folder instead of a PDF
        \tIf this argument is not added, exports as PDF by default

        {ansi.fore16.red}{ARGS.MULTIPLE}{ansi.clear}
        \tExports the file as a HTML folder instead of a PDF
        \tIf this argument is not added, exports as PDF by default

        {ansi.fore16.red}{ARGS.SORTCHNUM}{ansi.clear}
        \tSorts chapters numerically if possible

        {ansi.fore16.red}{ARGS.SORTPGNUM}{ansi.clear}
        \tSorts pages numerically if possible

        {ansi.fore16.red}{ARGS.SINGLE_CHAPTER}{ansi.clear}
        \tCompiles a single chapter
        \t\tIf the input directory is a chapter of a manga (a single folder with a list of images), using this setting skips the chapter scanning step and directly compiles it.

        {ansi.fore16.red}{ARGS.CHREG}=[regex expression]{ansi.clear}
        \tThe Regular Expression used to mask the chapter directory name (used for sorting)
        \tUse {ansi.qformat(ARGS.PRESETCH, ansi.fore16.red)} if you want a preset

        {ansi.fore16.red}{ARGS.PRESETCH}=[Chapter Preset Option]{ansi.clear}
        \tPresets Options:
        \t\tauto
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: None, is a special preset
        \t\t\tAutomatically tries all presets in the order {PRESETS.ch.keys()}. On failing to sort, it instead switches to the next preset and tries again.

        \t\tch
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.ch["ch"]}
        \t\t\tGets the first number after Ch. in the directory name (example: Vol 2 Ch.01 returns 01)

        \t\tignore[]
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.ch["ignore[]"]}
        \t\t\tExcludes any result in between square brackets (example: [Vol 1] Hunting Potatoes Chapter 1 returns 1)

        \t\t1num
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.ch["1num"]}
        \t\t\tGets the first number in the directory name (example: Chapter 02 returns 02)

        {ansi.fore16.red}{ARGS.PGREG}=[regex expression]{ansi.clear}
        \tThe Regular Expression used to mask the page directory name (used for sorting)
        \tUse {ansi.qformat(ARGS.PRESETPG, ansi.fore16.red)} if you want a preset

        {ansi.fore16.red}{ARGS.PRESETPG}=[Page Preset Option]{ansi.clear}
        \tPresets Options:
        \t\t1num
        \t\t\t{ansi.qformat("REGEX: ", ansi.fore16.blue)}: {PRESETS.pg["1num"]}
        \t\t\tGets the first number in the filename (example: Name of the Page 03 returns 03)

        {ansi.fore16.cyan}HTML SPECIFIC --{ansi.clear}

        {ansi.fore16.red}{ARGS.TEMPLATE}=[path/to/template]{ansi.clear} (default: {template})
        \tThe template file used to make the output html file.
        \tUSES PYTHON's STRING FORMATTING TO ADD
        \t\t%images
        \t\t\tImage tags (or custom ones if {ansi.fore16.red}{ARGS.TAGTEMPLATE}{ansi.clear} is set)

        {ansi.fore16.red}{ARGS.TAGTEMPLATE}=[TAG TEMPLATE]{ansi.clear} (default: {image_tag_template})
        \tThe template used to insert images into the HTML template
        \tUSES PYTHON's STRING FORMATTING TO ADD
        \t\t%source
        \t\t\tPath to image element

        {ansi.fore16.cyan}PDF SPECIFIC --{ansi.clear}

        {ansi.qformat(ARGS.OPTIMISE, ansi.fore16.red)}
        \tMarginal improvements during testing
        \tOptimises the PDF by checking if the picture is greyscale (Despite being in a different format)
        \tDone by converting it to greyscale (Mode L in PIL, 8 bit Greyscale)
        \t\tGreyscale is defined by checking if the difference between each channel is less than the greyscale threshold (by default: {greyscale_threshold})

        {ansi.fore16.red}{ARGS.GREYSCALE_THRESHOLD}=[Value: float]{ansi.clear} (default: {greyscale_threshold})
        \tOnly works if {ansi.qformat(ARGS.OPTIMISE, ansi.fore16.red)} is set!
        \tThe threshold checks if an image is greyscale, comparing the difference in value between each channel in the image.
        \tOnly converts to greyscale if it is less than the threshold.

        {ansi.fore16.red}{ARGS.RESOLUTION}=[Value: float]{ansi.clear} (default: {resolution})
        \tChanges the PDF Export resolution (The size of the PDF file in the reader, not actual PDF quality, see {ansi.qformat(ARGS.QUALITY, ansi.fore16.red)})
        \tNumber more than 0.

        {ansi.fore16.red}{ARGS.QUALITY}=[Value: integer]{ansi.clear} (default: {quality})
        \tChanges the PDF Export quality
        \tNumber between 0 and 100.
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
        case ARGS.OPTIMISE:
            optimise = True
        case ARGS.HTML:
            export_as_html = True
        case ARGS.FORCE_GREYSCALE:
            force_greyscale = True
        case ARGS.SINGLE_CHAPTER:
            single_chapter = True
        case _:
            if "=" in argument:
                stripped_argument: str = argument[: argument.find("=")]
                value: str = argument[argument.find("=") + 1:]
                match stripped_argument:
                    case ARGS.CHREG:
                        chapter_expression = value
                    case ARGS.GREYSCALE_THRESHOLD:
                        try:
                            greyscale_threshold = float(value)
                        except ValueError:
                            raise ValueError(
                                f"{ansi.qformat(f'{ARGS.GREYSCALE_THRESHOLD} is not a float: ', ansi.fore16.red)} {
                                    value}"
                            )
                    case ARGS.QUALITY:
                        try:
                            quality = int(value)
                        except ValueError:
                            raise ValueError(
                                f"{ansi.qformat(f'{ARGS.QUALITY} is not an integer: ', ansi.fore16.red)} {
                                    value}"
                            )
                    case ARGS.RESOLUTION:
                        try:
                            resolution = float(value)
                        except ValueError:
                            raise ValueError(
                                f"{ansi.qformat(f'{ARGS.RESOLUTION} is not a float: ', ansi.fore16.red)} {
                                    value}"
                            )
                    case ARGS.GREYSCALE_THRESHOLD:
                        try:
                            greyscale_threshold = int(value)
                        except ValueError:
                            raise ValueError(
                                f"{ansi.qformat(
                                    f'{ARGS.GREYSCALE_THRESHOLD} is not an integer: ', ansi.fore16.red)} {value}"
                            )
                    case ARGS.PRESETCH:
                        preset = value
                        if preset == PRESETS.AUTO:
                            auto_try_chapter_presets = True
                        else:
                            if not (preset in PRESETS.ch):
                                raise Exception(
                                    f"{ansi.qformat('Unknown chapter preset: ', ansi.fore16.red)}{
                                        preset}, available: {PRESETS.ch.keys()} or {PRESETS.AUTO}"
                                )
                            chapter_expression = PRESETS.ch[preset]

                        print(
                            f'{ansi.qformat("Chapter Preset: ", ansi.fore16.cyan)}"{
                                preset}"'
                        )
                    case ARGS.PRESETPG:
                        preset = value
                        if preset == PRESETS.AUTO:
                            auto_try_page_presets = True
                        else:
                            if not (preset in PRESETS.pg):
                                raise Exception(
                                    f"{ansi.qformat('Unknown page preset: ', ansi.fore16.red)}{
                                        preset}, available: {PRESETS.pg.keys()} or {PRESETS.AUTO}"
                                )
                            page_expression = PRESETS.pg[preset]

                        print(
                            f'{ansi.qformat("Chapter Preset: ", ansi.fore16.cyan)}"{
                                preset}"'
                        )
                    case ARGS.IN:
                        manga_path = value
                    case ARGS.TAGTEMPLATE:
                        image_tag_template = value
                    case ARGS.OUT:
                        out_path = value
                    case ARGS.TEMPLATE:
                        template = value
                    case _:
                        raise Exception(
                            f"{ansi.qformat('Unknown argument: ', ansi.fore16.red)}{argument}\nUse {
                                ansi.qformat(ARGS.HELP, ansi.fore16.blue)} if you want to view the help page"
                        )
            else:
                raise Exception(
                    f"{ansi.qformat('Unknown argument: ', ansi.fore16.red)}{argument}\nUse {
                        ansi.qformat(ARGS.HELP, ansi.fore16.blue)} if you want to view the help page"
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
elif export_as_html and not os.path.exists(template):
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
            f"Output file [{out_path}] already exists! Overwrite? (N/y) ",
            ansi.fore16.red,
        )
    )
    != "y"
):
    raise Exception(ansi.qformat("Aborted", ansi.fore16.cyan))

print(
    f"{ansi.qformat('Writing file: ', ansi.fore16.cyan)}{out_path}\n{
        ansi.qformat('Reading Manga Directory: ', ansi.fore16.cyan)}{manga_path}"
)

auto_sort_chapter_presets = [PRESETS.ch[key] for key in PRESETS.ch.keys()]
print(f"{ansi.qformat('Reading Manga: ', ansi.fore16.cyan)}{manga_path}")
image_paths = pages.read(
    manga_path,
    chapter_expression,
    page_expression,
    page_sort_number,
    chapter_sort_number,
    single_chapter,
    auto_try_chapter_presets,
    auto_sort_chapter_presets

)
images: list = []

if export_as_html:
    html_page: str = open(template, "r").read()
    root_image_path: str = os.path.join(out_path, "img")
    image_tag_template: str = "<img src='{source}'>"
    image_tag_list: str = ""
    if not os.path.exists(root_image_path):
        os.makedirs(root_image_path)
    for i, path in enumerate(image_paths):
        filename = f"{i}{os.path.splitext(path)[1]}"
        shutil.copy(path, os.path.join(root_image_path, filename))
        image_tag_list += image_tag_template.format(
            source=os.path.join("./img", filename)
        )

    with open(os.path.join(out_path, "index.html"), "w") as html_file:
        html_file.write(html_page.replace("{text}", image_tag_list))
else:
    for page in image_paths:
        print(ansi.qformat(f"\t{page}", ansi.fore16.red))
        image: Image.Image = Image.open(page)
        if force_greyscale:
            if image.mode != "L":
                image = image.convert("L")
        elif optimise:
            if image.mode != "L":
                channels: list[Image.Image] = []
                for i in range(len(image.getbands())):
                    channels.append(image.getchannel(i))

                color: bool = False
                for channel in channels[1:]:
                    extrema = ImageChops.difference(channels[0], channel).getextrema()[
                        1
                    ]
                    print(f"\t\tDifference: {extrema}")
                    # Checking if float even though it is not required (is a single-band image and will always be a float), done so to make pyright happy
                    if extrema is float and extrema > greyscale_threshold:
                        color = True
                        break
                if color:
                    if image.mode != "RGB":
                        print("\t\t Color image not in RGB: Converting")
                        image = image.convert("RGB")
                else:
                    print("\t\t Greyscale image: Converting")
                    image = image.convert("L")
            else:
                print("\t\tAlready Greyscale")
        elif image.mode != "RGB":
            image = image.convert("RGB")
            print("CONVERTING")
        images.append(image.copy())

    print(
        ansi.qformat(
            f"Making a PDF of {len(images)} pages at {
                out_path}", ansi.fore16.cyan
        )
    )

    images[0].save(
        out_path,
        "PDF",
        resolution=resolution,
        save_all=True,
        append_images=images[1:],
        quality=quality,
    )
print(ansi.qformat("DONE!!!", ansi.fore16.red, ansi.font.bold))
