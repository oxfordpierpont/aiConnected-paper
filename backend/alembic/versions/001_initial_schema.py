"""Initial schema.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Plans table
    op.create_table(
        'plans',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('price_monthly', sa.Integer(), nullable=False),
        sa.Column('price_yearly', sa.Integer(), nullable=False),
        sa.Column('max_clients', sa.Integer(), default=5),
        sa.Column('max_documents_per_month', sa.Integer(), default=20),
        sa.Column('features', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_plans_slug', 'plans', ['slug'])

    # Agencies table
    op.create_table(
        'agencies',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('subdomain', sa.String(50), nullable=False, unique=True),
        sa.Column('custom_domain', sa.String(255), nullable=True, unique=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('primary_color', sa.String(7), default='#1a4a6e'),
        sa.Column('secondary_color', sa.String(7), default='#b8860b'),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('plan_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('subscription_status', sa.String(50), default='trial'),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('monthly_usage', sa.Integer(), default=0),
        sa.Column('usage_reset_date', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_agencies_slug', 'agencies', ['slug'])
    op.create_index('ix_agencies_subdomain', 'agencies', ['subdomain'])

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(50), default='agency_admin'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('agency_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_agency_id', 'users', ['agency_id'])

    # Clients table
    op.create_table(
        'clients',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('services', postgresql.JSONB(), nullable=True),
        sa.Column('keywords', postgresql.JSONB(), nullable=True),
        sa.Column('tone', sa.String(50), default='professional'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('agency_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_clients_agency_id', 'clients', ['agency_id'])
    op.create_index('ix_clients_slug', 'clients', ['slug'])

    # Templates table
    op.create_table(
        'templates',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('preview_url', sa.String(500), nullable=True),
        sa.Column('template_path', sa.String(255), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('is_pro', sa.Boolean(), default=True),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_templates_slug', 'templates', ['slug'])

    # Documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('content_json', postgresql.JSONB(), nullable=True),
        sa.Column('pdf_url', sa.String(500), nullable=True),
        sa.Column('cover_image_url', sa.String(500), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('statistics_count', sa.Integer(), nullable=True),
        sa.Column('sources_count', sa.Integer(), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('generation_options', postgresql.JSONB(), nullable=True),
        sa.Column('distribution_status', postgresql.JSONB(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('agency_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_documents_agency_id', 'documents', ['agency_id'])
    op.create_index('ix_documents_client_id', 'documents', ['client_id'])
    op.create_index('ix_documents_status', 'documents', ['status'])
    op.create_index('ix_documents_slug', 'documents', ['slug'])

    # Generation Jobs table
    op.create_table(
        'generation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('current_step', sa.String(100), nullable=True),
        sa.Column('progress_percent', sa.Integer(), default=0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('steps', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('api_cost', sa.Float(), nullable=True),
        sa.Column('celery_task_id', sa.String(255), nullable=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=False), nullable=False, unique=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_generation_jobs_status', 'generation_jobs', ['status'])
    op.create_index('ix_generation_jobs_document_id', 'generation_jobs', ['document_id'])

    # Scheduled Content table
    op.create_table(
        'scheduled_content',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('template_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('generation_options', postgresql.JSONB(), nullable=True),
        sa.Column('auto_distribute', sa.Boolean(), default=False),
        sa.Column('distribution_platforms', postgresql.JSONB(), nullable=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scheduled_content_client_id', 'scheduled_content', ['client_id'])
    op.create_index('ix_scheduled_content_status', 'scheduled_content', ['status'])
    op.create_index('ix_scheduled_content_scheduled_date', 'scheduled_content', ['scheduled_date'])

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('agency_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_api_keys_agency_id', 'api_keys', ['agency_id'])

    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(50), nullable=False),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('agency_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_agency_id', 'audit_logs', ['agency_id'])

    # Insert default templates
    op.execute("""
        INSERT INTO templates (id, name, slug, description, template_path, is_public, is_pro, display_order, is_active)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'Professional', 'professional', 'Clean, modern professional design', 'professional/document.html', true, false, 1, true),
        ('00000000-0000-0000-0000-000000000002', 'Executive', 'executive', 'Premium executive-level design', 'executive/document.html', false, true, 2, true),
        ('00000000-0000-0000-0000-000000000003', 'Modern', 'modern', 'Contemporary minimalist design', 'modern/document.html', false, true, 3, true)
    """)

    # Insert default plans
    op.execute("""
        INSERT INTO plans (id, name, slug, price_monthly, price_yearly, max_clients, max_documents_per_month, is_active)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'Pro', 'pro', 4900, 49900, 10, 50, true),
        ('00000000-0000-0000-0000-000000000002', 'Enterprise', 'enterprise', 14900, 149900, 50, 200, true)
    """)


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('api_keys')
    op.drop_table('scheduled_content')
    op.drop_table('generation_jobs')
    op.drop_table('documents')
    op.drop_table('templates')
    op.drop_table('clients')
    op.drop_table('users')
    op.drop_table('agencies')
    op.drop_table('plans')
