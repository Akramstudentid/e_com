from rest_framework import serializers
from .models import Course, Offer, Order,Category
from rest_framework import serializers
from .models import Course, Category



from rest_framework import serializers
from .models import Course, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'keywords', 'type']

class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    class Meta:
        model = Course
        fields = [
            'name', 'description', 'docs', 'mrp', 'offer', 'stock',
            'available', 'category', 'video_url', 'thumbnail', 'images', 'offer_price'
        ]

    def validate_docs(self, value):
        if value and not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Documents must be a PDF file")
        return value

    def validate_thumbnail(self, value):
        if value and not value.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError("Thumbnail must be an image (png, jpg, jpeg)")
        return value

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        images_data = validated_data.pop('images', [])

        category_obj, _ = Category.objects.get_or_create(
            name=category_data.get('name'),
            defaults={
                'keywords': category_data.get('keywords', ''),
                'type': category_data.get('type', '')
            }
        )

        course = Course.objects.create(category=category_obj, images=images_data, **validated_data)
        return course
        
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'course', 'quantity', 'total_price', 'created_at']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)