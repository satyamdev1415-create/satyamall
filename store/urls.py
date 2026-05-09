from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='root'),   
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),  #
    path('logout/', views.user_logout, name='logout'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),

    path('update/<int:id>/<str:action>/', views.update_cart, name='update_cart'),

    path('checkout/',views.checkout,name='checkout'),

    path('success/',views.order_success,name="success"),

    path('wishlist/<int:id>/',views.add_to_wishlist,name="wishlist")
]