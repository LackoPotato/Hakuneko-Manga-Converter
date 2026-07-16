import os
import ansi
import regex as re


def listdir(path: str) -> list[str]:
    files: list[str] = []
    for file in os.listdir(path):
        if not file.startswith("."):
            files.append(file)
    return files


def auto_try_regex(regex: list[str], paths: list[str]) -> str | None:
    print(ansi.qformat(f"Trying regex: {regex}", ansi.fore16.cyan))
    for expression in regex:
        print(f"\t{expression}")
        r = re.compile(expression)
        for path in paths:
            if r.search(path):
                print(ansi.qformat(f"Found working regex: {
                      expression}", ansi.fore16.cyan))
                return expression
    return None


def get_directories(path: str) -> list[str]:
    return [dir for dir in listdir(path) if os.path.isdir(os.path.join(path, dir))]


def regex_paths(expression: str, paths: list[str]) -> dict[str, str]:
    regexed_paths: dict[str, str] = {}
    r = re.compile(expression)
    for path in paths:
        m = r.search(path)
        if m:
            regexed_paths[path] = m[0]
        else:
            raise Exception(
                ansi.qformat(
                    f'Path "{path}" failed regex with expression {expression}',
                    ansi.fore16.cyan,
                )
            )
    return regexed_paths


def numsort(sort: dict[str, str]) -> list[str]:
    keys: list[str] = list(sort)
    try:
        keys.sort(key=lambda k: float(sort[k]))
    except ValueError:
        raise ValueError(
            ansi.qformat(
                "Sorting by number failed! Try applying a regex, preset or removing the sort argument.\nFailed on: \n",
                ansi.fore16.red,
            )
            + str(sort)
        )
    return keys


def alphasort(sort: dict[str, str]) -> list[str]:
    keys: list[str] = list(sort)
    keys.sort()
    return keys


def read(
    manga_path: str,
    chapter_expression: str = "",
    page_expression: str = "",
    page_sort_number: bool = True,
    chapter_sort_number: bool = True,
    single_chapter: bool = False,
    auto_sort_chapter: bool = False,
    auto_sort_chapter_regex: list[str] = [],
) -> list[str]:
    sorted_chapter_keys: list[str] = []
    chapter_paths: dict[str, str] = {}

    if single_chapter:
        sorted_chapter_keys = [manga_path]
        chapter_paths = {manga_path: manga_path}
    else:
        raw_chapter_paths: list[str] = get_directories(manga_path)
        if len(raw_chapter_paths):
            for i, chapter_path in enumerate(raw_chapter_paths):
                print(f"\t{ansi.qformat(str(i), ansi.fore16.red)} {
                      chapter_path}")

            if auto_sort_chapter:
                print(ansi.qformat(
                    f"Trying to auto-sort chapters with the following: {auto_sort_chapter_regex}", ansi.fore16.cyan))
                sort_result = auto_try_regex(
                    auto_sort_chapter_regex, raw_chapter_paths)
                if sort_result:
                    chapter_expression = sort_result
                else:
                    raise Exception(
                        f'{ansi.fore16.cyan} "{
                            manga_path}" failed the auto-regex!{ansi.clear}'
                    )

            if chapter_expression:
                chapter_paths = regex_paths(
                    chapter_expression, raw_chapter_paths)
                print(f"{ansi.fore16.cyan}Masked Names: ")
                for i, chapter_path in enumerate(chapter_paths):
                    print(
                        f"\t{ansi.fore16.red}{i}{ansi.clear} {
                            chapter_paths[chapter_path]}"
                    )
            else:
                chapter_paths = {dir: dir for dir in raw_chapter_paths}
            print(
                ansi.qformat(
                    "Sorting Chapters numerically" if chapter_sort_number else "Sorting Chapters alphabetically",
                    ansi.fore16.cyan,
                )
            )
            if chapter_sort_number:
                sorted_chapter_keys = numsort(chapter_paths)
            else:
                sorted_chapter_keys = alphasort(chapter_paths)
        else:
            raise Exception(
                f'{ansi.fore16.cyan}Path "{
                    manga_path}" has no chapters! If you want to compile a single chapter, use the argument singlechapter {ansi.clear}'
            )
    manga_pages: list[dict] = []
    for chapter in sorted_chapter_keys:
        print(f"{ansi.qformat('Chapter Title: ', ansi.fore16.cyan)}{chapter}")
        chapter_path: str = manga_path
        if not single_chapter:
            chapter_path = os.path.join(manga_path, chapter)
        print(f"{ansi.qformat('Chapter Path: ', ansi.fore16.cyan)}{chapter_path}")
        page_paths: dict[str, str] = {}

        if page_expression:
            regexed_pages: dict[str, str] = regex_paths(
                page_expression, listdir(chapter_path))
            page_paths = {
                os.path.join(chapter_path, page): regexed_pages[page]
                for page in regexed_pages
            }
        else:
            page_paths = {
                os.path.join(chapter_path, page): os.path.splitext(page)[0]
                for page in listdir(chapter_path)
            }
        manga_pages.append(page_paths)

    print(
        ansi.qformat(
            "Sorting Pages numerically" if page_sort_number else "Sorting Pages alphabetically",
            ansi.fore16.cyan,
        )
    )

    images = []
    for chapter in manga_pages:
        page_key_sort: list[str] = []

        if page_sort_number:
            page_key_sort = numsort(chapter)
        else:
            page_key_sort = alphasort(chapter)

        for page_key in page_key_sort:
            images.append(page_key)
    return images
