"""empty message

Revision ID: 711eb319a68f
Revises: 
Create Date: 2023-04-09 03:26:40.673233

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import event
import logging
import os
SCHEMA = os.environ.get("SCHEMA")


# revision identifiers, used by Alembic.
revision = '711eb319a68f'
down_revision = None
branch_labels = None
depends_on = None

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"SCHEMA: {SCHEMA}")

def log_sql(engine, sql, *_):
    logger.debug(f"SQL: {sql}")

event.listen(op.get_bind(), "before_cursor_execute", log_sql)

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    logger.debug("Running upgrade function")
    op.execute("SET search_path TO pet_overload_db")
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=40), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
        schema=SCHEMA
    )
    op.create_table('questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('details', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], [f'{SCHEMA}.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA
    )
    op.create_table('answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('details', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], [f'{SCHEMA}.questions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], [f'{SCHEMA}.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA
    )
    op.create_table('question_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('is_liked', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], [f'{SCHEMA}.questions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], [f'{SCHEMA}.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA
    )
    op.create_table('answer_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('is_liked', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('answer_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['answer_id'], [f'{SCHEMA}.answers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], [f'{SCHEMA}.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema=SCHEMA
    )
    
    
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    logger.debug("Running downgrade function")

    op.execute("SET search_path TO pet_overload_db")
    op.drop_table('answer_votes', schema=SCHEMA)
    op.drop_table('question_votes', schema=SCHEMA)
    op.drop_table('answers', schema=SCHEMA)
    op.drop_table('questions', schema=SCHEMA)
    op.drop_table('users', schema=SCHEMA)
    # ### end Alembic commands ###
