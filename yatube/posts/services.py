from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .models import Like

User = get_user_model()


def add_like(obj, user):
    """
    Добавляет лайк объекту от пользователя.

    :param obj: Объект, которому ставится лайк.
    :param user: Пользователь, который ставит лайк.
    """
    obj_type = ContentType.objects.get_for_model(obj)
    like, is_created = Like.objects.get_or_create(
        content_type=obj_type,
        object_id=obj.id,
        user=user,
    )
    return like


def remove_like(obj, user):
    """
    Удаляет лайк объекту от пользователя.

    :param obj: Объект, у которого удаляется лайк.
    :param user: Пользователь, который удаляет свой лайк.
    """
    obj_type = ContentType.objects.get_for_model(obj)
    Like.objects.filter(
        content_type=obj_type,
        object_id=obj.id,
        user=user,
    ).delete()


def is_liked(obj, user) -> bool:
    """
    Показывает, лайкнул ли пользователь объект.

    :param obj: Объект, у которого проверяется наличие лайка пользователя.
    :param user: Пользователь, наличие лайка которого проверяется.
    """
    if not user.is_authenticated:
        return False

    obj_type = ContentType.objects.get_for_model(obj)
    likes = Like.objects.filter(
        content_type=obj_type,
        object_id=obj.id,
        user=user,
    )
    return likes.exists()


def get_likes(obj):
    """
    Получает пользователей, которые лайкнули данный объект.

    :param obj: Объект, для которого получает лайкнувших пользователей.
    """
    obj_type = ContentType.objects.get_for_model(obj)
    return User.objects.filter(
        likes__content_type=obj_type,
        likes__object_id=obj.id,
    )
