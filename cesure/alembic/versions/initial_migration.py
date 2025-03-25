"""Initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2025-03-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create artists table
    op.create_table('artists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('social_media', sa.String(length=255), nullable=True),
        sa.Column('cv', sa.JSON(), nullable=True),
        sa.Column('profile_image', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create artworks table
    op.create_table('artworks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('medium', sa.String(length=255), nullable=True),
        sa.Column('dimensions', sa.String(length=255), nullable=True),
        sa.Column('year_created', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('is_for_sale', sa.Integer(), nullable=True),
        sa.Column('additional_info', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create events table
    op.create_table('events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=True),
        sa.Column('is_public', sa.String(length=1), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create competitions table
    op.create_table('competitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rules', sa.Text(), nullable=True),
        sa.Column('entry_fee', sa.Float(), nullable=True),
        sa.Column('prize_info', sa.JSON(), nullable=True),
        sa.Column('entry_start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('entry_end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('judging_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('judging_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('results_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create competition_judges table
    op.create_table('competition_judges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('competition_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create competition_entries table
    op.create_table('competition_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('competition_id', sa.Integer(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('artwork_id', sa.Integer(), nullable=False),
        sa.Column('entry_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('artist_statement', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('additional_info', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
        sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create competition_results table
    op.create_table('competition_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('competition_id', sa.Integer(), nullable=False),
        sa.Column('entry_id', sa.Integer(), nullable=False),
        sa.Column('placement', sa.Integer(), nullable=True),
        sa.Column('award_category', sa.String(length=100), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('judge_comments', sa.Text(), nullable=True),
        sa.Column('prize_details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ),
        sa.ForeignKeyConstraint(['entry_id'], ['competition_entries.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('competition_results')
    op.drop_table('competition_entries')
    op.drop_table('competition_judges')
    op.drop_table('competitions')
    op.drop_table('events')
    op.drop_table('artworks')
    op.drop_table('artists')
    op.drop_table('users')