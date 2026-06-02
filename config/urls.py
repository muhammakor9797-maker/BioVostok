from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from goods.views import index, catalog, product_detail, sitemap_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('cart/', include('carts.urls')),
    path('orders/', include('orders.urls')),
    path('sitemap.xml', sitemap_view, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('', index, name='home'),
    path('catalog/', catalog, name='catalog'),
    path('product/<slug:product_slug>/', product_detail, name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)