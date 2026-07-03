from flask_jwt_extended import JWTManager
from app.db.model import User
from app.db.session import get_db
from app.authen.jwt_blocklist import BLACKLIST

jwt = JWTManager()


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data["sub"]
    db = get_db()
    return db.get(User, user_id)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(_jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST
