from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from . forms import *
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render,redirect
from .forms import ImageForm
from django.http import HttpResponse
from .models import CapturedImage
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from django.conf import settings
import requests
from .models import Product
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model





saved_model_path = os.path.join(settings.BASE_DIR, 'models', 'cnn_practice1_model.h5')
model = load_model(saved_model_path)

IMAGE_WIDTH, IMAGE_HEIGHT = 100, 100
class_names = ['acne', 'dark circles', 'white spots']





# Create your views here.

def home(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items'] 

    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    
    return render(request, 'store/home.html', context)

def about(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items'] 

    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    
    return render(request, 'store/about.html', context)



def register(request):
	data = cartData(request)
	cartItems = data['cartItems']
	if request.user.is_authenticated:
		return redirect("home")
	if request.method == "POST":
		form = UserRegistrationForm(request.POST, request.FILES)
		if form.is_valid():
			user = form.save()
			first_name = form.cleaned_data.get('first_name')
			email = form.cleaned_data.get('email')
			customer, created = Customer.objects.get_or_create(
				user=user,
				defaults={'name': first_name, 'email': email}
				)
			login(request, user)

			username = form.cleaned_data.get('username')
			messages.success(request, f'Hi {username} your account has been created')
			return redirect('home')
	else:
		form = UserRegistrationForm()
	context = {'form':form,'cartItems':cartItems,}
	return render(request, 'store/register.html', context)



class CustomLoginView(LoginView):
    template_name = 'store/login.html'

    def form_valid(self, form):
        # Perform the standard login process
        response = super().form_valid(form)

        # Merge carts after successful login
        cartData(self.request)

        # Delete the cart cookie
        response.delete_cookie('cart')

        return response




def profile(request):
    if request.user.is_authenticated:
        data = cartData(request)
        cartItems = data['cartItems']
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer)
        reviews = Review.objects.filter(customer=customer)
        if request.method == 'POST':
            review_id = request.POST.get('review_id')
            review = Review.objects.get(id=review_id)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('profile')  # Redirect to the profile page after saving


        orders_with_items = []

        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            items_with_products = [
                {"item": item, "product_name": item.product.name if item.product else "No Product"}
                for item in order_items
            ]
            orders_with_items.append({
                "order": order,
                "items": items_with_products
            })

        print(orders_with_items)
        context = {"cartItems": cartItems, "orders_with_items":orders_with_items, "reviews":reviews,"customer":customer,}
    else:
        return redirect("login")
    return render(request, 'store/profile.html', context)












def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    category = Category.objects.all()
    products = Product.objects.all()
    ordered_product_ids = []
    if request.user.is_authenticated:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete=True)
        ordered_product_ids = OrderItem.objects.filter(order__in=orders).values_list('product_id', flat=True)
    context = {'products':products,'cartItems':cartItems,'category':category,'ordered_product_ids':ordered_product_ids}
    return render(request, 'store/store.html', context)

def suggested_products(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    if request.user.is_authenticated:
        customer = request.user.customer
        skin_type = customer.predicted_skin_type
        products = Product.objects.filter(description=skin_type)
        orders = Order.objects.filter(customer=customer, complete=True)
        ordered_product_ids = OrderItem.objects.filter(order__in=orders).values_list('product_id', flat=True)
    else:
        return redirect("capture-image")
    
    context = {'products':products,'cartItems':cartItems,'skin_type':skin_type,'ordered_product_ids':ordered_product_ids}
    return render(request, 'store/Suggested_products.html', context)

	

def storeCat(request,id=None):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    category = Category.objects.all()
    products = Product.objects.filter(category=id)
    ordered_product_ids = []
    if request.user.is_authenticated:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete=True)
        ordered_product_ids = OrderItem.objects.filter(order__in=orders).values_list('product_id', flat=True)
    context = {'products':products,'cartItems':cartItems,'category':category,'ordered_product_ids':ordered_product_ids}
    return render(request, 'store/store.html', context)




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']   
    ordered = False
    if request.user.is_authenticated:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete=True)
        ordered = OrderItem.objects.filter(order__in=orders, product=product).exists()

    context = {
        'product': product,
        'reviews': reviews,
        'ordered': ordered,
        'cartItems':cartItems,
        'order':order,
        'items':items,
    }
    return render(request, 'store/product_detail.html', context)





def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']    
        
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    message = "Please Login or register to proceed further"
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'message': message}

    if request.user.is_authenticated:
        return render(request, 'store/checkout.html', context)
    else:
        return HttpResponseRedirect(reverse('login') + '?next=' + reverse('checkout'))




