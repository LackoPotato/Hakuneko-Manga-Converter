import os
import ansi
import regex as re


class Reader:
    chapter_expression: str = ""
    auto_sort_chapter: bool = False
    auto_sort_chapter_regex: list[str] = []
    ignore_autoreg_failure: bool = False
    chapter_sort_number: bool = True
    manga_path: str = ""
    page_expression: str = ""
    page_sort_number: bool = True
    single_chapter: bool = False

    def __init__(self,
                 manga_path: str,
                 single_chapter: bool = False,
                 chapter_expression: str = "",
                 chapter_sort_number: bool = True,
                 auto_sort_chapter: bool = False,
                 auto_sort_chapter_regex: list[str] = [],
                 ignore_autoreg_failure: bool = False,
                 page_expression: str = "",
                 page_sort_number: bool = True,
                 ) -> None:
        self.chapter_expression = chapter_expression
        self.auto_sort_chapter = auto_sort_chapter
        self.auto_sort_chapter_regex = auto_sort_chapter_regex
        self.ignore_autoreg_failure = ignore_autoreg_failure
        self.chapter_sort_number = chapter_sort_number
        self.manga_path = manga_path
        self.page_expression = page_expression
        self.page_sort_number = page_sort_number
        self.single_chapter = single_chapter

    @staticmethod
    def listdir(path: str) -> list[str]:
        files: list[str] = []
        for file in os.listdir(path):
            if not file.startswith("."):
                files.append(file)
        return files

    @staticmethod
    def auto_try_regex(regex: list[str], paths: list[str]) -> str | None:
        print(ansi.qformat(f"Trying regex: {regex}", ansi.fore16.cyan))
        for expression in regex:
            print(f"\t{expression}")
            r = re.compile(expression)
            failed: bool = False
            for path in paths:
                if not r.search(path):
                    print(f'{ansi.qformat(f"Expression failed to pass", ansi.fore16.cyan)} {
                        expression}{ansi.qformat(f", failed at {path}", ansi.fore16.cyan)}')
                    failed = True
                    break
            if not failed:
                print(ansi.qformat(f"Found working regex: {
                    expression}", ansi.fore16.cyan))
                return expression

        return None

    @staticmethod
    def get_directories(path: str) -> list[str]:
        return [dir for dir in Reader.listdir(path) if os.path.isdir(os.path.join(path, dir))]

    @staticmethod
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
                        f'Path "{path}" failed regex with expression {
                            expression}',
                        ansi.fore16.cyan,
                    )
                )
        return regexed_paths

    @staticmethod
    def numsort(sort: dict[str, str]) -> list[str]:
        keys: list[str] = list(sort)
        try:
            keys.sort(key=lambda k: float(sort[k]))
        except ValueError as error:
            raise ValueError(
                ansi.qformat(
                    "Sorting by number failed! Try applying a regex, preset or removing the sort argument.\nMessage: \n",
                    ansi.fore16.red,
                )
                + str(error)
            )
        return keys

    @staticmethod
    def alphasort(sort: dict[str, str]) -> list[str]:
        keys: list[str] = list(sort)
        keys.sort()
        return keys

    def get_sorted_chapter_paths(self, raw_chapter_paths: list[str]) -> dict[str, str]:
        if len(raw_chapter_paths) > 1:
            if self.auto_sort_chapter:
                print(ansi.qformat(
                    f"Trying to auto-sort chapters with the following: {self.auto_sort_chapter_regex}", ansi.fore16.cyan))
                sort_result = Reader.auto_try_regex(
                    self.auto_sort_chapter_regex, raw_chapter_paths)
                if sort_result:
                    self.chapter_expression = sort_result
                elif not self.ignore_autoreg_failure:
                    raise Exception(
                        f'{ansi.fore16.cyan} "{
                            self.manga_path}" failed the auto-regex!{ansi.clear}'
                    )
                else:
                    print(ansi.qformat(f'[WARNING] {ansi.fore16.cyan} "{
                        self.manga_path}" failed the auto-regex!{ansi.fore16.yellow}, continuing anyways...'), ansi.fore16.yellow)

        if self.chapter_expression:
            return Reader.regex_paths(
                self.chapter_expression, raw_chapter_paths)
        return {dir: dir for dir in raw_chapter_paths}

    def sort_chapters(self, chapter_paths: dict[str, str]) -> list[str]:
        if len(chapter_paths) > 1:
            print(
                ansi.qformat(
                    "Sorting Chapters numerically" if self.chapter_sort_number else "Sorting Chapters alphabetically",
                    ansi.fore16.cyan,
                )
            )
            if self.chapter_sort_number:
                return Reader.numsort(chapter_paths)
            return Reader.alphasort(chapter_paths)
        print(
            ansi.qformat(
                "Skipping Chapter sorting as there is only 1 Chapter",
                ansi.fore16.cyan,
            )
        )
        return list(chapter_paths.keys())

    def read_singular(
        self,
    ) -> list[str]:
        sorted_chapter_keys: list[str] = []
        chapter_paths: dict[str, str] = {}

        if self.single_chapter:
            sorted_chapter_keys = [self.manga_path]
            chapter_paths = {self.manga_path: self.manga_path}
        else:
            raw_chapter_paths: list[str] = Reader.get_directories(
                self.manga_path)
            if len(raw_chapter_paths):
                chapter_paths = self.get_sorted_chapter_paths(
                    raw_chapter_paths)
                sorted_chapter_keys = self.sort_chapters(chapter_paths)
            else:
                raise Exception(
                    f'{ansi.fore16.cyan}Path "{
                        self.manga_path}" has no chapters! If you want to compile a single chapter, use the argument singlechapter {ansi.clear}'
                )
        return self.get_pages(sorted_chapter_keys)

    def get_pages(
        self,
        sorted_chapter_keys: list[str]
    ) -> list[str]:
        manga_pages: list[dict] = []
        for chapter in sorted_chapter_keys:
            chapter_path: str = self.manga_path
            if not self.single_chapter:
                self.chapter_path = os.path.join(self.manga_path, chapter)
            page_paths: dict[str, str] = {}

            if self.page_expression:
                regexed_pages: dict[str, str] = Reader.regex_paths(
                    self.page_expression, Reader.listdir(chapter_path))
                page_paths = {
                    os.path.join(chapter_path, page): regexed_pages[page]
                    for page in regexed_pages
                }
            else:
                page_paths = {
                    os.path.join(chapter_path, page): os.path.splitext(page)[0]
                    for page in Reader.listdir(chapter_path)
                }
            manga_pages.append(page_paths)

        print(
            ansi.qformat(
                "Sorting Pages numerically" if self.page_sort_number else "Sorting Pages alphabetically",
                ansi.fore16.cyan,
            )
        )

        images = []
        for chapter in manga_pages:
            page_key_sort: list[str] = []

            if self.page_sort_number:
                page_key_sort = Reader.numsort(chapter)
            else:
                page_key_sort = Reader.alphasort(chapter)

            for page_key in page_key_sort:
                images.append(page_key)
        return images
