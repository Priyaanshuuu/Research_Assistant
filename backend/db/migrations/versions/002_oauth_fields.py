"""Add OAuth fields to user model

Revision ID: 002_oauth_fields
Revises: 001_initial_schema
Create Date: 2026-05-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add GITHUB to authprovider enum (safely, checking if google exists first)
    op.execute("""
        DO $$ BEGIN
            -- Check if 'google' already exists in enum
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumtypid = 'authprovider'::regtype 
                AND enumlabel = 'google'
            ) THEN
                -- If google doesn't exist, just add it
                ALTER TYPE authprovider ADD VALUE 'google';
            END IF;
            
            -- Now add github if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumtypid = 'authprovider'::regtype 
                AND enumlabel = 'github'
            ) THEN
                ALTER TYPE authprovider ADD VALUE 'github';
            END IF;
        END $$;
    """)
    
    # Add email_verified column
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"),
    )
    
    # Add image column for OAuth profile pictures
    op.add_column(
        "users",
        sa.Column("image", sa.Text(), nullable=True),
    )
    
    # Add UNIQUE constraint to provider_id (with special handling for NULLs)
    op.create_index(
        "ix_users_provider_id_unique",
        "users",
        ["provider_id"],
        unique=True,
        postgresql_where=sa.text("provider_id IS NOT NULL")
    )


def downgrade() -> None:
    # Drop the index
    op.drop_index("ix_users_provider_id_unique", table_name="users")
    
    # Drop the columns
    op.drop_column("users", "image")
    op.drop_column("users", "email_verified")
