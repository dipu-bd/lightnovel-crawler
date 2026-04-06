from sqlmodel import col, select

from ...dao import Job


def select_ancestors(job_id: str, inclusive: bool = False):
    """
    WITH RECURSIVE ancestors(id) AS (
        SELECT jobs.id AS id FROM jobs
            WHERE jobs.id = %(job_id)s::VARCHAR
        UNION ALL
        SELECT jobs.parent_job_id AS id FROM jobs
            JOIN ancestors ON jobs.id = ancestors.id
    ) SELECT ancestors.id FROM ancestors
    """
    anchor = Job.id if inclusive else Job.parent_job_id
    par = select(col(anchor).label("id")).where(Job.id == job_id).cte("ancestors", recursive=True)
    par = par.union_all(
        select(col(Job.parent_job_id).label("id"))
        .join(par, col(Job.id) == par.c.id)
        .where(col(Job.parent_job_id).is_not(None))
    )
    return select(par.c.id)


def select_descendends(job_id: str, inclusive: bool = False):
    """
    WITH RECURSIVE descendends(id) AS (
        SELECT jobs.id AS id FROM jobs
            WHERE jobs.id = %(job_id)s::VARCHAR
        UNION ALL
            SELECT jobs.id AS id FROM jobs
            JOIN descendends ON jobs.parent_job_id = descendends.id
    ) SELECT descendends.id FROM descendends
    """
    des = select(col(Job.id).label("id")).where(Job.id == job_id).cte("descendends", recursive=True)
    des = des.union_all(
        select(col(Job.id).label("id")).join(des, col(Job.parent_job_id) == des.c.id)
    )
    stmt = select(des.c.id)
    if not inclusive:
        stmt = stmt.where(des.c.id != job_id)
    return stmt
