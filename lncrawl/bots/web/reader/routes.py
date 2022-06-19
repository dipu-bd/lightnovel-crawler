from ..flaskapp import app
from flask import redirect, render_template, request, send_from_directory
from .. import lib
from urllib.parse import unquote_plus
import json
from math import ceil

@app.route("/lncrawl/")
@app.route("/lncrawl/page-<int:page>")
def menu(page=None):
    last_page = ceil(len(lib.all_downloaded_novels) / 50)
    start = ((page if page else 1) - 1) * 50
    stop = min((page if page else 1) * 50, len(lib.all_downloaded_novels))

    return render_template(
        "reader/menu.html",
        novels=lib.all_downloaded_novels[start:stop],
        page=page,
        last_page=last_page,
    )


@app.route("/lncrawl/novel/<path:novel_and_source_path>/chapterlist/")
@app.route("/lncrawl/novel/<path:novel_and_source_path>/chapterlist/page-<int:page>")
def chapterlist(novel_and_source_path, page=None):

    novel_and_source_path = lib.LIGHTNOVEL_FOLDER / unquote_plus(novel_and_source_path)
    novel = lib.get_novel_info_source(novel_and_source_path)

    with open(novel_and_source_path / "meta.json", "r", encoding="utf-8") as f:
        chapters = json.load(f)["chapters"]
        start = ((page if page else 1) - 1) * 100
        stop = min((page if page else 1) * 100, len(chapters))
        chapters = chapters[start:stop]

    return render_template(
        "reader/chapterlist.html",
        novel=novel,
        chapters=chapters,
        page=page,
        last_page=ceil(novel.chapter_count / 100),
    )


@app.route("/lncrawl/novel/<path:novel_and_source_path>/gotochap", methods=["POST"])
def gotochap(novel_and_source_path):
    return redirect(
        f"/lncrawl/novel/{novel_and_source_path}/chapter-{request.form.get('chapno')}"
    )


@app.route("/lncrawl/novel/<path:novel_and_source_path>/")
def novel_info(novel_and_source_path):
    novel_and_source_path = lib.LIGHTNOVEL_FOLDER / unquote_plus(novel_and_source_path)
    novel = lib.get_novel_info_source(novel_and_source_path)
    current_source = novel_and_source_path.name
    return render_template(
        "reader/novel_info.html",
        novel=novel,
        len_sources=len(novel.sources),
        current_source=current_source,
    )


@app.route("/lncrawl/novel/<path:novel_and_source_path>/chapter-<int:chapter_id>")
def chapter(novel_and_source_path, chapter_id: int):
    chapter_folder = (
        lib.LIGHTNOVEL_FOLDER / unquote_plus(novel_and_source_path) / "json"
    )
    chapter_file = chapter_folder / f"{str(chapter_id).zfill(5)}.json"

    prev_chapter = chapter_folder / f"{str(chapter_id - 1).zfill(5)}.json"
    next_chapter = chapter_folder / f"{str(chapter_id + 1).zfill(5)}.json"

    with open(chapter_file, encoding="utf8") as f:
        chapter = json.load(f)

    novel = lib.get_novel_info_source(
        lib.LIGHTNOVEL_FOLDER / unquote_plus(novel_and_source_path)
    )

    return render_template(
        "reader/chapter.html",
        chapter=chapter,
        is_prev=prev_chapter.exists(),
        is_next=next_chapter.exists(),
        novel=novel,
    )

@app.route("/lncrawl/novel/<path:novel_and_source_path>/images/<string:image_name>/")
def novel_image(novel_and_source_path, image_name:str):
    file = f"{unquote_plus(novel_and_source_path)}/images/{image_name}"
    path = lib.LIGHTNOVEL_FOLDER / file
    if path.exists():
        return send_from_directory(lib.LIGHTNOVEL_FOLDER, file)
    else:
        print(path)
        print(path.name)

from difflib import SequenceMatcher


@app.route("/lncrawl/lnsearchlive", methods=["POST"])
def lnsearchlive():
    search_query = request.form.get("inputContent").replace("+", " ")

    # [(Novel, similarity), ]
    ratio = [
        (novel, SequenceMatcher(None, search_query, novel.title).quick_ratio())
        for novel in lib.all_downloaded_novels
    ]

    search_results = [
        e[0]
        for e in sorted(ratio, key=lambda x: x[1], reverse=True)[
            : min(20, len(lib.all_downloaded_novels))
        ]
    ]

    return {
        "$id": "1",
        "success": True,
        "resultview": render_template(
            "reader/lnsearchlive.html", novels=search_results
        ),
    }


@app.route("/lncrawl/search")
def search():
    return render_template("reader/search.html")
