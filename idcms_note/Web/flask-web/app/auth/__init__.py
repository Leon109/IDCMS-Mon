#coding=utf-8

from flask import Blueprint
auth = Blueprint('auth', __name__)

from . import views, errors
from app.utils.permission import Permission

@auth.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
