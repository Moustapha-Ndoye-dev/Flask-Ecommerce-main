from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Category, OneOrder, Product, Cart, product_category
from flask_login import login_required, current_user
from . import db
from intasend import APIService
import requests

views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'ISPubKey_test_d9102635-51b4-4cd9-92a1-4f1d9d235b76'
API_TOKEN = 'ISSecretKey_test_13676ec8-d545-4dc9-878e-cb11369d936e'

@views.route('/')
def home():
    category_id = request.args.get('category_id')  # Récupère l'ID de la catégorie depuis l'URL
    categories = Category.query.all()
    
    if category_id:
        # Requête pour récupérer les produits de la catégorie spécifiée
        items = Product.query.join(product_category).filter(product_category.c.category_id == category_id).all()
    else:
        items = Product.query.all()

    cart_items = Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []

    return render_template('home.html', items=items, categories=categories, cart=cart_items)

@views.route('/category/<int:category_id>')
def show_category_products(category_id):
    category = Category.query.get(category_id)
    if category:
        products = Product.query.filter_by(category_id=category_id).all()
        return render_template('category_products.html', category=category, products=products)
    else:
        flash('Catégorie non trouvée')
        return redirect('/')

@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f'Quantité de { item_exists.product.product_name } a été mise à jour')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantité non mise à jour', e)
            flash(f'Quantité de { item_exists.product.product_name } non mise à jour')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} ajouté au panier')
    except Exception as e:
        print('Article non ajouté au panier', e)
        flash(f'{new_cart_item.product.product_name} n\'a pas été ajouté au panier')

    return redirect(request.referrer)

@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.product.current_price * item.quantity for item in cart)
    return render_template('cart.html', cart=cart, amount=amount, total=amount + 200)

@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity += 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = sum(item.product.current_price * item.quantity for item in cart)

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()

            cart = Cart.query.filter_by(customer_link=current_user.id).all()
            amount = sum(item.product.current_price * item.quantity for item in cart)

            data = {
                'quantity': cart_item.quantity,
                'amount': amount,
                'total': amount + 200
            }

            return jsonify(data)
        else:
            return jsonify({'message': 'La quantité ne peut pas être inférieure à 1'})

@views.route('/removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = sum(item.product.current_price * item.quantity for item in cart)

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id)
    if customer_cart:
        try:
            total = sum(item.product.current_price * item.quantity for item in customer_cart)
            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(phone_number='25472000000', email=current_user.email,
                                                                   amount=total + 200, narrative='Achat de marchandises')

            for item in customer_cart:
                new_order = OneOrder()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price
                new_order.status = ("En attente").capitalize()
                new_order.payment_id = create_order_response['id']
                new_order.product_link = item.product_link
                new_order.customer_link = item.customer_link

                db.session.add(new_order)

                product = Product.query.get(item.product_link)
                product.in_stock -= item.quantity

                db.session.delete(item)

                db.session.commit()
            flash('Commande passée avec succès')
            return redirect('/orders')  # Redirige vers la vue des commandes de l'utilisateur après avoir placé la commande
        except Exception as e:
            print("Une erreur s'est produite lors de la commande :", e)
            flash('Commande non passée. Veuillez vérifier la console pour plus de détails.')
            return redirect('/')
    else:
        flash('Votre panier est vide')
        return redirect('/')

@views.route('/view-orders')
@login_required
def order_views():
    orders = OneOrder.query.all()
    return render_template('view_orders.html', orders=orders)

@views.route('/propos')
@login_required
def propos_views():

    return render_template('propos.html')

@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                               if current_user.is_authenticated else [])

    return render_template('search.html')

@views.route('/orders')
@login_required
def order():
    customer_orders = OneOrder.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=customer_orders)
