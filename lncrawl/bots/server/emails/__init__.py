from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent


@lru_cache
def get_jinja2_env():
    return Environment(
        loader=FileSystemLoader(str(ROOT)),
        autoescape=select_autoescape(['html', 'xml'])
    )


@lru_cache
def otp_template():
    return get_jinja2_env().get_template("otp.jinja2")


@lru_cache
def job_template():
    return get_jinja2_env().get_template("job.jinja2")
