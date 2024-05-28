from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth import views as auth_view

urlpatterns = [
    
    # Home Page
    path('', views.home, name="home"),
	path('about/',views.about, name="about"),
    
    # Store-related URLs
    path('store/', views.store, name="store"),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('storeCat/', views.storeCat, name="storeCat"),
	path('storeCat/<int:id>/', views.storeCat, name="storeCat"),
    
    
    # Authentication URLs
    path('register/', views.register, name="register"),
    path('login/', CustomLoginView.as_view(), name="login"),
	path('logout/', auth_view.LogoutView.as_view(next_page='home'), name="logout"),
    
    
    # User profile and reviews
    path('profile/',views.profile, name='profile'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    
    
    # Image capture and prediction
    path('suggest/', views.suggest, name="suggest"),
    path('capture-image/',views.capture_image,name='capture-image'),
    path('decision/', views.decision_page, name='decision_page'),
    path('prediction_page/',views.prediction_page, name='prediction_page'),
    path('suggested-products/',views.suggested_products, name='suggested-products'),
    

    # Review summarization and product search
    path('summary/<int:product_id>/', views.summarize_reviews, name='summary'),
    path('search/product/', views.search_product, name='search_product'),
]