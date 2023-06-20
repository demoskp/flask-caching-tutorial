from flask import request
from flask_restful import Resource

from api.schemas.user import UserSchema, RoleSchema
from constants import ONE_WEEK
from extensions import db, cache
from models import User
from models.users import Role


class UserList(Resource):
    def get(self):
        users = User.query.all()
        schema = UserSchema(many=True)
        return {"results": schema.dump(users)}

    def post(self):
        schema = UserSchema()
        validated_data = schema.load(request.json)

        user = User(**validated_data)
        db.session.add(user)
        db.session.commit()

        return {"msg": "User created", "user": schema.dump(user)}


class UserResource(Resource):
    def get(self, user_id):
        user = cache.get(f"user_id_{user_id}")
        if user is None:
            user = User.query.get_or_404(user_id)
            cache.set(f"user_id_{user_id}", user)
        schema = UserSchema()

        return {"user": schema.dump(user)}

    def put(self, user_id):
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        user = schema.load(request.json, instance=user)

        db.session.add(user)
        db.session.commit()

        return {"msg": "User updated", "user": schema.dump(user)}

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return {"msg": "User deleted"}


class RoleList(Resource):
    @cache.cached(ONE_WEEK, key_prefix="user_roles")
    def get(self):
        roles = Role.query.all()
        schema = RoleSchema(many=True)
        return {"results": schema.dump(roles)}
