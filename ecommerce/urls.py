from django.urls import path
from . import views

app_name = "get_your_goods"

urlpatterns = [
     path("", views.login_user, name="home"),
     path("register/", views.register_user, name="register"),
     path("login/", views.login_user, name="login"),
     path("logout/", views.logout_user, name="logout"),
     path("welcome/", views.welcome, name="welcome"),
     path("stores/", views.view_stores, name="view_stores"),
     path("stores/create/", views.create_store, name="create_store"),
     path("stores/edit/<int:store_id>/", views.edit_store, name="edit_store"),
     path("stores/delete/<int:store_id>/", views.delete_store,
          name="delete_store"),
     path("products/create/", views.create_product, name="create_product"),
     path("products/", views.view_products, name="view_products"),
     path("products/edit/<int:product_id>/", views.edit_product,
          name="edit_product"),
     path("products/delete/<int:product_id>/", views.delete_product,
          name="delete_product"),
     path("stores/<int:store_id>/", views.store_detail,
          name="store_detail"),
     path("products/browse/", views.browse_products,
          name="browse_products"),
     path("cart/add/<int:product_id>/", views.add_to_cart,
          name="add_to_cart"),
     path("cart/", views.view_cart, name="view_cart"),
     path("cart/increase/<int:product_id>/", views.increase_quantity,
          name="increase_quantity",),
     path("cart/decrease/<int:product_id>/", views.decrease_quantity,
          name="decrease_quantity"),
     path("cart/remove/<int:product_id>/", views.remove_from_cart,
          name="remove_from_cart"),
     path("checkout/", views.checkout, name="checkout"),
     path("review/<int:product_id>/", views.leave_review,
          name="leave_review"),
     path("product/<int:product_id>/", views.product_detail,
          name="product_detail"),
     path("my_reviews/", views.my_reviews, name="my_reviews"),
     path("forgot_password/", views.forgot_password,
          name="forgot_password"),
     path("reset_password/<str:token>/", views.reset_password,
          name="reset_password"),

     # REST API URLs

     path("api/stores/add/", views.add_store, name="api_add_store"),
     path("api/products/add/", views.add_product, name="api_add_product"),
     path("api/products/<int:product_id>/reviews/", views.get_reviews,
          name="api_get_reviews"),
     path("api/vendors/<int:vendor_id>/stores/", views.get_vendor_stores,
          name="api_vendor_stores"),
     path("api/stores/<int:store_id>/products/", views.get_store_products,
          name="api_store_products"),

     # Reddit URL
     path("reddit/", views.reddit_feed, name="reddit_feed"),
]
