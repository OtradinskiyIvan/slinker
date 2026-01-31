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
            logger.info(f"Link already exists: {existing_link.short_link} -> {real_link}")
            return existing_link.short_link

        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            short_link = random_alfanum(5)

            existing_short = self.db.query(Link).filter(
                Link.short_link == short_link
            ).first()

            if not existing_short:
                try:
                    db_link = Link(
                        real_link=real_link,
                        short_link=short_link
                    )
                    self.db.add(db_link)
                    self.db.commit()
                    self.db.refresh(db_link)
                    logger.info(f"Created new link: {short_link} -> {real_link}")
                    return short_link
                except IntegrityError:
                    self.db.rollback()
                    logger.warning(f"Collision for short link: {short_link}")
                    attempts += 1
            else:
                attempts += 1

        short_link = random_alfanum(8)
        db_link = Link(real_link=real_link, short_link=short_link)
        self.db.add(db_link)
        self.db.commit()
        self.db.refresh(db_link)
        logger.info(f"Created link with longer hash: {short_link} -> {real_link}")
        return short_link

    def get_real_link(self, short_link: str) -> str | None:
        link = self.db.query(Link).filter(
            Link.short_link == short_link
        ).first()

        if link: return link.real_link
        return None

    def log_usage(self, link_id: int, user_ip: str, user_agent: str) -> None:
        usage = Usage(
            link_id=link_id,
            user_ip=user_ip,
            user_agent=user_agent
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
        ).order_by(Usage.accessed_at.desc()).all()



"""from utils.utils_random import random_alfanum


class LinkService:
    def __init__(self) -> None:
        self.short_link_to_real_link: dict[str, str] = {}

    def create_link(self, link: str) -> str:
        short_link = random_alfanum(5)
        self.short_link_to_real_link[short_link] = link

        return short_link

    def get_real_link(self, link: str) -> str | None:
        return self.short_link_to_real_link.get(link)
"""