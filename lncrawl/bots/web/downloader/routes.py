from ..flaskapp import app
from flask import redirect, request, render_template
from .. import lib
from .job_handler import JobHandler

# ----------------------------------------------- Search Novel ----------------------------------------------- #

@app.route("/lncrawl/addnovel")
def addnovel():
    return render_template("reader/addnovel.html")

@app.route("/lncrawl/addnovel/search/")
@app.route("/lncrawl/addnovel/search/<string:job_id>/")
def search_input_page(job_id=None):
    if not job_id:
        job_id = str(hash(request.remote_addr))

    return render_template("downloader/search_novel.html", job_id=job_id)


@app.route("/lncrawl/addnovel/search/form/", methods=["POST"])
def search_form():
    query = request.form["query"]
    if len(query) < 4:
        return render_template(
            "downloader/queue.html",
            message="Query too short",
            url="/lncrawl/addnovel/search/",
        )
    job_id = (
        request.form["job_id"]
        if "job_id" in request.form
        else str(hash(request.remote_addr))
    )
    if job_id in lib.jobs:
        lib.jobs[job_id].destroy()
    lib.jobs[job_id] = JobHandler(job_id)
    job = lib.jobs[job_id]

    job.get_list_of_novel(query)

    if "redirect" in request.form and request.form["redirect"] == "true":
        return redirect(f"/lncrawl/addnovel/choose_novel/{job_id}")
    else:
        return 200


# ----------------------------------------------- Choose Novel ----------------------------------------------- #


@app.route("/lncrawl/addnovel/choose_novel/")
@app.route("/lncrawl/addnovel/choose_novel/<string:job_id>")
def novel_select_page(job_id=None):
    if not job_id:
        job_id = str(hash(request.remote_addr))
    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")
    job = lib.jobs[job_id]
    if job.is_busy:
        return render_template(
            "downloader/queue.html",
            message=job.get_status(),
            url=f"/lncrawl/addnovel/choose_novel/{job_id}",
        )

    return render_template(
        "downloader/choose_novel.html",
        job_id=job_id,
        search_results=job.search_results,
    )


@app.route("/lncrawl/addnovel/novel_selected/<int:novel_id>")
@app.route("/lncrawl/addnovel/novel_selected/<int:novel_id>/<string:job_id>")
def novel_selected(novel_id, job_id=None):
    if not job_id:
        job_id = str(hash(request.remote_addr))
    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")
    job = lib.jobs[job_id]
    if job.is_busy:
        return render_template(
            "downloader/queue.html",
            message=job.get_status(),
            url=f"/lncrawl/addnovel/novel_selected/{novel_id}/{job_id}",
        )

    job.select_novel(novel_id)

    return redirect(f"/lncrawl/addnovel/choose_source/{job_id}")


# ----------------------------------------------- Choose Source ----------------------------------------------- #


@app.route("/lncrawl/addnovel/choose_source/")
@app.route("/lncrawl/addnovel/choose_source/<string:job_id>")
def source_select_page(job_id=None):
    if not job_id:
        job_id = str(hash(request.remote_addr))
    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")
    job = lib.jobs[job_id]
    if job.is_busy:
        return render_template(
            "downloader/queue.html",
            message=job.get_status(),
            url=f"/lncrawl/addnovel/choose_source/{job_id}",
        )

    return render_template(
        "downloader/choose_source.html",
        job_id=job_id,
        sources=job.get_list_of_sources(),
    )


@app.route("/lncrawl/addnovel/source_selected/<int:novel_id>")
@app.route("/lncrawl/addnovel/source_selected/<int:novel_id>/<string:job_id>")
def source_selected(novel_id, job_id=None):
    if not job_id:
        job_id = str(hash(request.remote_addr))
    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")
    job = lib.jobs[job_id]
    if job.is_busy:
        return render_template(
            "downloader/queue.html",
            message=job.get_status(),
            url=f"/lncrawl/addnovel/source_selected/{novel_id}/{job_id}",
        )

    job.select_source(novel_id)

    return redirect(f"/lncrawl/addnovel/download/{job_id}")



@app.route("/lncrawl/addnovel/download/")
@app.route("/lncrawl/addnovel/download/<string:job_id>")
def downloaded_page(job_id=None):
    if not job_id:
        job_id = str(hash(request.remote_addr))

    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")

    job = lib.jobs[job_id]
    if job.is_finished:
        return render_template("downloader/downloaded.html", job_id=job_id, job=job)

    if job.is_busy:
        return render_template(
            "downloader/queue.html",
            message=job.get_status(),
            url=f"/lncrawl/addnovel/download/{job_id}",
        )

    job.select_range()
    job.start_download()

    return render_template(
        "downloader/queue.html",
        message=job.get_status(),
        url=f"/lncrawl/addnovel/download/{job_id}",
    )
