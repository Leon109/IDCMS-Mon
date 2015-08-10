"""add cabinet

Revision ID: 58840f599ed2
Revises: 37e91e07ade2
Create Date: 2015-08-09 17:40:51.905597

"""

# revision identifiers, used by Alembic.
revision = '58840f599ed2'
down_revision = '37e91e07ade2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cabinet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('an', sa.String(length=64), nullable=True),
    sa.Column('wan_ip', sa.String(length=64), nullable=True),
    sa.Column('lan_ip', sa.String(length=64), nullable=True),
    sa.Column('site', sa.String(length=64), nullable=True),
    sa.Column('rack', sa.String(length=64), nullable=True),
    sa.Column('seat', sa.String(length=32), nullable=True),
    sa.Column('bandwidth', sa.String(length=32), nullable=True),
    sa.Column('up_link', sa.String(length=32), nullable=True),
    sa.Column('height', sa.String(length=32), nullable=True),
    sa.Column('brand', sa.String(length=64), nullable=True),
    sa.Column('model', sa.String(length=64), nullable=True),
    sa.Column('sn', sa.String(length=64), nullable=True),
    sa.Column('salesman', sa.String(length=64), nullable=True),
    sa.Column('client', sa.String(length=64), nullable=True),
    sa.Column('c_time', sa.Date(), nullable=True),
    sa.Column('e_time', sa.Date(), nullable=True),
    sa.Column('remark', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cabinet_an'), 'cabinet', ['an'], unique=True)
    op.create_index(op.f('ix_cabinet_lan_ip'), 'cabinet', ['lan_ip'], unique=False)
    op.create_index(op.f('ix_cabinet_wan_ip'), 'cabinet', ['wan_ip'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_cabinet_wan_ip'), table_name='cabinet')
    op.drop_index(op.f('ix_cabinet_lan_ip'), table_name='cabinet')
    op.drop_index(op.f('ix_cabinet_an'), table_name='cabinet')
    op.drop_table('cabinet')
    ### end Alembic commands ###