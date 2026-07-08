from Models import *
import asyncio
from datetime import datetime
from typing import List
from typing import Optional
from datetime import date
from sqlalchemy import inspect
from sqlalchemy import ForeignKey 
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,validates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from Models import *
from Models.BaseClass import Base
#engine = create_engine("postgresql+psycopg://reyan:1234@localhost:5432/mydb", echo=True)

#Base.metadata.create_all(engine)
# 2. Create the inspector object
# inspector = inspect(engine)

# # 3. Get all table names
# table_names = inspector.get_table_names()
# print(table_names)
