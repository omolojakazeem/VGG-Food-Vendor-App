from rest_framework import serializers

from .models import Menu


class MenuListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class MenuUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['name','description', 'price', 'menu_cat']


class MenuCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

        read_only_fields = ['vendor_id',]
