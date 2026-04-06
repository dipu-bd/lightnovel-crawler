from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent


@lru_cache(1)
def get_jinja2_env():
    return Environment(
        loader=FileSystemLoader(str(ROOT)), autoescape=select_autoescape(["html", "xml"])
    )


@lru_cache(1)
def otp_template():
    return get_jinja2_env().get_template("otp.html.j2")


@lru_cache(1)
def repass_template():
    return get_jinja2_env().get_template("repass.html.j2")


@lru_cache(1)
def job_full_novel_template():
    return get_jinja2_env().get_template("full_novel.html.j2")


@lru_cache(1)
def job_status_template():
    return get_jinja2_env().get_template("job_status.html.j2")
