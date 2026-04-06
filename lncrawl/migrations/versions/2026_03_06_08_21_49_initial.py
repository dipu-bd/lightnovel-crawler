"""Initial

Revision ID: 71de6ded2787
Revises:
Create Date: 2026-03-06 08:21:49.013198
"""

from typing import Sequence, Union

import sqlmodel as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlmodel.sql.sqltypes import AutoString

from lncrawl.dao import enums

# revision identifiers, used by Alembic.
revision: str = "4d43af0bd879"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    # Users table
    op.create_table(
        "users",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("referrer_id", AutoString(), nullable=True),
        sa.Column("password", AutoString(), nullable=False),
        sa.Column("email", AutoString(), nullable=False),
        sa.Column("name", AutoString(), nullable=True),
        sa.Column("role", sa.Enum(enums.UserRole, name="userrole"), nullable=False),
        sa.Column("tier", sa.Enum(enums.UserTier, name="usertier"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["referrer_id"], ["users.id"], ondelete="SET NULL", name=op.f("users_referrer_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("users_pkey")),
    )
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_updated_at"), "users", ["updated_at"], unique=False)

    # Verified email table
    op.create_table(
        "verifiedemail",
        sa.Column("email", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("email", name=op.f("verifiedemail_pkey")),
    )

    # User Tokens table
    op.create_table(
        "user_tokens",
        sa.Column("token", sa.CHAR(10), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("token"),
    )

    # Secrets table
    op.create_table(
        "secrets",
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("name", AutoString(length=255), nullable=False),
        sa.Column("value", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("secrets_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("name", name=op.f("secrets_pkey")),
    )
    op.create_index(op.f("ix_secrets_created_at"), "secrets", ["created_at"], unique=False)
    op.create_index(op.f("ix_secrets_name"), "secrets", ["name"], unique=False)
    op.create_index(op.f("ix_secrets_user_id"), "secrets", ["user_id"], unique=False)

    # Jobs table
    op.create_table(
        "jobs",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("parent_job_id", AutoString(), nullable=True),
        sa.Column("depends_on", AutoString(), nullable=True),
        sa.Column("type", sa.Enum(enums.JobType, name="jobtype"), nullable=False),
        sa.Column("priority", sa.Enum(enums.JobPriority, name="jobpriority"), nullable=False),
        sa.Column("status", sa.Enum(enums.JobStatus, name="jobstatus"), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("error", AutoString(), nullable=True),
        sa.Column("started_at", sa.BigInteger(), nullable=True),
        sa.Column("finished_at", sa.BigInteger(), nullable=True),
        sa.Column("done", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("failed", sa.Integer(), server_default=sa.literal(0), nullable=False),
        sa.ForeignKeyConstraint(
            ["depends_on"], ["jobs.id"], ondelete="CASCADE", name=op.f("jobs_depends_on_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["parent_job_id"], ["jobs.id"], ondelete="CASCADE", name=op.f("jobs_parent_job_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("jobs_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("jobs_pkey")),
    )
    op.create_index(op.f("ix_jobs_created_at"), "jobs", ["created_at"], unique=False)
    op.create_index(op.f("ix_jobs_updated_at"), "jobs", ["updated_at"], unique=False)
    op.create_index(op.f("ix_jobs_depends_on"), "jobs", ["depends_on", "is_done"], unique=False)
    op.create_index(op.f("ix_jobs_is_done"), "jobs", ["is_done"], unique=False)
    op.create_index(
        op.f("ix_jobs_ordering"), "jobs", ["priority", "user_id", "updated_at"], unique=False
    )
    op.create_index(op.f("ix_jobs_parent_job_id"), "jobs", ["parent_job_id"], unique=False)
    op.create_index(op.f("ix_jobs_scheduler"), "jobs", ["status", "done", "type"], unique=False)

    # Novels table
    op.create_table(
        "novels",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("domain", AutoString(), nullable=False),
        sa.Column("url", AutoString(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("authors", AutoString(), nullable=True),
        sa.Column("synopsis", AutoString(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("cover_url", AutoString(), nullable=True),
        sa.Column("mtl", sa.Boolean(), nullable=False),
        sa.Column("rtl", sa.Boolean(), nullable=False),
        sa.Column("manga", sa.Boolean(), nullable=False),
        sa.Column("language", sa.CHAR(length=2), nullable=True),
        sa.Column("volume_count", sa.Integer(), nullable=False),
        sa.Column("chapter_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("novels_pkey")),
        sa.UniqueConstraint("url", name="novels_url_key"),
    )
    op.create_index(op.f("ix_novels_created_at"), "novels", ["created_at"], unique=False)
    op.create_index(op.f("ix_novels_domain"), "novels", ["domain"], unique=False)
    op.create_index(op.f("ix_novels_updated_at"), "novels", ["updated_at"], unique=False)
    if dialect == "postgresql":
        op.alter_column(
            "novels", "tags", existing_type=postgresql.JSON(astext_type=sa.Text()), nullable=False
        )

    # Tags table
    op.create_table(
        "tags",
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("description", AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("name", name=op.f("tags_pkey")),
    )

    # Libraries table
    op.create_table(
        "libraries",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("description", AutoString(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("libraries_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("libraries_pkey")),
    )
    op.create_index(op.f("ix_libraries_created_at"), "libraries", ["created_at"], unique=False)
    op.create_index(op.f("ix_libraries_updated_at"), "libraries", ["updated_at"], unique=False)
    op.create_index(op.f("ix_libraries_user_id"), "libraries", ["user_id"], unique=False)
    op.create_index(op.f("ix_libraries_name"), "libraries", ["name"], unique=False)

    # Library novels table
    op.create_table(
        "library_novels",
        sa.Column("library_id", AutoString(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_id"],
            ["libraries.id"],
            ondelete="CASCADE",
            name=op.f("library_novels_library_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["novel_id"],
            ["novels.id"],
            ondelete="CASCADE",
            name=op.f("library_novels_novel_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("library_id", "novel_id", name=op.f("library_novels_pkey")),
    )

    # Volumes table
    op.create_table(
        "volumes",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("serial", sa.Integer(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("chapter_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["novel_id"], ["novels.id"], ondelete="CASCADE", name=op.f("volumes_novel_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("novel_id", "serial", name="volumes_novel_id_serial_key"),
    )
    op.create_index(op.f("ix_volume_novel_id"), "volumes", ["novel_id"], unique=False)
    op.create_index(op.f("ix_volume_novel_serial"), "volumes", ["novel_id", "serial"], unique=False)
    op.create_index(op.f("ix_volumes_created_at"), "volumes", ["created_at"], unique=False)
    op.create_index(op.f("ix_volumes_updated_at"), "volumes", ["updated_at"], unique=False)

    # Chapters table
    op.create_table(
        "chapters",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("serial", sa.Integer(), nullable=False),
        sa.Column("volume_id", AutoString(), nullable=True),
        sa.Column("url", AutoString(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["novel_id"], ["novels.id"], ondelete="CASCADE", name=op.f("chapters_novel_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["volume_id"], ["volumes.id"], ondelete="SET NULL", name=op.f("chapters_volume_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("novel_id", "serial", name="chapters_novel_id_serial_key"),
    )
    op.create_index(op.f("ix_chapter_novel_id"), "chapters", ["novel_id"], unique=False)
    op.create_index(
        op.f("ix_chapter_novel_serial"), "chapters", ["novel_id", "serial"], unique=False
    )
    op.create_index(
        op.f("ix_chapter_novel_volume"), "chapters", ["novel_id", "volume_id"], unique=False
    )
    op.create_index(op.f("ix_chapters_created_at"), "chapters", ["created_at"], unique=False)
    op.create_index(op.f("ix_chapters_updated_at"), "chapters", ["updated_at"], unique=False)

    # Chapter images table
    op.create_table(
        "chapter_images",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("chapter_id", AutoString(), nullable=False),
        sa.Column("url", AutoString(), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chapter_id"],
            ["chapters.id"],
            ondelete="CASCADE",
            name=op.f("chapter_images_chapter_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["novel_id"],
            ["novels.id"],
            ondelete="CASCADE",
            name=op.f("chapter_images_novel_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("chapter_images_pkey")),
    )
    op.create_index(
        op.f("ix_chapter_image_chapter"), "chapter_images", ["chapter_id"], unique=False
    )
    op.create_index(
        op.f("ix_chapter_images_created_at"), "chapter_images", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_chapter_images_updated_at"), "chapter_images", ["updated_at"], unique=False
    )

    # Artifacts table
    op.create_table(
        "artifacts",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("job_id", AutoString(), nullable=True),
        sa.Column("user_id", AutoString(), nullable=True),
        sa.Column("format", sa.Enum(enums.OutputFormat, name="outputformat"), nullable=False),
        sa.Column("file_name", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], ondelete="SET NULL", name=op.f("artifacts_job_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["novel_id"], ["novels.id"], ondelete="CASCADE", name=op.f("artifacts_novel_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="SET NULL", name=op.f("artifacts_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("artifacts_pkey")),
    )
    op.create_index(op.f("ix_artifacts_created_at"), "artifacts", ["created_at"], unique=False)
    op.create_index(op.f("ix_artifacts_format"), "artifacts", ["format"], unique=False)
    op.create_index(op.f("ix_artifacts_novel_id"), "artifacts", ["novel_id"], unique=False)
    op.create_index(op.f("ix_artifacts_updated_at"), "artifacts", ["updated_at"], unique=False)

    # Read history table
    op.create_table(
        "read_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("chapter_id", AutoString(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("volume_id", AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["chapter_id"],
            ["chapters.id"],
            ondelete="CASCADE",
            name=op.f("read_history_chapter_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["novel_id"], ["novels.id"], ondelete="CASCADE", name=op.f("read_history_novel_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("read_history_user_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["volume_id"],
            ["volumes.id"],
            ondelete="SET NULL",
            name=op.f("read_history_volume_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("read_history_pkey")),
        sa.UniqueConstraint("user_id", "chapter_id", name="read_history_user_id_chapter_id_key"),
    )
    op.create_index(
        op.f("ix_read_history_user_created"),
        "read_history",
        ["user_id", "created_at"],
        unique=False,
    )

    # Feedback table
    op.create_table(
        "feedback",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("type", sa.Enum(enums.FeedbackType, name="feedbacktype"), nullable=False),
        sa.Column("status", sa.Enum(enums.FeedbackStatus, name="feedbackstatus"), nullable=False),
        sa.Column("subject", AutoString(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("feedback_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("feedback_pkey")),
    )
    op.create_index(op.f("ix_feedback_created_at"), "feedback", ["created_at"], unique=False)
    op.create_index(op.f("ix_feedback_updated_at"), "feedback", ["updated_at"], unique=False)
    op.create_index(op.f("ix_feedback_status"), "feedback", ["status"], unique=False)
    op.create_index(op.f("ix_feedback_type"), "feedback", ["type"], unique=False)
    op.create_index(op.f("ix_feedback_user_id"), "feedback", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    if dialect != "sqlite":
        op.drop_constraint(op.f("users_referrer_id_fkey"), "users", type_="foreignkey")
        op.drop_constraint(op.f("jobs_user_id_fkey"), "jobs", type_="foreignkey")
        op.drop_constraint(op.f("jobs_parent_job_id_fkey"), "jobs", type_="foreignkey")
        op.drop_constraint(op.f("jobs_depends_on_fkey"), "jobs", type_="foreignkey")
        op.drop_constraint(op.f("secrets_user_id_fkey"), "secrets", type_="foreignkey")
        op.drop_constraint(op.f("novels_url_key"), "novels", type_="unique")
        op.drop_constraint(op.f("libraries_user_id_fkey"), "libraries", type_="foreignkey")
        op.drop_constraint(
            op.f("library_novels_novel_id_fkey"), "library_novels", type_="foreignkey"
        )
        op.drop_constraint(
            op.f("library_novels_library_id_fkey"), "library_novels", type_="foreignkey"
        )
        op.drop_constraint(op.f("volumes_novel_id_serial_key"), "volumes", type_="unique")
        op.drop_constraint(op.f("volumes_novel_id_fkey"), "volumes", type_="foreignkey")
        op.drop_constraint(op.f("chapters_novel_id_serial_key"), "chapters", type_="unique")
        op.drop_constraint(op.f("chapters_novel_id_fkey"), "chapters", type_="foreignkey")
        op.drop_constraint(op.f("chapters_volume_id_fkey"), "chapters", type_="foreignkey")
        op.drop_constraint(
            op.f("chapter_images_chapter_id_fkey"), "chapter_images", type_="foreignkey"
        )
        op.drop_constraint(
            op.f("chapter_images_novel_id_fkey"), "chapter_images", type_="foreignkey"
        )
        op.drop_constraint(op.f("artifacts_job_id_fkey"), "artifacts", type_="foreignkey")
        op.drop_constraint(op.f("artifacts_novel_id_fkey"), "artifacts", type_="foreignkey")
        op.drop_constraint(op.f("artifacts_user_id_fkey"), "artifacts", type_="foreignkey")
        op.drop_constraint(
            op.f("read_history_user_id_chapter_id_key"), "read_history", type_="unique"
        )
        op.drop_constraint(op.f("read_history_chapter_id_fkey"), "read_history", type_="foreignkey")
        op.drop_constraint(op.f("read_history_novel_id_fkey"), "read_history", type_="foreignkey")
        op.drop_constraint(op.f("read_history_user_id_fkey"), "read_history", type_="foreignkey")
        op.drop_constraint(op.f("read_history_volume_id_fkey"), "read_history", type_="foreignkey")
        op.drop_constraint(op.f("feedback_user_id_fkey"), "feedback", type_="foreignkey")

    op.drop_index(op.f("ix_novels_created_at"), "novels")
    op.drop_index(op.f("ix_novels_domain"), "novels")
    op.drop_index(op.f("ix_novels_updated_at"), "novels")
    op.drop_index(op.f("ix_libraries_name"), "libraries")
    op.drop_index(op.f("ix_libraries_user_id"), "libraries")
    op.drop_index(op.f("ix_libraries_updated_at"), "libraries")
    op.drop_index(op.f("ix_libraries_created_at"), "libraries")
    op.drop_index(op.f("ix_users_created_at"), "users")
    op.drop_index(op.f("ix_users_email"), "users")
    op.drop_index(op.f("ix_users_updated_at"), "users")
    op.drop_index(op.f("ix_jobs_created_at"), "jobs")
    op.drop_index(op.f("ix_jobs_updated_at"), "jobs")
    op.drop_index(op.f("ix_secrets_created_at"), "secrets")
    op.drop_index(op.f("ix_secrets_name"), "secrets")
    op.drop_index(op.f("ix_secrets_user_id"), "secrets")
    op.drop_index(op.f("ix_volume_novel_id"), "volumes")
    op.drop_index(op.f("ix_volume_novel_serial"), "volumes")
    op.drop_index(op.f("ix_volumes_created_at"), "volumes")
    op.drop_index(op.f("ix_volumes_updated_at"), "volumes")
    op.drop_index(op.f("ix_chapter_novel_id"), "chapters")
    op.drop_index(op.f("ix_chapter_novel_serial"), "chapters")
    op.drop_index(op.f("ix_chapter_novel_volume"), "chapters")
    op.drop_index(op.f("ix_chapters_created_at"), "chapters")
    op.drop_index(op.f("ix_chapters_updated_at"), "chapters")
    op.drop_index(op.f("ix_chapter_image_chapter"), "chapter_images")
    op.drop_index(op.f("ix_chapter_images_created_at"), "chapter_images")
    op.drop_index(op.f("ix_chapter_images_updated_at"), "chapter_images")
    op.drop_index(op.f("ix_artifacts_created_at"), "artifacts")
    op.drop_index(op.f("ix_artifacts_format"), "artifacts")
    op.drop_index(op.f("ix_artifacts_novel_id"), "artifacts")
    op.drop_index(op.f("ix_artifacts_updated_at"), "artifacts")
    op.drop_index(op.f("ix_read_history_user_created"), "read_history")
    op.drop_index(op.f("ix_feedback_user_id"), "feedback")
    op.drop_index(op.f("ix_feedback_type"), "feedback")
    op.drop_index(op.f("ix_feedback_status"), "feedback")
    op.drop_index(op.f("ix_feedback_created_at"), "feedback")
    op.drop_index(op.f("ix_feedback_updated_at"), "feedback")

    op.drop_table("feedback")
    op.drop_table("read_history")
    op.drop_table("artifacts")
    op.drop_table("chapter_images")
    op.drop_table("chapters")
    op.drop_table("volumes")
    op.drop_table("verifiedemail")
    op.drop_table("jobs")
    op.drop_table("secrets")
    op.drop_table("users")
    op.drop_table("user_tokens")
    op.drop_table("library_novels")
    op.drop_table("libraries")
    op.drop_table("tags")
    op.drop_table("novels")

    if dialect == "postgresql":
        op.execute("DROP TYPE IF EXISTS userrole")
        op.execute("DROP TYPE IF EXISTS usertier")
        op.execute("DROP TYPE IF EXISTS jobtype")
        op.execute("DROP TYPE IF EXISTS jobpriority")
        op.execute("DROP TYPE IF EXISTS jobstatus")
        op.execute("DROP TYPE IF EXISTS outputformat")
        op.execute("DROP TYPE IF EXISTS feedbacktype")
        op.execute("DROP TYPE IF EXISTS feedbackstatus")
