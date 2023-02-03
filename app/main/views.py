from flask import render_template, flash, redirect, url_for, request, g
from app import create_app, db

#login functionality
from app.main.forms import LoginForm, RegistrationForm, AddToCartForm, CartQuantitiesForm, SearchForm, ItemForm,WithdrawForm,DepositForm,TransferForm, SalesForm, AddProduct
from app.main import bp
#user functionality
from flask_login import current_user, login_user, logout_user
from app.models import User, Item, Cart, CartItem, Order, Merchant,Transaction, Card, CardTransaction,Product,Collect
from base64 import b64encode
import base64
from io import BytesIO #C

app = create_app()
#universal content rendering
@app.before_request
def before_request():
    g.search_form = SearchForm()

#homepage
@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title="Front Page", featured=Item.query.all() )

#login page
@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        #this fails if:
        ##the user doesnt exist
        ##the password is wrong (check_password)
        ##the selected usertype is wrong (want users to always know what they're logging in as, even if it's redundant)
        ##the usertype selection doesn't matter if you're logging in as an admin though
        if not user or not user.check_password(form.password.data) or (user.usertype != form.usertype.data and user.usertype != 'Admin'):
            flash('No such user exists.', 'error')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title="Login Page", form=form)

#logout page
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

#register
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, 
            email=form.email.data, 
            phone=form.phone.data,
            address=form.address.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            usertype=form.usertype.data)
            
        user.set_password(form.password.data)
        user.initialize_cart()
        db.session.add(user)
        db.session.commit()
        if form.usertype.data == 'Vendor':
            new_merchant = Merchant(name=user.username ,balance=0,vendor_id=user.id)
            db.session.add(new_merchant)
            db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login')) 
    return render_template('register.html', title='Register', form=form)

#product page routing
@bp.route('/product-<pid>', methods=['GET', 'POST'])
def product(pid):
    item = Item.query.filter_by(id=pid).first()
    if item:
        form = AddToCartForm()
        if request.method == 'POST' and not request.args.get('featuring'):
            current_user.cart.add_item(item)
            flash('Add to cart successful.')
            return redirect(url_for('main.cart')) 
        elif request.args.get('featuring'):
            if item.toggle_feature():
                flash('Item featured successfully.')
            else:
                flash('Item removed from featured items successfully.')
            return redirect(url_for('main.index'))
        
        vendorname = item.vendor.firstname + " " + item.vendor.lastname
        
        return render_template('product.html', item=item, form=form, vendorname=vendorname)

    else:
        return render_template('product.html')


@bp.route('/cart', methods=['GET', 'POST'])
def cart():
    if current_user.is_anonymous:
        flash('You must register to buy items!', 'error')
        return redirect(url_for('main.register')) 

    elif current_user.usertype == 'Vendor' or current_user.usertype == 'Admin':
        flash('You must be a customer to buy items!', 'error')
        return redirect(url_for('index'))

    else:
        editing = False
        form = None
        cart = Cart.query.filter_by(customerid=current_user.id).first()
        if request.args.get('removed'):
            flash('Item removed from cart.')
            cart.remove_item(Item.query.get(request.args.get('removed')))
            return redirect(url_for('cart'))

        cartitems = CartItem.query.filter_by(cartid=cart.id)

        if request.args.get('edit'):
            editing = True
            quantities = []
            for cartitem in cartitems:
                temp = {}
                temp["quantity"] = cartitem.quantity
                quantities.append(temp)
            form = CartQuantitiesForm(quantities=quantities)
        
        if form and request.method == 'POST':
            for i, cartitem in enumerate(cartitems):
                current_user.cart.set_quantity(cartitem.item, form.quantities[i].quantity.data)

            flash('Quantities saved.')
            return redirect(url_for('cart'))

        return render_template('cart.html', cartitems=cartitems, ccart=cart, editing=editing, form=form)

@bp.route('/cart/checkout', methods=['GET','POST'])
def checkout():
    if not current_user.is_anonymous and current_user.usertype=='Customer':
        cart = Cart.query.filter_by(customerid=current_user.id).first()
        cartitems = CartItem.query.filter_by(cartid=cart.id)
        if cartitems:
            error_str = 'Vendor does not have enough items to fulfill order for: '
            errors = 0
            for cartitem in cartitems:
                if cartitem.quantity >= cartitem.item.stock:
                    error_str += cartitem.item.title + ', '
                    errors += 1

        else:
            error_str += 'Cart is empty.  '
            errors += 1

        if errors > 0:
            flash(error_str[:-2], 'error')
            return redirect(url_for('main.cart'))
        
        else:
            cart.checkout()
            flash('Purchase successful. Vendors have been notified.')
            return redirect(url_for('main.index'))
    
    else:
        return redirect(url_for('main.index'))
