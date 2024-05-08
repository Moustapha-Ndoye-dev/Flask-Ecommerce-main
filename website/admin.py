from datetime import datetime
import os
from flask import Blueprint, app, render_template, flash, send_from_directory, redirect, url_for
from flask_login import login_required, current_user
from .forms import CategoryForm, ShopItemsForm, OrderForm
from werkzeug.utils import secure_filename
from .models import Category, Product, OneOrder, Customer
from flask import send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
from . import db


admin = Blueprint('admin', __name__)


from flask import send_from_directory

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('c:\\Users\\bmd tech\\Pictures', filename)




@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 5:
        form = ShopItemsForm()
        categories = Category.query.all()
        form.category.choices = [(str(category.id), category.name) for category in categories]

        if form.validate_on_submit():
            # Récupérer les données du formulaire
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            category_id = form.category.data

            # Enregistrer l'image sur le serveur
            file = form.product_picture.data
            if file:
                file_name = secure_filename(file.filename)
                file_path = os.path.join('c:\\Users\\bmd tech\\Pictures', file_name)
                file.save(file_path)

                # Créer une nouvelle instance de Product avec le chemin de l'image
                new_shop_item = Product(
                    product_name=product_name,
                    current_price=current_price,
                    previous_price=previous_price,
                    in_stock=in_stock,
                    flash_sale=flash_sale,
                    product_picture=file_path,
                    date_added=datetime.utcnow()
                )

                try:
                    db.session.add(new_shop_item)
                    db.session.commit()

                    # Ajouter la relation many-to-many entre le produit et la catégorie
                    category = Category.query.get(category_id)
                    new_shop_item.categories.append(category)
                    db.session.commit()

                    flash(f'{product_name} ajouté avec succès')
                    return redirect('/add-shop-items')
                except Exception as e:
                    print(e)
                    flash('Erreur lors de l\'ajout du produit')

        return render_template('add_shop_items.html', form=form, categories=categories)
    else:
        return render_template('404.html')



@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 5 or current_user.id == 6:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')



@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    # Vérifie si l'utilisateur actuel est autorisé à accéder à cette page
    if current_user.id not in [5, 6]:
        return render_template('404.html')

    # Récupère l'élément à mettre à jour depuis la base de données
    item_to_update = Product.query.get_or_404(item_id)
    form = ShopItemsForm(obj=item_to_update)

    # Charge les catégories disponibles depuis la base de données
    categories = Category.query.all()
    # Crée une liste de tuples (id, nom) pour les choix du champ de sélection de catégorie
    category_choices = [(category.id, category.name) for category in categories]
    # Ajoute les choix au champ de sélection de catégorie
    form.category.choices = category_choices

    if form.validate_on_submit():
        # Récupère les données du formulaire
        product_name = form.product_name.data
        current_price = form.current_price.data
        previous_price = form.previous_price.data
        in_stock = form.in_stock.data
        flash_sale = form.flash_sale.data
        category_id = form.category.data  # Récupère l'ID de la catégorie sélectionnée

        # Gère le fichier de la photo du produit
        file = form.product_picture.data
        if file:
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)
            item_to_update.product_picture = file_path

        # Met à jour les attributs de l'objet existant
        item_to_update.product_name = product_name
        item_to_update.current_price = current_price
        item_to_update.previous_price = previous_price
        item_to_update.in_stock = in_stock
        item_to_update.flash_sale = flash_sale
        item_to_update.category_id = category_id  # Met à jour la catégorie

        # Enregistre les modifications dans la base de données
        try:
            db.session.commit()
            flash(f'{product_name} mis à jour avec succès', 'success')
            print('Produit mis à jour')
            return redirect(url_for('shop_items'))  # Redirige vers la liste des produits
        except Exception as e:
            print('Produit non mis à jour', e)

    return render_template('update_item.html', form=form)
    



@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 5 or current_user.id == 6:
        try:
            # Ouvrir une connexion à la base de données SQLite
            conn = sqlite3.connect(db.engine.url.database)

            # Désactiver les contraintes de clé étrangère
            conn.execute("PRAGMA foreign_keys = OFF")

            # Supprimer l'élément
            conn.execute(f"DELETE FROM product WHERE id = {item_id}")

            # Valider et enregistrer les modifications
            conn.commit()

            # Réactiver les contraintes de clé étrangère
            conn.execute("PRAGMA foreign_keys = ON")

            # Fermer la connexion
            conn.close()

            flash('Article supprimé avec succés')
        except Exception as e:
            print('Error deleting item:', e)
            flash('Suspression échouer')
    else:
        flash('Accés non autoriser')

    return redirect('/shop-items')





@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 5 or current_user.id == 6:
        orders = OneOrder.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 5 or 6:
        form = OrderForm()

        order = OneOrder.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Article mis a jour avec succés')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Article non mis a jour')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')


@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 5 or 6:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 5 or 6:
        return render_template('admin.html')
    return render_template('404.html')


@admin.route('/categories', methods=['GET'])
@login_required
def categories():
    if current_user.id == 5 or current_user.id == 6:
        categories = Category.query.all()
        return render_template('categories.html', categories=categories)
    return render_template('404.html')

@admin.route('/add-category', methods=['GET', 'POST'])
@login_required
def add_category():
    if current_user.id == 5 or current_user.id == 6:
        form = CategoryForm()
        if form.validate_on_submit():
            name = form.name.data
            new_category = Category(name=name)
            try:
                db.session.add(new_category)
                db.session.commit()
                flash('Catégorie ajouté avec succés')
                return redirect('/categories')
            except Exception as e:
                print(e)
                flash('Lajout a échouer')
        return render_template('add_category.html', form=form)
    return render_template('404.html')



@admin.route('/delete-category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if current_user.id == 5 or current_user.id == 6:
        category = Category.query.get(category_id)
        try:
            db.session.delete(category)
            db.session.commit()
            flash('Catégorie supprimé avec succés')
        except Exception as e:
            print(e)
            flash('La suspression a échouer')
        return redirect('/categories')
    return render_template('404.html')




