"""URL routing for the attributes app API."""

from rest_framework.routers import DefaultRouter

from .views import AttributeGroupViewSet, AttributeOptionViewSet, AttributeViewSet

app_name = "attributes"

router = DefaultRouter()
router.register("attribute-groups", AttributeGroupViewSet, basename="attributegroup")
router.register("attributes", AttributeViewSet, basename="attribute")
router.register("attribute-options", AttributeOptionViewSet, basename="attributeoption")

urlpatterns = router.urls
