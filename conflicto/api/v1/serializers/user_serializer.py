from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from conflicto.models import UserProfile, FBProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['fcm_token', 'uuid', 'firebase_id']


class FBProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FBProfile
        fields = ['first_name', 'last_name', 'fb_link', 'name', 'dp_link', 'uuid']


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(required=False)
    fbprofile = FBProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['userprofile', 'fbprofile']

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create(username=validated_data['userprofile']['firebase_id'],
                                       is_staff=True, is_superuser=False
                                       )
            user.userprofile = UserProfile.objects.create(fcm_token=validated_data['userprofile']['fcm_token'],
                                                          firebase_id=validated_data['userprofile']['firebase_id'],
                                                          user=user)
            user.fbprofile = FBProfile.objects.create(token=validated_data.get('fbprofile',{}).get('fb_token', None),
                                                      user=user, uuid=user.userprofile.uuid)
            # TODO: Populate data from fb api
            return user

    def update(self, instance, validated_data):
        instance.userprofile.fcm_token = validated_data['userprofile'].get('fcm_token', instance.userprofile.fcm_token)
        instance.userprofile.firebase_id = validated_data['userprofile'].get('firebase_id',
                                                                             instance.userprofile.firebase_id)
        instance.userprofile.save()
        return instance


class UserPostSerializer(serializers.ModelSerializer):

    fbprofile = FBProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['fbprofile']