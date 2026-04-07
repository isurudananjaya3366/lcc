# File Storage API Integration

> Patterns for integrating the storage module with Django REST Framework
> views and serializers.

---

## Upload Endpoint Pattern

```python
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.core.storage import (
    handle_image_upload,
    get_image_validator,
    product_path,
)


class ProductImageUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, product_id):
        file = request.FILES["image"]

        # 1. Validate
        validator = get_image_validator()
        validator.validate_all(file)

        # 2. Process (auto sync/async based on size)
        processed = handle_image_upload(file, instance=product)

        # 3. Save via model
        product.image.save(
            product_path(product, file.name),
            processed,
        )

        return Response({"url": product.image.url}, status=201)
```

---

## Serializer Validation

```python
from rest_framework import serializers
from apps.core.storage import get_image_validator, get_document_validator


class ProductImageSerializer(serializers.Serializer):
    image = serializers.ImageField(validators=[get_image_validator()])


class InvoiceSerializer(serializers.Serializer):
    attachment = serializers.FileField(validators=[get_document_validator()])
```

---

## Signed URL in Serializers

```python
from apps.core.storage import generate_signed_url


class InvoiceDetailSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ["id", "number", "download_url"]

    def get_download_url(self, obj):
        if obj.attachment:
            return generate_signed_url(obj.attachment.name, expiry=7200)
        return None
```

---

## Bulk Download

```python
from apps.core.storage import generate_bulk_signed_urls


class InvoiceBulkDownloadView(APIView):
    def post(self, request):
        invoice_ids = request.data.get("ids", [])
        invoices = Invoice.objects.filter(id__in=invoice_ids)

        paths = [inv.attachment.name for inv in invoices if inv.attachment]
        urls = generate_bulk_signed_urls(paths, expiry=3600)

        return Response(urls)
```

---

## Thumbnail Retrieval

```python
class ProductListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "thumbnail"]

    def get_thumbnail(self, obj):
        if obj.image:
            thumb_path = obj.image.name.replace(
                "products/", "thumbs/small/"
            )
            return self.context["request"].build_absolute_uri(
                f"/media/{thumb_path}"
            )
        return None
```

---

## See Also

- [Storage Overview](overview.md) – architecture, quick start
- [Configuration Guide](configuration.md) – all settings reference
- [Performance & Tuning](performance.md) – async processing, CDN
