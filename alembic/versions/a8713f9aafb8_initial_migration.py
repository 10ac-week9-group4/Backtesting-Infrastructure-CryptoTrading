"""Initial migration

Revision ID: a8713f9aafb8
Revises: 
Create Date: 2024-06-22 09:12:37.913583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8713f9aafb8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dim_assets',
    sa.Column('AssetID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('AssetName', sa.String(length=100), nullable=True),
    sa.Column('AssetType', sa.String(length=50), nullable=True),
    sa.Column('TickerSymbol', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('AssetID')
    )
    op.create_table('dim_date',
    sa.Column('DateKey', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('Date', sa.Date(), nullable=True),
    sa.Column('Year', sa.Integer(), nullable=True),
    sa.Column('Quarter', sa.Integer(), nullable=True),
    sa.Column('Month', sa.Integer(), nullable=True),
    sa.Column('Day', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('DateKey')
    )
    op.create_table('dim_strategy',
    sa.Column('StrategyID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('StrategyName', sa.String(length=100), nullable=True),
    sa.Column('StrategyDescription', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('StrategyID')
    )
    op.create_table('dim_users',
    sa.Column('UserID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('UserName', sa.String(length=100), nullable=True),
    sa.Column('Email', sa.String(length=100), nullable=True),
    sa.Column('PasswordHash', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('UserID')
    )
    op.create_table('dim_scene',
    sa.Column('SceneID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('Symbol', sa.String(length=10), nullable=True),
    sa.Column('StartDate', sa.Date(), nullable=True),
    sa.Column('EndDate', sa.Date(), nullable=True),
    sa.Column('StrategyID', sa.Integer(), nullable=True),
    sa.Column('Parameters', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['StrategyID'], ['dim_strategy.StrategyID'], ),
    sa.PrimaryKeyConstraint('SceneID')
    )
    op.create_table('fact_backtests',
    sa.Column('BacktestID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('DateKey', sa.Integer(), nullable=True),
    sa.Column('UserID', sa.Integer(), nullable=True),
    sa.Column('StrategyID', sa.Integer(), nullable=True),
    sa.Column('MaxDrawdown', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('SharpeRatio', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('TotalReturn', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('TradeCount', sa.Integer(), nullable=True),
    sa.Column('WinningTrades', sa.Integer(), nullable=True),
    sa.Column('LosingTrades', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['DateKey'], ['dim_date.DateKey'], ),
    sa.ForeignKeyConstraint(['StrategyID'], ['dim_strategy.StrategyID'], ),
    sa.ForeignKeyConstraint(['UserID'], ['dim_users.UserID'], ),
    sa.PrimaryKeyConstraint('BacktestID')
    )
    op.create_table('fact_crypto_prices',
    sa.Column('CryptoPriceID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('DateKey', sa.Integer(), nullable=True),
    sa.Column('AssetID', sa.Integer(), nullable=True),
    sa.Column('Open', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('High', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('Low', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('Close', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.ForeignKeyConstraint(['AssetID'], ['dim_assets.AssetID'], ),
    sa.ForeignKeyConstraint(['DateKey'], ['dim_date.DateKey'], ),
    sa.PrimaryKeyConstraint('CryptoPriceID')
    )
    op.create_table('fact_stock_prices',
    sa.Column('StockPriceID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('DateKey', sa.Integer(), nullable=True),
    sa.Column('AssetID', sa.Integer(), nullable=True),
    sa.Column('Open', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('High', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('Low', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('Close', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.ForeignKeyConstraint(['AssetID'], ['dim_assets.AssetID'], ),
    sa.ForeignKeyConstraint(['DateKey'], ['dim_date.DateKey'], ),
    sa.PrimaryKeyConstraint('StockPriceID')
    )
    op.create_table('fact_trades',
    sa.Column('TradeID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('DateKey', sa.Integer(), nullable=True),
    sa.Column('UserID', sa.Integer(), nullable=True),
    sa.Column('AssetID', sa.Integer(), nullable=True),
    sa.Column('StrategyID', sa.Integer(), nullable=True),
    sa.Column('TradeType', sa.String(length=10), nullable=True),
    sa.Column('Quantity', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.Column('PricePerUnit', sa.Numeric(precision=18, scale=4), nullable=True),
    sa.ForeignKeyConstraint(['AssetID'], ['dim_assets.AssetID'], ),
    sa.ForeignKeyConstraint(['DateKey'], ['dim_date.DateKey'], ),
    sa.ForeignKeyConstraint(['StrategyID'], ['dim_strategy.StrategyID'], ),
    sa.ForeignKeyConstraint(['UserID'], ['dim_users.UserID'], ),
    sa.PrimaryKeyConstraint('TradeID')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fact_trades')
    op.drop_table('fact_stock_prices')
    op.drop_table('fact_crypto_prices')
    op.drop_table('fact_backtests')
    op.drop_table('dim_scene')
    op.drop_table('dim_users')
    op.drop_table('dim_strategy')
    op.drop_table('dim_date')
    op.drop_table('dim_assets')
    # ### end Alembic commands ###
