from rest_framework import serializers
import re


class TenantLookupSerializer(serializers.Serializer):
    """Serializer for tenant/subdomain lookup."""
    domain = serializers.CharField(max_length=255, required=True)
    
    def validate_domain(self, value):
        """Validate domain format."""
        value = value.strip().lower()
        # Remove protocol if present
        value = re.sub(r'^https?://', '', value)
        # Remove trailing slash
        value = value.rstrip('/')
        
        # Validate domain format
        domain_regex = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$'
        if not re.match(domain_regex, value):
            raise serializers.ValidationError("Please enter a valid domain (e.g., yourcompany.com)")
        
        return value


class SignInRequestSerializer(serializers.Serializer):
    """Serializer for sign-in request (magic link)."""
    email = serializers.EmailField(required=True)
    domain = serializers.CharField(max_length=255, required=True)
    use_shared_instance = serializers.BooleanField(default=False)
    
    def validate_email(self, value):
        """Validate and normalize email."""
        return value.strip().lower()
    
    def validate_domain(self, value):
        """Validate domain."""
        return value.strip().lower()


class VerifyMagicLinkSerializer(serializers.Serializer):
    """Serializer for magic link verification."""
    token = serializers.CharField(required=True)


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
