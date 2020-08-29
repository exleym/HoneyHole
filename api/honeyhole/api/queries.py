import logging
from sqlalchemy import asc
from typing import List
from ..extensions import db
from .. errors import MissingResourceException


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ModelType = type(db.Model)


def persist_resource(data: dict, model: ModelType) -> db.Model:
    obj = model(**data)
    db.session.add(obj)
    db.session.commit()
    return obj


def create_resource(model: ModelType, **kwargs) -> db.Model:
    persist_resource(kwargs, model)


def list_resources(model: ModelType, **kwargs) -> List[db.Model]:
    q = model.query
    limit = kwargs.pop("limit", None)
    offset = kwargs.pop("offset", None)
    order_by = kwargs.pop("order_by", None)
    for k, v in kwargs.items():
        if v:
            q = q.filter_by(**{k: v})
    if not order_by:
        order_by = model.id
    q = q.order_by(asc(order_by))
    if limit:
        q = q.limit(limit)
    if offset:
        q = q.offset(offset)
    return q.all()


def get_resource(id: int, model: ModelType) -> db.Model:
    obj = model.query.filter_by(id=id).first()
    if not obj:
        logger.error(f"error looking up {model.__name__} with id={id}")
        msg = f"No {model.__name__} with id={id}"
        raise MissingResourceException(msg)
    return obj


def search(filters: List[dict], model: ModelType) -> List[db.Model]:
    return []


def edit_resource(id: int, data: dict, model: ModelType) -> db.Model:
    obj = get_resource(id=id, model=model)
    _ = data.pop("id", None)
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.add(obj)
    db.session.commit()
    return obj


def remove_resource_by_id(id: int, model: ModelType):
    obj = get_resource(id=id, model=model)
    db.session.delete(obj)
    db.session.commit()
