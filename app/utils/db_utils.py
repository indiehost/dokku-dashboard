from typing import Optional

from models import Test
from sqlmodel import select, Session


def create_test(db: Session, name: str, description: Optional[str] = None) -> Test:
    """
    Create a new Test item in the database
    """
    test = Test(name=name, description=description)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


def delete_test(db: Session, test_id: int):
    """
    Delete a Test item by its ID
    """
    statement = select(Test).where(Test.id == test_id)
    db.delete(db.exec(statement).first())
    db.commit()
