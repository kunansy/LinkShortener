import datetime
import hashlib
import os
import sys
from contextlib import contextmanager
from typing import ContextManager, Any, Optional, Iterable

from sqlalchemy import (
    Column, Integer,
    String, Date, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


Base = declarative_base()
SHORTENER_URL = "https://short.ru/{}"


class Link(Base):
    __tablename__ = 'link'

    link_id = Column(Integer, primary_key=True)
    long_link = Column(String, nullable=False, unique=True)
    short_link = Column(String, nullable=False, unique=True)
    created_at = Column(Date, nullable=False)

    def _as_dict(self) -> dict[str, Any]:
        return {
            'link_id': self.link_id,
            'long_link': self.long_link,
            'short_link': self.short_link,
            'created_at': self.created_at
        }

    def json(self,
             exclude: Iterable[str] = None) -> dict[str, Any]:
        exclude = exclude or ()

        return {
            key: value
            for key, value in self._as_dict()
            if key not in exclude
        }


engine = create_engine(os.getenv('DB_URI'), encoding='utf-8')
Base.metadata.create_all(engine)


def _hash_link(long_link: str) -> str:
    return hashlib.sha256(long_link.encode('utf-8')).hexdigest()[:4:-4]


def _short_link(long_link: str) -> str:
    return SHORTENER_URL.format(_hash_link(long_link))


def today() -> datetime.date:
    return datetime.date.today()


@contextmanager
def session(**kwargs) -> ContextManager[Session]:
    new_session = Session(**kwargs, expire_on_commit=False, bind=engine)
    try:
        yield new_session
        new_session.commit()
    except Exception as e:
        print(e, file=sys.stderr)
        new_session.rollback()
    finally:
        new_session.close()


def short_link(*,
               long_link: str) -> Link:
    short_link = _short_link(long_link)

    with session() as ses:
        link = Link(
            short_link=short_link,
            long_link=long_link,
            created_at=today(),
        )
        ses.add(link)
        # to get link_id
        ses.commit()

        return link


def find_short_link(*,
                    long_link: str) -> Optional[Link]:
    with session() as ses:
        link = ses.query(Link)\
            .filter_by(long_link=long_link)

        return link.first()


def get_link(*,
             link_id: int) -> Optional[Link]:
    with session() as ses:
        return ses.query(Link).get(link_id)


def delete_link(*,
                link_id: int) -> Link:
    with session() as ses:
        link = get_link(link_id=link_id)
        ses.delete(link)

        return link
