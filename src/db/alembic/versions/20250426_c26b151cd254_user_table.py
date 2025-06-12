"""script_set_https

Revision ID: c26b151cd254
Revises: 
Create Date: 2025-04-26 21:36:00.673017

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c26b151cd254'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE users (
            id VARCHAR(100) PRIMARY KEY,
            first_name VARCHAR(100) COLLATE "C",
            last_name VARCHAR(100) COLLATE "C",
            birthdate DATE,
            gender VARCHAR(10),
            interests TEXT,
            city VARCHAR(100),
            password BYTEA NOT NULL
        );
        """
    )


def downgrade():
    op.execute("DROP TABLE users;")
