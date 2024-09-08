from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '<revision_id>'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('client_file', sa.Column('type_of_settlement', sa.String(length=50), nullable=False))
    op.add_column('client_file', sa.Column('type_of_client', sa.String(length=50), nullable=False))

def downgrade():
    op.drop_column('client_file', 'type_of_settlement')
    op.drop_column('client_file', 'type_of_client')