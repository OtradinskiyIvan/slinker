from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from infrastructure.models import Link, Usage
from utils.utils_random import random_alfanum
import logging

logger = logging.getLogger(__name__)


class LinkService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_link(self, real_link: str) -> str:

        existing_link = self.db.query(Link).filter(
            Link.real_link == real_link
        ).first()

        if existing_link:
            return existing_link.short_link

        short_link = random_alfanum(5)

        try:
            db_link = Link(
                real_link=real_link,
                short_link=short_link
            )
            self.db.add(db_link)
            self.db.commit()
            self.db.refresh(db_link)
            return short_link

        except IntegrityError:
            self.db.rollback()
            raise

    def get_real_link(self, short_link: str) -> str | None:
        link = self.db.query(Link).filter(
            Link.short_link == short_link
        ).first()

        if link: return link.real_link
        return None

    def log_usage(
            self, link_id: int, user_ip: str,
            user_agent: str, usage_count: int
    ) -> None:
        usage = Usage(
            link_id=link_id,
            user_ip=user_ip,
            user_agent=user_agent,
            count=usage_count
        )
        self.db.add(usage)
        self.db.commit()

    def get_link_by_short(self, short_link: str) -> Link | None:
        return self.db.query(Link).filter(
            Link.short_link == short_link
        ).first()

    def get_link_usage(self, link_id: int) -> list[Usage]:
        return self.db.query(Usage).filter(
            Usage.link_id == link_id
        ).order_by(Usage.id.desc()).all()

    def get_link_usage_count(self, link_id) -> int:
        result = self.db.query(Usage.count).filter(
            Usage.link_id == link_id
        ).scalar()
        logger.debug('cnt res: {}', result)
        return result if result is not None else 0