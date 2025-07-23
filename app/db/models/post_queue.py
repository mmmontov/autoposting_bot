from sqlalchemy import Column, Integer, Text, Table, MetaData
from app.db.base import Base


def create_post_queue_model(table_name: str, metadata: MetaData):
    print('таблица создана', table_name)
    return Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True),
        Column('post_text', Text, nullable=False),
        Column('image_url', Text, nullable=True),
        extend_existing=True
    )