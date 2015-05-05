from enum import Enum


class Permissions(Enum):
    PUBLIC = 'public'
    VIEW = 'view'
    EDIT = 'edit'
    CREATE = 'create'
    DELETE = 'delete'
