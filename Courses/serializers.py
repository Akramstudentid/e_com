from decimal import Decimal

from rest_framework import serializers

from .models import Course, Offer, Order, Category

class LoginSerializer(serializers.Serializer):
    """Serializer for user login with username and password"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'keywords', 'type']

class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_price = serializers.SerializerMethodField()
    offer_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    images = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'docs', 'mrp', 'offer', 'stock',
            'available', 'category', 'category_name', 'video_url', 'thumbnail',
            'images', 'offer_price', 'final_price'
        ]
        read_only_fields = ['id', 'final_price', 'category_name']

    def get_final_price(self, obj):
        return obj.offer_price

    def validate_docs(self, value):
        if value and not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Documents must be a PDF file")
        return value

    def validate_thumbnail(self, value):
        if value and not value.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError("Thumbnail must be an image (png, jpg, jpeg)")
        return value

    def _apply_offer_price(self, validated_data):
        offer_price = validated_data.pop('offer_price', None)
        mrp = validated_data.get('mrp')

        if offer_price is not None and mrp and Decimal(mrp) > 0:
            offer_price = Decimal(offer_price)
            mrp = Decimal(mrp)
            discount = (((mrp - offer_price) / mrp) * Decimal('100')).quantize(Decimal('0.01'))
            validated_data['offer'] = max(Decimal('0'), min(discount, Decimal('100')))

        return validated_data

    def create(self, validated_data):
        category_data = validated_data.pop('category', None) or {
            'name': 'Uncategorized',
            'keywords': '',
            'type': '',
        }
        images_data = validated_data.pop('images', [])
        validated_data = self._apply_offer_price(validated_data)

        category_obj, _ = Category.objects.get_or_create(
            name=category_data.get('name'),
            defaults={
                'keywords': category_data.get('keywords', ''),
                'type': category_data.get('type', '')
            }
        )

        course = Course.objects.create(category=category_obj, images=images_data, **validated_data)
        return course

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        validated_data.pop('images', None)
        validated_data = self._apply_offer_price(validated_data)

        if category_data:
            category_obj, _ = Category.objects.get_or_create(
                name=category_data.get('name'),
                defaults={
                    'keywords': category_data.get('keywords', ''),
                    'type': category_data.get('type', '')
                }
            )
            instance.category = category_obj

        return super().update(instance, validated_data)
        
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'course', 'quantity', 'total_price', 'created_at']

class PlaceOrderSerializer(serializers.Serializer):
    """Serializer for placing an order from cart"""
    coupon_code = serializers.CharField(required=False, allow_blank=True)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