def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id
	if total == order.get_cart_total:
		order.complete = True 
	order.save()

	
	ShippingAddress.objects.create(
	customer=customer,
	order=order,
	address=data['shipping']['address'],
	city=data['shipping']['city'],
	state=data['shipping']['state'],
	zipcode=data['shipping']['zipcode'],
	)

	return JsonResponse('Payment submitted..', safe=False)



def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    
    
    # Assuming the customer is logged in
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=True, orderitem__product=product).first()
        print(order)
        if order:
            if request.method == 'POST':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.product = product
                    review.customer = customer
                    review.order = order
                    review.save()
                    return redirect('home')
            else:
                form = ReviewForm()
                
            return render(request, 'store/submit_review.html', {'form': form, 'product': product, 'order': order})
        else:
            # The customer hasn't bought this product
            return redirect('home')  # or display a message informing them they can't review this product
    else:
        # The customer is not logged in
        return redirect('login')  # Redirect to the login page or handle as needed



# @login_required
def search_product(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            data = json.loads(request.body)
            product_name = data.get('product_name')
            print(product_name)
            try:
                product = Product.objects.get(name__iexact=product_name)
                product_id = product.id
                return JsonResponse({'success': True, 'product_id': product_id})
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Product not found.'})
        else:
            return render(request,'store/base.html')
            # return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    else:
         return redirect('home')





# @login_required
def summarize_reviews(request, product_id):
    if request.user.is_superuser:
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZmNjOWYzMmUtMDNmNC00ZDkyLWExOTQtMDI5ZjI0OTFlNzc3IiwidHlwZSI6ImFwaV90b2tlbiJ9.x0BgY13sdcx0E5a059PCen7RqjjiOsHe5OBazuQUSuI"}  # Replace with your actual API key
        url = "https://api.edenai.run/v2/text/summarize"
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        reviews = Review.objects.filter(product_id=product_id)  # Filter reviews by product ID
        review_texts = [review.comment for review in reviews if review.comment]  # Extract review texts

        if not review_texts:
            # return render(request, 'no_reviews.html', {'message': 'No reviews found for this product.'})
            return HttpResponse("no reviews availble")

        payload = {
            "providers": "anthropic",
            "language": "en",
            "text":"\n".join(review_texts),  # Concatenate all review texts with newlines
            "fallback_providers": "nlpcloud"
        }


        texting = "\n".join(review_texts)
        print(texting)

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            result = json.loads(response.text)
            summary = result['anthropic']['result']  # Extract summary from Microsoft provider
            
            context = {'summary':summary,'text':texting,'product_name':product_name}
            print(summary)
            return render(request, 'store/summary.html', context)
        except requests.exceptions.RequestException as e:
            # Handle API request errors gracefully (e.g., log the error)
            return HttpResponse("error fatching summary")
            # return render(request, 'error.html', {'message': 'Error fetching summary.'})
    else:
         return redirect("home")






















def suggest(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items'] 
    if request.method == 'POST':
          skin_type = request.POST.get('skin_type')
          
    products = Product.objects.filter(description=skin_type)  # Filter products based on description
    context = {'products': products,'skin_type':skin_type,'cartItems':cartItems}
    return render(request, 'store/suggest.html', context)


def capture_image(request):
    
	
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items'] 
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()  # Save the image to the database
            request.session['captured_image_id'] = image_instance.id  # Store image ID in session
            return redirect('decision_page')  # Redirect to decision page
    else:
        form = ImageForm()
        

    context = {'form':form,'cartItems':cartItems}
    return render(request, 'store/capture-image.html', context)




def decision_page(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    return render(request, 'store/decision_page.html',{'cartItems':cartItems})





def prediction_page(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    captured_image_id = request.session.get('captured_image_id')
    if captured_image_id:
        image_instance = CapturedImage.objects.get(id=captured_image_id)
        img_path = image_instance.image.path

        try:
            img = image.load_img(img_path, target_size=(IMAGE_WIDTH, IMAGE_HEIGHT))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.  # Rescale pixel values to [0, 1]

            prediction = model.predict(img_array)
            predicted_class_index = np.argmax(prediction)
            predicted_class = class_names[predicted_class_index]
            confidence = prediction[0][predicted_class_index]

            if request.user.is_authenticated:
                  customer = request.user.customer
                  customer.predicted_skin_type = predicted_class
                  customer.save()

            return render(request, 'store/prediction_page.html', {
                'image_instance': image_instance,
                'predicted_class': predicted_class,
                'confidence': confidence,
                'cartItems':cartItems,
            })
        except Exception as e:
            return HttpResponse("Error: " + str(e))
    else:
        return HttpResponse("No captured image found.")


