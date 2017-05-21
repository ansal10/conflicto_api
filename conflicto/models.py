# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models


# Create your models here.

def generate_uuid():
    return uuid.uuid4().__str__()


class Actions():
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'
    SUPPORT = 'SUPPORT'
    CONFLICT = 'CONFLICT'
    ENDORSE = 'ENDORSE'
    REPORT = 'REPORT'


class Objects():
    POST = 'POST'
    COMMENT = 'COMMENT'



class UserProfile(models.Model):
    uuid = models.CharField(max_length=63, null=False, default=generate_uuid, db_index=True, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=255, null=True)
    firebase_id = models.CharField(max_length=255, null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class FBProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    fb_link = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    dp_link = models.CharField(max_length=255, null=True)
    cover_link = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=10, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class Post(models.Model):
    uuid = models.CharField(max_length=63, null=False, default=generate_uuid, db_index=True, unique=True)
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    category = models.CharField(max_length=255, null=True, db_index=True)
    tags = JSONField(default=[])
    shared_post = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # counts of likes/dislikes/supporters
    reports = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    endorse = models.IntegerField(default=0)
    supports = models.IntegerField(default=0)
    conflicts = models.IntegerField(default=0)

    #foreign key
    user = models.ForeignKey(User, null=False, db_index=True)




class Comment(models.Model):

    ACTIONS_CHOICES = (
        (Actions.SUPPORT, Actions.SUPPORT),
        (Actions.CONFLICT, Actions.CONFLICT),
        (Actions.REPORT, Actions.REPORT),
    )

    uuid = models.CharField(max_length=63, null=False, default=generate_uuid, db_index=True, unique=True)
    post_uuid = models.CharField(max_length=63, null=False)
    comment = models.TextField(null=False)
    type = models.CharField(max_length=255, choices=ACTIONS_CHOICES)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # counts of like and dislikes...
    reports = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    endorse = models.IntegerField(default=0)

    #foreign keys
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post, related_name='comments')


class Reaction(models.Model):

    ACTIONS_CHOICES = (
        (Actions.LIKE, Actions.LIKE),
        (Actions.DISLIKE, Actions.DISLIKE),
        (Actions.SUPPORT, Actions.SUPPORT),
        (Actions.CONFLICT, Actions.CONFLICT),
        (Actions.REPORT, Actions.REPORT),
        (Actions.ENDORSE, Actions.ENDORSE)
    )

    OBJECT_TYPE_CHOICES = (
        (Objects.POST, Objects.POST),
        (Objects.COMMENT, Objects.COMMENT)
    )

    object_uuid = models.CharField(max_length=63, null=False, db_index=True)
    user = models.ForeignKey(User, null=False, db_index=True)
    actions = JSONField(max_length=255, null=False, default=[])
    object_type = models.CharField(max_length=255, null=False, choices=OBJECT_TYPE_CHOICES, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['object_uuid', 'object_type', 'user_id'])
        ]

    @staticmethod
    def user_reactions(user_id, object_uuids, object_type):
        uuids = object_uuids if hasattr(object_uuids, '__iter__') else [object_uuids]
        reactions = Reaction.objects.values('actions', 'object_uuid').filter(user_id=user_id, object_uuid__in=uuids, object_type=object_type)

        reaction_dict = {}
        for reaction in reactions:
            reaction_dict[reaction['object_uuid']] = reaction['actions']

        if hasattr(object_uuids, '__iter__'):
            return reaction_dict
        else:
            return reaction_dict[object_uuids]



