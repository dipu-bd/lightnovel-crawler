from ..flaskapp import app
from flask import redirect, request, render_template
from .. import lib
from .job_handler import JobHandler

# ----------------------------------------------- Search Novel ----------------------------------------------- #


@app.route("/lncrawl/addnovel/search/")
@app.route("/lncrawl/addnovel/search/<string:job_id>/")
def search_input_page(job_id=None):
    if not job_id:
        job_id = str(hash(request.remote_addr))

    return render_template("downloader/search_novel.html", job_id=job_id)


@app.route("/lncrawl/addnovel/search/form", methods=["POST"])
def search_form():
    request.form = request.json

    query = request.form["inputContent"]
    if len(query) < 4:
        return {"message" : "Query too short"}, 400
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

    return {"status": "success"}, 200


# ----------------------------------------------- Choose Novel ----------------------------------------------- #


@app.route("/lncrawl/addnovel/choose_novel/")
@app.route("/lncrawl/addnovel/choose_novel/<string:job_id>")
def novel_select_page(job_id=None):
    """Return search results"""
    if not job_id:
        job_id = str(hash(request.remote_addr))
    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")
    job = lib.jobs[job_id]
    if job.is_busy:
        return {"status": "pending", "html": job.get_status()}, 200
    return {"status": "success", "novels": job.search_results}, 200



# ----------------------------------------------- Choose Source ----------------------------------------------- #


@app.route("/lncrawl/addnovel/choose_source/<int:novel_id>")
@app.route("/lncrawl/addnovel/choose_source/<int:novel_id>/<string:job_id>")
def novel_selected(novel_id, job_id=None):
    """Return list of sources for selected novel"""
    if not job_id:
        job_id = str(hash(request.remote_addr))
    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")
    job = lib.jobs[job_id]
    if job.is_busy:
        return {"status": "pending", "html": job.get_status()}, 200

    job.select_novel(novel_id)

    return {"status":"success", "sources":job.get_list_of_sources()}, 200

# ----------------------------------------------- Start Download ----------------------------------------------- #

@app.route("/lncrawl/addnovel/download/<int:novel_id>/<int:source_id>")
@app.route("/lncrawl/addnovel/download/<int:novel_id>/<int:source_id>/<string:job_id>")
def download(novel_id, source_id, job_id=None):
    """Select Source and start download"""
    if not job_id:
        job_id = str(hash(request.remote_addr))
    if not job_id in lib.jobs:
        return redirect("/lncrawl/addnovel/search")
    job = lib.jobs[job_id]

    if job.is_busy:
        return {"status": "pending", "html": job.get_status()}, 200

    if job.is_finished:
        return {"status": "success", "html": job.get_status()}, 200

    if not job.metadata_downloaded:
        job.select_novel(novel_id)
        job.select_source(source_id)
        return {"status": "pending", "html": job.get_status()}, 200
    
    job.select_range()
    job.start_download()

    return {"status": "pending", "html": job.get_status()}, 200