##vendor stuff
#add_item page

def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic

@bp.route('/add_item',methods=["GET","POST"])
def add_item():
        form = ItemForm()

        if form.validate_on_submit():
    
            image = form.image.data
            data= image.read()
            rendered_file = render_picture(data)
            #url = photos.url(filename)
            item = Item(title=form.name.data,
                price=form.price.data,
                description=form.description.data,
                stock=form.stock.data,
                vendorid=current_user.id,
                data=data, 
                rendered_data=rendered_file)
            db.session.add(item)
            db.session.commit()
            flash("Congratulations, your item has been added")
            return redirect(url_for('main.inventory'))
        else:
            return render_template('add_item.html', title="Add Item", form=form)

#inventory page
@bp.route('/inventory',methods=["GET"])
def inventory():
    if not current_user.is_anonymous and current_user.usertype == 'Vendor':
        items = Item.query.filter_by(vendorid = current_user.id).all()
        if request.args.get('removed'):
            flash('Item removed from your inventory.')
            db.session.delete(Item.query.get(request.args.get('removed')))
            cartitems = CartItem.query.filter_by(itemid=request.args.get('removed'))
            for cartitem in cartitems:
                db.session.delete(cartitem)
            db.session.commit()
            return redirect(url_for('main.inventory'))
        return render_template('inventory.html',items = items)

##profile pages
#vendor page
@bp.route('/vendor/<username>', methods=['GET', 'POST'])
def vendor(username):

    user = User.query.filter_by(username=username).first()

    if request.args.get('completed'):
        flash('Order marked as complete.')
        db.session.delete(Order.query.get(request.args.get('completed')))
        db.session.commit()

        return redirect(url_for('vendor', username=username))

    if user and user.usertype == 'Vendor':
        if current_user.username == user.username:
            orders = Order.query.filter_by(vendor=current_user)
            items = []
        else:
            orders = []
            items = Item.query.filter_by(vendor=user)

        return render_template('vendor.html', vendor=user, items=items, orders=orders)

    else:
        return render_template('404.html')
@bp.route('/main')
def main():


    return render_template('apex.html')

@bp.route('/closest_store')
def closest():

    return render_template('store.html')

@bp.route('/market_place')
def market():

    items = Item.query.order_by(Item.id).all()

    return render_template('markets.html', title="Front Page", items=items)


@bp.route('/view_store/<username>')
def view_store(username):

    user = User.query.filter_by(username=username).first()

    return render_template('store.html',user=user)

@bp.route('/store_sales', methods=['GET', 'POST'])
def store_sales( ):

    sales_form = SalesForm()
    
    if sales_form.validate_on_submit():
        amount = sales_form.amount.data
        discount = sales_form.discount.data
        customer_id = sales_form.customer.data
        vendor_id = current_user.id

        account = Merchant.query.filter_by(vendor_id=vendor_id).first()

        card = Card.query.filter_by(customer_id=customer_id).filter_by(vendor_id=vendor_id).first()

        user = User.query.filter_by(id=customer_id).first()

        if card:

            id = account.id
            account_id = customer_id
            account = Merchant.query.get(id)
    
            if account.deposit_withdraw('withdraw',discount):
                new_transaction = Transaction('transfer out',f'transfer to account {account_id}',account.id,(discount*(-1)))
                db.session.add(new_transaction)
                if card.deposit_withdraw('deposit',discount):
                    new_transaction2 = CardTransaction('transfer in',f'transfer from account {account.id}',card.id,discount)
                    db.session.add(new_transaction2)
                    db.session.commit()

                    return redirect(url_for('main.store_sales'))
    
                else:
                    #flash = you do not have sufficient funds to perform this operation
                    return redirect(url_for('main.store_sales'))
        else:
            new_card = Card(name=user.username ,balance=0,vendor_id=vendor_id, customer_id=customer_id)
            db.session.add(new_card)
            db.session.commit()
            id = account.id
            amount = amount
            discount = amount * 0.10
            account_id = customer_id
            account = Merchant.query.get(id)
    
            if account.deposit_withdraw('withdraw',discount):
                new_transaction = Transaction('transfer out',f'transfer to account {account_id}',account.id,(discount*(-1)))
                db.session.add(new_transaction)
                if new_card.deposit_withdraw('deposit',discount):
                    new_transaction2 = CardTransaction('transfer in',f'transfer from account {account.id}',new_card.id,discount)
                    db.session.add(new_transaction2)
                    db.session.commit()
                    flash('Loyalty discount sent')
                    return redirect(url_for('main.vendor', username=current_user.username))


    return render_template('sales.html', sales_form=sales_form)

