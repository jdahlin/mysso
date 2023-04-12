from sqlalchemy.orm import Session

from sso.models.user import User


def test_get_user(session: Session) -> None:
    user = session.query(User).filter_by(email="bob@example.com").one()
    assert user.email == "bob@example.com"
