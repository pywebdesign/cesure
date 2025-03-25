"""Add email verification fields

Revision ID: email_verification_fields
Revises: initial_migration
Create Date: 2025-03-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'email_verification_fields'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('verification_token_expires', sa.DateTime(), nullable=True))
    
    # Set all existing users to have verified emails
    op.execute("UPDATE users SET email_verified = true")


def downgrade():
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'email_verified')