@bp.route('/sales-<order_id>-<float:amount>-<vendor_id>-<customer_id>')
def sales(order_id,amount,vendor_id,customer_id):

    account = Merchant.query.filter_by(vendor_id=vendor_id).first()
    order = Order.query.filter_by(id=order_id).first()

    card = Card.query.filter_by(customer_id=customer_id).filter_by(vendor_id=vendor_id).first()

    user = User.query.filter_by(id=customer_id).first()

    if card:

        id = account.id
        discount = amount * 0.10
        account_id = customer_id
        account = Merchant.query.get(id)
 
        if account.deposit_withdraw('withdraw',discount):
            new_transaction = Transaction('transfer out',f'transfer to account {account_id}',account.id,(discount*(-1)))
            db.session.add(new_transaction)
            if card.deposit_withdraw('deposit',discount):
                new_transaction2 = CardTransaction('transfer in',f'transfer from account {account.id}',card.id,discount)
                db.session.add(new_transaction2)
                db.session.commit()
                order.loyalty = True
                db.session.add(order)
                db.session.commit()
                return redirect(url_for('main.vendor', username=current_user.username))
 
            else:
       
                return redirect(url_for('main.vendor', username=current_user.username))
    else:
        new_card = Card(name=user.username ,balance=0,vendor_id=vendor_id, customer_id=customer_id)
        db.session.add(new_card)
        db.session.commit()
        id = account.id
        amount = amount
        discount = amount * 0.10
        account_id = customer_id
        account = Merchant.query.get(id)
 
        if account.deposit_withdraw('withdraw',discount):
            new_transaction = Transaction('transfer out',f'transfer to account {account_id}',account.id,(discount*(-1)))
            db.session.add(new_transaction)
            if new_card.deposit_withdraw('deposit',discount):
                new_transaction2 = CardTransaction('transfer in',f'transfer from account {account.id}',new_card.id,discount)
                db.session.add(new_transaction2)
                db.session.commit()
                order.loyalty = True
                db.session.add(order)
                db.session.commit()
                flash('Loyalty discount sent')
            return redirect(url_for('main.vendor', username=current_user.username))
    return redirect(request.referrer)
  


#customer page
@bp.route('/user/<username>')
def customer(username):
    user = User.query.filter_by(username=username).first()
    if user and user.usertype == 'Customer':
        return render_template('customer.html', customer=user)

    else:
        return render_template('404.html')

@bp.route('/my_account', methods=['GET', 'POST'])
def my_account():

    withdraw_form = WithdrawForm()
    deposit_form = DepositForm()
    transfer_form = TransferForm()
 
    account = Merchant.query.filter_by(vendor_id=current_user.id).first()
    if account:

        transactions = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.date.desc())

        if deposit_form.deposit.data and deposit_form.validate():
            id = account.id
            amount = deposit_form.amount.data
            account = Merchant.query.get(id)
            if account.deposit_withdraw('deposit',amount):
                new_transaction = Transaction('deposit','self deposit',account.id,amount)
                db.session.add(new_transaction)
                db.session.commit()
                return redirect(url_for('main.my_account'))
            else:

                return redirect(url_for('main.my_account'))
        elif withdraw_form.withdraw.data and withdraw_form.validate():
            id = account.id
            amount = withdraw_form.amount.data
            account = Merchant.query.get(id)
            if account.deposit_withdraw('withdraw',amount):
                new_transaction = Transaction('withdraw','self withdraw',account.id,(amount*(-1)))
                db.session.add(new_transaction)
                db.session.commit()
                return redirect(url_for('main.my_account'))
            else:
                #flash = you do not have sufficient funds to perform this operation
                return redirect(url_for('main.my_account'))        
        elif transfer_form.transfer.data and transfer_form.validate():
            id = account.id
            amount = transfer_form.amount.data
            account_id = transfer_form.account_id.data
            password = transfer_form.password.data #To be HASHED      ### Account they are transfering to 
            account = Merchant.query.get(id)
            user = User.query.filter_by(id=current_user.id).first()
            if user is not None and user.verify_password(transfer_form.password.data):
                if account.deposit_withdraw('withdraw',amount):
                    new_transaction = Transaction('transfer out',f'transfer to account {account_id}',account.id,(amount*(-1)))
                    db.session.add(new_transaction)
                    recipient = Account.query.get(account_id)
                    if recipient.deposit_withdraw('deposit',amount):
                        new_transaction2 = Transaction('transfer in',f'transfer from account {account.id}',account_id,amount)
                        db.session.add(new_transaction2)
                        db.session.commit()
                        return redirect(url_for('main.my_account'))
                    else:
                        #flash = you do not have sufficient funds to perform this operation
                        return redirect(url_for('main.my_account'))
                else:
                    #flash = you do not have sufficient funds to perform this operation
                    return redirect(url_for('main.my_account'))
            else:
                return '<h1>Invalid Account Password</h1>'

        return render_template('my_account.html',user=current_user.id,account=account,deposit_form=deposit_form,transfer_form=transfer_form,withdraw_form=withdraw_form)
    return render_template('my_account.html',user=current_user.id,account=account,deposit_form=deposit_form,transfer_form=transfer_form,withdraw_form=withdraw_form)

