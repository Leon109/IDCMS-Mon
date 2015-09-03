from flask import Blueprint

cmdb = Blueprint('cmdb', __name__)

from . import views
from .sales import views
#from .client import views
#from .site import views
#from .rack import views
#from .ipsubnet import views
#from .ippool import views
#from .cabinet import views
#from .record import views
#from .statistics import views

from ..utils.permission import Permission

@cmdb.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
