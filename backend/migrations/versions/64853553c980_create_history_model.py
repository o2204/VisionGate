"""create history model

Revision ID: 64853553c980
Revises:
Create Date: 2026-05-08 07:08:31.874650
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "64853553c980"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # histories table
    op.create_table(
        "histories",

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False
        ),

        sa.Column(
            "person_name",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "dataset_image",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "captured_image",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "confidence",
            sa.Float(),
            nullable=True
        ),

        sa.Column(
            "is_real",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        ),

        sa.Column(
            "is_allowed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint("id")
    )

    # index
    op.create_index(
        op.f("ix_histories_id"),
        "histories",
        ["id"],
        unique=False
    )

    # users table updates
    op.add_column(
        "users",
        sa.Column(
            "image_path",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        )
    )

    # email unique constraint
    op.drop_index(
        "ix_users_email",
        table_name="users"
    )

    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"]
    )

    # remove old columns
    op.drop_column("users", "is_active")
    op.drop_column("users", "email_verified")


def downgrade() -> None:

    # restore removed columns
    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )

    # remove unique constraint
    op.drop_constraint(
        "uq_users_email",
        "users",
        type_="unique"
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True
    )

    # remove added columns
    op.drop_column("users", "created_at")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "image_path")

    # remove histories table
    op.drop_index(
        op.f("ix_histories_id"),
        table_name="histories"
    )

    op.drop_table("histories")