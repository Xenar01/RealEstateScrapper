from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config.yaml'
Base = declarative_base()


class Site(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    url = Column(String)
    listings = relationship('Listing', back_populates='site')


class Listing(Base):
    __tablename__ = 'listings'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    title = Column(String)
    price = Column(String)
    description = Column(Text)
    location = Column(String)
    phone = Column(String)
    site = relationship('Site', back_populates='listings')
    images = relationship('Image', back_populates='listing')


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey('listings.id'))
    path = Column(String)
    listing = relationship('Listing', back_populates='images')


def get_engine():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    return create_engine(cfg['database']['url'])


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
