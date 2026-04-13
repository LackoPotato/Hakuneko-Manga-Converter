import os
import re
import ansi


def listdir(path: str) -> list[str]:
    files: list[str] = []
    for file in os.listdir(path):
        if not file.startswith("."):
            files.append(file)
    return files


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
                f"Path {path} failed regex with expression {expression}")
    return regexed_paths


def numsort(sort: dict[str, str]) -> list[str]:
    keys: list[str] = list(sort)
    keys.sort(key=lambda k: float(sort[k]))
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
) -> list[str]:
    raw_chapter_paths: list[str] = get_directories(manga_path)

    for i, chapter_path in enumerate(raw_chapter_paths):
        print(f"\t{ansi.qformat(str(i), ansi.fore16.red)} {chapter_path}")

    chapter_paths: dict[str, str] = {}
    if chapter_expression:
        chapter_paths = regex_paths(chapter_expression, raw_chapter_paths)
        print(f"{ansi.fore16.cyan}Masked Names: ")
        for i, chapter_path in enumerate(chapter_paths):
            print(
                f"\t{ansi.fore16.red}{i}{ansi.clear} {chapter_paths[chapter_path]}")
    else:
        chapter_paths = {dir: dir for dir in raw_chapter_paths}

    print(
        ansi.qformat(
            "Sorting by float" if page_sort_number else "Sorting by string",
            ansi.fore16.cyan,
        )
    )
    sorted_chapter_keys: list[str] = []
    if chapter_sort_number:
        sorted_chapter_keys = numsort(chapter_paths)
    else:
        sorted_chapter_keys = alphasort(chapter_paths)

    manga_pages: list[dict] = []

    for chapter in sorted_chapter_keys:
        print(f"{ansi.qformat('Chapter Title: ', ansi.fore16.cyan)}{chapter}")
        print(
            f"{ansi.qformat('Chapter Path: ', ansi.fore16.cyan)}{chapter_paths[chapter]}"
        )
        chapter_path: str = os.path.join(manga_path, chapter)
        page_paths: dict[str, str] = {}
        if page_expression:
            page_paths = {
                os.path.join(chapter_path, page): os.path.splitext(page)[0]
                for page in regex_paths(page_expression, listdir(chapter_path))
            }
        else:
            page_paths = {
                os.path.join(chapter_path, page): os.path.splitext(page)[0]
                for page in listdir(chapter_path)
            }
        manga_pages.append(page_paths)

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
