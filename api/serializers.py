from rest_framework import serializers


class ContactFormSerializer(serializers.Serializer):
    """Serializer for contact form submissions."""
    name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    company = serializers.CharField(max_length=100, required=False, allow_blank=True)
    message = serializers.CharField(max_length=2000, required=True)
    
    def validate_name(self, value):
        return value.strip()
    
    def validate_email(self, value):
        return value.strip().lower()


class NewsletterSerializer(serializers.Serializer):
    """Serializer for newsletter signup."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        return value.strip().lower()