#admin page
@bp.route('/admin/<username>')
def admin(username):
    user = User.query.filter_by(username=username).first()
    if user and user.usertype == 'Admin':
        if current_user.is_anonymous or current_user.usertype != 'Admin':
            return render_template('403.html')
        
        else:
            return render_template('admin.html', admin=user, users=User.query.all())
    
    else:
        return render_template('404.html')


@bp.route('/collect/<int:product_id>', methods=['GET','POST'])
def collect(product_id):
    product = Product.query.get_or_404(product_id)
    if current_user.is_collecting(product):
        flash('Already collected.', 'info')
        return redirect(url_for('main.product', id=product_id))

    current_user.collect(product)
    flash('Product collected.', 'success')

    return redirect(url_for('mainproduct', id=product_id))


@bp.route('/uncollect/<int:product_id>', methods=['GET', 'POST'])

def uncollect(product_id):
    product = Product.query.get_or_404(product_id)
    if not current_user.is_collecting(product):
        flash('Not collect yet.', 'info')
        return redirect(url_for('product', id=product_id))

    current_user.uncollect(product)
    flash('Photo uncollected.', 'info')
    return redirect(url_for('product', id=product_id))

@bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProduct()

    if form.validate_on_submit():

        name = form.name.data
        description = form.description.data
        category = form.category.data
        image = form.image.data

        print(name)

        data= image.read()
        rendered_file = render_picture(data)

        new_product = Product(name=name, description=description, data=data, rendered_data=rendered_file, category=category)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('main.add_product'))

    return render_template('admin-add.html',form=form)

@bp.route('/online_product-<id>')
def online_product(id):
    product = Product.query.filter_by(id=id).first()

    return render_template('online_product.html', product=product)

@bp.route('/product_collectors-<int:product_id>')
def show_collectors(product_id):
    
    photo = Product.query.get_or_404(product_id)
    page = request.args.get('page', 1, type=int)
    per_page = app.config['PRODUCTS_PER_PAGE']
    pagination = Collect.query.with_parent(photo).order_by(Collect.timestamp.asc()).paginate(page, per_page)
    collects = pagination.items

    return render_template('collectors.html', collects=collects, photo=photo, pagination=pagination)


@bp.route('/collections-<username>', methods=['GET','POST'])
def show_collections(username):
    user = User.query.filter_by(username=username).first_or_404()
    collects = Collect.query.filter_by(collector_id=user.id).all()
    return render_template('collections.html', user=user, collects=collects)


@bp.route("/ajaxlivesearch",methods=["POST","GET"])
def ajaxlivesearch():
 
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            print('type a word')
        else:    
            posts = Product.query.filter(Product.name.like('%' + search_word + '%'))
    
       
    return jsonify({'htmlresponse': render_template('response.html', posts=posts)})


@bp.route('/live_search')
def live_search():

    return render_template('live-search.html')

@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

@bp.route('/product_search', methods=["POST","GET"])
def product_search():
    form = SearchForm()
    return render_template("product_search.html",form=form)


@bp.route('/search', methods=["POST","GET"])
def search():
	form = SearchForm()
	posts = Product.query
	if form.validate_on_submit():
		# Get data from submitted form
		searched = form.searched.data
		# Query the Database
		posts = Product.query.filter(Product.name.like('%' + searched + '%'))

	return render_template("search.html",form=form,searched = form.searched.data,posts = posts)

@bp.route('/card', methods=["POST","GET"])
def card():

    cards = Card.query.filter_by(customer_id=current_user.id).all()

    return render_template("card.html",cards=cards)
