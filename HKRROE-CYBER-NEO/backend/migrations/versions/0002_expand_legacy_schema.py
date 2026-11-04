"""Add columns introduced after the original starter schema."""
from alembic import op
from sqlalchemy import inspect, Column, String, Boolean, DateTime, text

revision = '0002_expand_legacy_schema'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def _columns(table_name: str) -> set[str]:
    return {column['name'] for column in inspect(op.get_bind()).get_columns(table_name)}

def upgrade():
    inspector = inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if 'projects' in tables:
        existing = _columns('projects')
        additions = [
            Column('image_url', String(500), nullable=False, server_default=''),
            Column('source_url', String(500), nullable=False, server_default=''),
            Column('status', String(30), nullable=False, server_default='in-progress'),
            Column('featured', Boolean(), nullable=False, server_default=text('false')),
            Column('published', Boolean(), nullable=False, server_default=text('true')),
            Column('updated_at', DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        ]
        for column in additions:
            if column.name not in existing:
                op.add_column('projects', column)
    if 'verifications' in tables and 'updated_at' not in _columns('verifications'):
        op.add_column('verifications', Column('updated_at', DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))

def downgrade():
    inspector = inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if 'verifications' in tables and 'updated_at' in _columns('verifications'):
        op.drop_column('verifications', 'updated_at')
    if 'projects' in tables:
        for name in ('updated_at','published','featured','status','source_url','image_url'):
            if name in _columns('projects'):
                op.drop_column('projects', name)
