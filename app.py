from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import Flask, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
import sqlite3  # Or your database library
import os
from werkzeug.utils import secure_filename
from flask import send_file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://avnadmin:AVNS_b8kdyTKrDSvGW41y5Xw@mysql-15214597-curecart.i.aivencloud.com:26397/defaultdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'product')
app.config['UPLOAD_FOLDER1'] = os.path.join(app.root_path, 'static', 'banner')
db = SQLAlchemy(app)
class Customer(db.Model):
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), default=None)
    phone_number = db.Column(db.String(20), default=None)
    address = db.Column(db.Text, default=None)

    cart_items = db.relationship('CustomersCart', back_populates='customer')
class Banner(db.Model):
    __tablename__ = 'banners'  # Ensure this matches your table name
    banner_id = db.Column(db.Integer, primary_key=True)  # Correct primary key column
    image_name = db.Column(db.String(255), nullable=False)
class Employee(db.Model):
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('billing', 'stock', 'manager'), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=True)

    details = db.relationship('EmployeeDetails', back_populates='employee')


class EmployeeDetails(db.Model):
    __tablename__ = 'employee_details'
    
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    email = db.Column(db.String(255), default=None)
    phone_number = db.Column(db.String(20), default=None)
    address = db.Column(db.Text, default=None)

    employee = db.relationship('Employee', back_populates='details')


class Medicines(db.Model):
    __tablename__ = 'medicines'
    
    medicine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), default=None)  # Add image field if necessary
    description = db.Column(db.Text, default=None)
    manufacturer = db.Column(db.String(255), default=None)
    dosage_form = db.Column(db.String(50), default=None)
    prescription_needed = db.Column(db.Boolean, default=None)
    expiry_date = db.Column(db.Date, default=None)
    side_effects = db.Column(db.Text, default=None)

    stock_items = db.relationship('Stock', back_populates='medicine')
    cart_items = db.relationship('CustomersCart', back_populates='medicine')


class Stock(db.Model):
    __tablename__ = 'stock'
    
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.medicine_id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    medicine = db.relationship('Medicines', back_populates='stock_items')


class CustomersCart(db.Model):
    __tablename__ = 'customers_cart'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.medicine_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # Relationships (if necessary)
    customer = db.relationship("Customer", back_populates="cart_items")
    medicine = db.relationship("Medicines", back_populates="cart_items")
class OrderHistory(db.Model):
    __tablename__ = 'orderhistory'

    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.medicine_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    customer = db.relationship('Customer', backref='orders')  # Use lowercase
    medicine = db.relationship('Medicines', backref='orders')
# Home route
@app.route('/')
def home():
    return render_template('login.html')
ALLOWED_EXTENSIONS = {'jpg'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']

        # Check if the username already exists
        existing_user = Customer.query.filter_by(username=username).first()
        if existing_user:
            flash("User already exists! Please log in.")
            return redirect(url_for('login'))  # Redirect to login page if user exists

        # Create a new customer and save to the database
        new_customer = Customer(
            name=name,
            username=username, 
            password=password, 
            email=email, 
            phone_number=phone_number, 
            address=address
        )
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('login'))  # Redirect to login after successful signup

    # If it's a GET request, show the signup form
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission (POST request)
        role = request.form.get('role')  # Get selected role (customer or employee)
        username = request.form.get('username')
        password = request.form.get('password')

        if role == 'customer':
            user = Customer.query.filter_by(username=username, password=password).first()
            if user:
                session['username'] = username
                session['customer_id'] = user.customer_id  # Save customer_id in session
                return redirect(url_for('customer_dashboard'))
        elif role == 'employee':
            # Check employee credentials
            employee = Employee.query.filter_by(username=username, password=password).first()
            if employee:
                session['username'] = username
                session['role'] = employee.role
                if employee.role == 'billing':
                    return redirect(url_for('billing_employee'))
                elif employee.role == 'stock':
                    return redirect(url_for('stock_manager'))
                elif employee.role == 'manager':
                    return redirect(url_for('manager'))

        # If authentication fails, show error message
        return render_template('login.html', error="Username or Password is Wrong!")

    # Handle GET request (show login form)
    return render_template('login.html')

# Billing Employee Route
@app.route('/billing_employee', methods=['GET', 'POST'])
def billing_employee():
    if 'cart_items' not in session:
        session['cart_items'] = []  # Create an empty list for cart items

    error_message = None  # Initialize error message variable

    if request.method == 'POST':
        medicine_name = request.form.get('medicine_name')
        quantity = int(request.form.get('quantity'))

        # Fetch medicine details from the database
        medicine = Medicines.query.filter_by(name=medicine_name).first()
        if medicine:
            stock_item = Stock.query.filter_by(medicine_id=medicine.medicine_id).first()
            if stock_item and stock_item.quantity >= quantity:
                # Check if the item already exists in the cart
                existing_item = next((item for item in session['cart_items'] if item['name'] == medicine.name), None)
                if existing_item:
                    # If item exists, increment the quantity
                    existing_item['quantity'] += quantity
                    flash(f"Updated {existing_item['name']} quantity in cart: {existing_item['quantity']}", 'success')
                else:
                    # Add new item to the cart
                    cart_item = {
                        'name': medicine.name,
                        'price': stock_item.price,  # Use the price from the stock
                        'quantity': quantity
                    }
                    session['cart_items'].append(cart_item)
                    flash(f"Added {cart_item['name']} to cart with quantity: {cart_item['quantity']}", 'success')
            else:
                error_message = "Not enough stock available!"  # Set error message
        else:
            error_message = "Medicine not found!"  # Set error message

    # Render the billing page with current cart items
    cart_items = session.get('cart_items', [])  # Load cart items from session
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('billing_employee.html', cart_items=cart_items, total=total, error_message=error_message)

# Remove Item from Cart Route
@app.route('/remove_item', methods=['POST'])
def remove_item():
    item_name = request.form.get('item_name')
    session['cart_items'] = [item for item in session.get('cart_items', []) if item['name'] != item_name]
    session.modified = True  # Mark the session as modified to ensure it saves
    flash(f"{item_name} removed from the cart.", 'success')  # Alert user about the removal
    return redirect(url_for('billing_employee'))

# Proceed to Checkout Route
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart_items' in session:
        for item in session['cart_items']:
            medicine = Medicines.query.filter_by(name=item['name']).first()
            stock_item = Stock.query.filter_by(medicine_id=medicine.medicine_id).first()  # Fetch stock item
            if medicine and stock_item:
                if stock_item.quantity >= item['quantity']:
                    stock_item.quantity -= item['quantity']
                    print(f"Reduced stock for {medicine.name}. New stock: {stock_item.quantity}")
                else:
                    flash(f"Not enough stock available for {medicine.name}. Current stock: {stock_item.quantity}", 'danger')
                    return redirect(url_for('billing_employee'))

        # Commit changes to the database
        db.session.commit()
        flash("Checkout successful! Stock has been updated.", 'success')  # Alert for successful checkout
        session.pop('cart_items', None)  # Clear the cart
        print("Cart cleared after checkout")
    
    return redirect(url_for('billing_employee'))

# Stock Manager Route
@app.route('/stock_manager', methods=['GET', 'POST'])
def stock_manager():
    if request.method == 'POST':
        if 'add_stock' in request.form:
            item_name = request.form['item_name']
            quantity = request.form['quantity']
            price = request.form['price']
            medicine = Medicines.query.filter_by(name=item_name).first()

            if medicine:
                stock_item = Stock.query.filter_by(medicine_id=medicine.medicine_id).first()
                if stock_item:
                    stock_item.quantity += int(quantity)
                    stock_item.price = float(price)
                    flash(f"Updated stock for {medicine.name}: Quantity {stock_item.quantity}, Price {stock_item.price}", 'success')
                else:
                    new_stock_item = Stock(medicine_id=medicine.medicine_id, quantity=int(quantity), price=float(price))
                    db.session.add(new_stock_item)
                    flash(f"Added new stock for {medicine.name}: Quantity {quantity}, Price {price}", 'success')
                db.session.commit()
            else:
                flash("Medicine not found!", 'danger')

        elif 'add_medicine' in request.form:
            new_medicine_name = request.form['new_medicine_name']
            new_medicine_price = request.form['new_medicine_price']
            new_medicine_image = request.files['new_medicine_image']
            new_medicine_description = request.form['new_medicine_description']
            new_medicine_manufacturer = request.form['new_medicine_manufacturer']
            new_medicine_dosage_form = request.form['new_medicine_dosage_form']
            new_medicine_prescription_needed = request.form['new_medicine_prescription_needed']
            new_medicine_expiry_date = request.form['new_medicine_expiry_date']

            # Save the image file
            if new_medicine_image:
                image_filename = f"{new_medicine_name.replace(' ', '_')}.jpg"
                new_medicine_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            else:
                image_filename = None  # Handle no image case

            new_medicine = Medicines(
                name=new_medicine_name,
                image=image_filename,
                description=new_medicine_description,
                manufacturer=new_medicine_manufacturer,
                dosage_form=new_medicine_dosage_form,
                prescription_needed=bool(int(new_medicine_prescription_needed)),
                expiry_date=new_medicine_expiry_date,
                side_effects=None  # Can be filled if needed
            )
            db.session.add(new_medicine)
            db.session.commit()
            flash(f"Successfully added new medicine: {new_medicine_name}", 'success')

    # Fetch all stock items and medicines
    stock_items = db.session.query(Stock, Medicines).filter(Stock.medicine_id == Medicines.medicine_id).all()
    return render_template('stock_manager.html', stock_items=stock_items)

# Employee Profile Route
@app.route('/employee_profile', methods=['GET', 'POST'])
def employee_profile():
    username = session.get('username')
    employee = Employee.query.filter_by(username=username).first()
    details = EmployeeDetails.query.filter_by(employee_id=employee.employee_id).first()

    if request.method == 'POST':
        # Update profile information
        employee_details = EmployeeDetails.query.filter_by(employee_id=employee.employee_id).first()
        employee_details.email = request.form.get('email')
        employee_details.phone_number = request.form.get('phone_number')
        employee_details.address = request.form.get('address')

        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            employee.password = new_password  # Update employee password

        db.session.commit()
        flash("Profile updated successfully!", 'success')
        return redirect(url_for('employee_profile'))

    return render_template('employee_profile.html', employee=employee, details=details)

# Manager Route
@app.route('/manager', methods=['GET', 'POST'])
def manager():
    selected_role = None
    employees = []
    banners = []

    if request.method == 'POST':
        # If the "Show Employees" button is pressed
        if 'show_employees' in request.form:
            selected_role = request.form.get('role')  # Get the selected role from the form
            # Fetch employees with that role and their details
            employees = db.session.query(Employee, EmployeeDetails).outerjoin(EmployeeDetails).filter(Employee.role == selected_role).all()
        
        # Handle banner upload
        elif 'upload_banner' in request.form:
            return upload_banner()  # Delegate to the upload function

        # Handle banner deletion
        elif 'delete_banner' in request.form:
            banner_id = request.form['banner_id']
            # Fetch the banner to delete
            banner_to_delete = db.session.query(Banner).get(banner_id)
            if banner_to_delete:
                # Remove the file from the server
                image_path = os.path.join(app.config['UPLOAD_FOLDER1'], banner_to_delete.image_name)
                if os.path.exists(image_path):
                    os.remove(image_path)  # Delete the file from the server

                db.session.delete(banner_to_delete)  # Remove the banner from the database
                db.session.commit()  # Commit the changes
                flash('Banner deleted successfully!', 'success')

    # Fetch all banners to display on the manager page
    banners = db.session.query(Banner).all()  # Fetch all banners

    return render_template('manager.html', employees=employees, selected_role=selected_role, banners=banners)

@app.route('/upload_banner', methods=['POST'])
def upload_banner():
    if request.method == 'POST':
        banner_image = request.files.get('image_file')  # Get the uploaded file

        if banner_image and allowed_file(banner_image.filename):  # Check if the file is valid
            # Create a unique filename based on the banner ID from the database
            # Get the next available banner_id (ensure you have a function to do this)
            new_banner_id = get_next_banner_id()  # Implement this function to get the next ID
            image_name = f'banner{new_banner_id}.jpg'  # Create the new file name

            image_path = os.path.join(app.config['UPLOAD_FOLDER1'], image_name)  # Define the full path

            # Save the uploaded file to the designated folder
            banner_image.save(image_path)

            # Create a new banner record in the database
            new_banner = Banner(image_name=image_name)  # Create a new Banner object
            db.session.add(new_banner)  # Add the banner to the session
            db.session.commit()  # Commit the session to save the banner in the database

            flash('Banner uploaded successfully!', 'success')  # Notify the user
        else:
            flash('Invalid file type. Please upload a JPG or PNG image.', 'danger')  # Notify for invalid file type

    return redirect(url_for('manager'))  # Redirect back to the manager page

def get_next_banner_id():
    """Fetch the next available banner ID."""
    last_banner = db.session.query(Banner).order_by(Banner.banner_id.desc()).first()
    return (last_banner.banner_id + 1) if last_banner else 1  # Return next ID or 1 if no banners exist
# Route to Update Employee Salary
@app.route('/update_salary', methods=['POST'])
def update_salary():
    emp_id = request.form.get('emp_id')
    new_salary = request.form.get('new_salary')

    # Fetch the employee to update
    employee = Employee.query.get(emp_id)
    if employee:
        employee.salary = float(new_salary)  # Update the salary
        db.session.commit()
        flash(f"Successfully updated salary for {employee.username} to ₹{new_salary}.", 'success')
    else:
        flash("Employee not found!", 'danger')

    return redirect(url_for('manager'))  # Redirect back to manager dashboard

# Route to Update Employee Role
@app.route('/update_role', methods=['POST'])
def update_role():
    emp_id = request.form.get('emp_id')
    new_role = request.form.get('new_role')

    # Fetch the employee to update
    employee = Employee.query.get(emp_id)
    if employee:
        employee.role = new_role  # Update the role
        db.session.commit()
        flash(f"Successfully updated role for {employee.username} to {new_role}.", 'success')
    else:
        flash("Employee not found!", 'danger')

    return redirect(url_for('manager'))  # Redirect back to manager dashboard

# Route to Show Add Employee Form
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        salary = request.form.get('salary')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')

        # Check if the username already exists
        existing_employee = Employee.query.filter_by(username=username).first()
        if existing_employee:
            flash("Username already exists!", 'danger')
            return redirect(url_for('add_employee'))

        new_employee = Employee(username=username, password=password, role=role, salary=float(salary))
        db.session.add(new_employee)
        db.session.commit()

        # Add employee details
        new_details = EmployeeDetails(employee_id=new_employee.employee_id, email=email, 
                                       phone_number=phone_number, address=address)
        db.session.add(new_details)
        db.session.commit()
        flash(f"Successfully added new employee: {username}", 'success')
        return redirect(url_for('manager'))

    return render_template('add_employee.html')

@app.route('/remove_employee', methods=['POST'])
def remove_employee():
    emp_id = request.form.get('emp_id')
    employee = Employee.query.get(emp_id)
    
    if employee:
        # Remove associated employee details first
        employee_details = EmployeeDetails.query.filter_by(employee_id=emp_id).first()
        if employee_details:
            db.session.delete(employee_details)

        # Now remove the employee
        db.session.delete(employee)
        db.session.commit()  # Commit all deletions together
        flash(f"Successfully removed employee: {employee.username}", 'success')
    else:
        flash("Employee not found!", 'danger')
    
    return redirect(url_for('manager'))
#online evide muthal
@app.route('/customer_dashboard', methods=['GET'])
def customer_dashboard():
    if 'customer_id' not in session:
        return redirect(url_for('home'))  # Redirect to home if not logged in

    # Fetch customer details using the customer ID from session
    customer = Customer.query.get(session['customer_id'])
    
    if customer is None:
        return redirect(url_for('home'))  # Handle case if customer not found

    customer_name = customer.name  # Get the customer's name directly from the customer object
    cart_items = session.get('cart_items', [])  # Load cart items from session
    total = sum(item['price'] * item['quantity'] for item in cart_items)  # Calculate total price

    # Fetch all available medicines or filter by search query
    query = request.args.get('query')  # Get the search query from URL parameters
    if query:
        medicines = Medicines.query.filter(Medicines.name.ilike(f'%{query}%')).all()  # Search for medicines
    else:
        medicines = Medicines.query.all()  # Get all medicines from the database

    # Check if no medicines found
    no_medicines_found = not medicines  # True if no medicines found

    # Fetch banner images from the database
    banners = Banner.query.all()  # Fetch all banners from the database

    return render_template('customer_dashboard.html',
                           customer_name=customer_name,  # Pass customer_name directly
                           cart_items=cart_items,
                           total=total,
                           medicines=medicines,
                           no_medicines_found=no_medicines_found,
                           banners=banners)  # Pass the banners list to the template

@app.route('/medicine_details/<int:medicine_id>')
def medicine_details(medicine_id):
    medicine = Medicines.query.get(medicine_id)
    stock_item = Stock.query.filter_by(medicine_id=medicine.medicine_id).first()
    
    if medicine:
        return render_template('medicine_detail.html', medicine=medicine, stock_item=stock_item)
    else:
        flash("Medicine not found!", 'danger')
        return redirect(url_for('home'))

@app.route('/add_to_cart/<int:medicine_id>', methods=['POST'])
def add_to_cart(medicine_id):
    # Check if the user is logged in
    if 'customer_id' not in session:
        flash("You must be logged in to add items to the cart.", 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    customer_id = session['customer_id']
    
    # Parse the quantity from the JSON payload
    data = request.get_json()
    
    # Log the incoming request data
    app.logger.info(f'Received request to add Medicine ID {medicine_id} with data: {data}')
    
    quantity = data.get('quantity')

    # Validate if the quantity is valid (e.g., greater than 0)
    if not quantity or int(quantity) <= 0:
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400

    # Check if the medicine exists in the Medicines table
    medicine = Medicines.query.get(medicine_id)
    if not medicine:
        return jsonify({'success': False, 'message': 'Medicine not found.'}), 404

    # Check if the medicine is already in the cart for the logged-in customer
    cart_item = CustomersCart.query.filter_by(customer_id=customer_id, medicine_id=medicine_id).first()

    if cart_item:
        # If the medicine is already in the cart, update the quantity
        flash(f'Updated {quantity} of Medicine ID {medicine_id} in cart!', 'success')
        cart_item.quantity += int(quantity)
    else:
        # If the medicine is not in the cart, add it as a new item
        flash(f'Added {quantity} of Medicine ID {medicine_id} to cart!', 'success')
        new_item = CustomersCart(customer_id=customer_id, medicine_id=medicine_id, quantity=int(quantity))
        db.session.add(new_item)

    # Attempt to commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        app.logger.error(f'Error committing to the database: {str(e)}')
        return jsonify({'success': False, 'message': 'Error adding to cart. Please try again.'}), 500

    # Respond with a success message
    return jsonify({'success': True, 'message': 'Added to cart successfully!'})

@app.route('/customer_cart')
def customer_cart():
    return view_cart()

@app.route('/view_details/<int:customer_id>', methods=['GET'])
def view_details(customer_id):
    try:
        conn = get_db_connection()  # Get database connection
        cursor = conn.cursor(dictionary=True)  # Create a cursor
        
        # Query to fetch customer details
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer_details = cursor.fetchone()  # Fetch one record
        
        if not customer_details:
            return "Customer not found", 404

        return render_template('customer_details.html', details=customer_details)
        
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while retrieving details.", 500

    finally:
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection

def view_cart():
    # Check if the user is logged in
    if 'customer_id' not in session:
        return jsonify({'success': False, 'message': 'You must be logged in to view the cart.'}), 403

    customer_id = session['customer_id']
    print("Session Customer ID:", customer_id)  # Debug statement

    # Fetch the cart items for the logged-in customer
    cart_items = CustomersCart.query.filter_by(customer_id=customer_id).all()
    print("Fetched Cart Items:", cart_items)  # Debug statement

    # Calculate total price and prepare items for rendering
    total_price = 0
    items = []
    for item in cart_items:
        medicine = Medicines.query.get(item.medicine_id)
        # Assuming there is a relationship or way to get stock info
        stock_info = Stock.query.filter_by(medicine_id=item.medicine_id).first()
        if medicine and stock_info:
            items.append({
                'cart_item_id': item.cart_item_id,
                'medicine': medicine,
                'quantity': item.quantity,
                'price': stock_info.price,  # Use price from stock table
                'total': item.quantity * stock_info.price  # Calculate total for each item
            })
            total_price += item.quantity * stock_info.price  # Accumulate total price

    if not items:
        print("No items found in the cart for customer_id:", customer_id)  # Debug statement

    # Render the template with cart items and total price
    return render_template('customer_cart.html', cart_items=items, total_price=total_price)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'customer_id' not in session:
        flash('You must be logged in to update your cart.', 'danger')
        return redirect(url_for('login'))

    customer_id = session['customer_id']
    cart_items = CustomersCart.query.filter_by(customer_id=customer_id).all()

    for item in cart_items:
        new_quantity = request.form.get(f'quantity_{item.cart_item_id}')
        if new_quantity.isdigit():
            new_quantity = int(new_quantity)
            if new_quantity > 0:
                item.quantity = new_quantity
            else:
                # If quantity is 0, delete the item from the cart
                db.session.delete(item)

    db.session.commit()
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('customer_cart'))


@app.route('/medicines')
def medicines():
    # Fetch medicines from the database
    medicines_data = Medicines.query.all()  # Fetch all medicines
    return render_template('medicines.html', medicines=medicines_data)
@app.route('/checkout', methods=['GET', 'POST'])
def checkout1():
    # Check if the user is logged in
    if 'customer_id' not in session:
        flash('You must be logged in to checkout.', 'danger')
        return redirect(url_for('login'))

    customer_id = session['customer_id']

    # Fetch the cart items for the logged-in customer
    cart_items = db.session.query(CustomersCart, Medicines, Stock).filter(
        CustomersCart.customer_id == customer_id,
        CustomersCart.medicine_id == Medicines.medicine_id,
        Medicines.medicine_id == Stock.medicine_id  # Join with Stock table
    ).all()

    # Check stock availability
    insufficient_stock = False  # Flag for insufficient stock
    for item, medicine, stock in cart_items:
        if item.quantity > stock.quantity:  # Check if requested quantity exceeds available stock
            flash(f"Not enough stock for {medicine.name}. Requested: {item.quantity}, Available: {stock.quantity}", 'danger')
            insufficient_stock = True  # Set the flag if stock is insufficient

    # Calculate total price
    total = sum(item.quantity * stock.price for item, medicine, stock in cart_items)

    if request.method == 'POST' and not insufficient_stock:
        # Deduct the stock for each item in the cart
        for item, medicine, stock in cart_items:
            if item.quantity <= stock.quantity:  # Just a safeguard; this was already checked above
                stock.quantity -= item.quantity  # Reduce the stock by the quantity bought
                db.session.commit()  # Commit the stock change to the database

        flash('Purchase confirmed successfully!', 'success')  # Show success message
        return redirect(url_for('confirm_purchase'))  # Redirect to purchase confirmation page

    return render_template('checkout.html', cart_items=cart_items, total=total, insufficient_stock=insufficient_stock)

@app.route('/confirm_purchase', methods=['POST'])
def confirm_purchase():
    if 'customer_id' not in session:
        return redirect(url_for('login'))

    customer_id = session['customer_id']
    cart_items = CustomersCart.query.filter_by(customer_id=customer_id).all()

    for item in cart_items:
        # Fetch the stock item to get the price
        stock_item = Stock.query.filter_by(medicine_id=item.medicine_id).first()

        if stock_item is None:
            continue  # Handle the case where the stock item doesn't exist

        total = item.quantity * stock_item.price  # Calculate the total price

        new_order = OrderHistory(
            customer_id=customer_id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            price=stock_item.price,  # Use the price from the stock
            total=total
        )

        # Update stock
        stock_item.quantity -= item.quantity  # Reduce stock based on quantity

        # Add new order to the session
        db.session.add(new_order)

    # Clear the cart
    db.session.query(CustomersCart).filter_by(customer_id=customer_id).delete()

    # Commit all changes
    db.session.commit()

    return redirect(url_for('customer_dashboard'))


@app.route('/cancel_purchase')
def cancel_purchase():
    flash('Order canceled.', 'warning')
    return redirect(url_for('customer_dashboard'))

@app.route('/customer_profile')
def customer_profile():
    # Check if the user is logged in
    if 'customer_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    customer_id = session['customer_id']
    
    # Fetch customer details
    customer = Customer.query.get(customer_id)

    # Fetch order history
    order_history = OrderHistory.query.filter_by(customer_id=customer_id).all()

    return render_template('customer_profile.html', customer=customer, order_history=order_history)
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'customer_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    customer_id = session['customer_id']
    customer = Customer.query.get(customer_id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        password = request.form['password']

        # Update the customer's details
        customer.name = name
        customer.email = email
        customer.phone_number = phone_number
        customer.address = address

        # Update password only if provided
        if password:  # Check if the password field is not empty
            customer.password = password

        db.session.commit()  # Save changes to the database
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer_profile'))

    return render_template('edit_profile.html', customer=customer)
@app.route('/order_history')
def order_history():
    customer_id = session.get('customer_id')  # Ensure the customer is logged in

    if not customer_id:
        flash('You must be logged in to view your order history.', 'warning')
        return redirect(url_for('login'))

    # Query to get order history along with medicine names
    orders = db.session.query(
        OrderHistory,
        Medicines.name.label('medicine_name')  # Get the medicine name
    ).join(Medicines, OrderHistory.medicine_id == Medicines.medicine_id) \
     .filter(OrderHistory.customer_id == customer_id) \
     .all()

    return render_template('order_history.html', orders=orders)
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        # Query the medicines table for matching names
        results = Medicines.query.filter(Medicines.name.ilike(f'%{search_query}%')).all()
        return render_template('search_results.html', results=results, search_query=search_query)

    return redirect(url_for('customer_dashboard')) 
@app.route('/checkout2', methods=['POST'])
def checkout2():
    customer_id = request.form.get('customer_id')

    # Validate customer_id
    customer = db.session.query(Customer).filter_by(customer_id=customer_id).first()

    if not customer:
        flash('Customer not found. Please enter a valid Customer ID.', 'danger')
        return redirect(url_for('billing_employee'))  # Redirect back to the billing employee page

    # Store the customer_id in the session so it can be used later in confirm_purchasebill
    session['customer_id'] = customer_id

    # Fetch the cart items for the specified customer by joining CustomersCart, Medicines, and Stock
    cart_items = db.session.query(CustomersCart, Medicines, Stock).filter(
        CustomersCart.customer_id == customer_id,
        CustomersCart.medicine_id == Medicines.medicine_id,
        Medicines.medicine_id == Stock.medicine_id
    ).all()

    # Calculate total price
    total = sum(item.quantity * stock.price for item, medicine, stock in cart_items)

    # Check if there's insufficient stock
    insufficient_stock = any(item.quantity > stock.quantity for item, medicine, stock in cart_items)

    # Render the checkout page with the customer's cart and stock check
    return render_template('checkout2.html', cart_items=cart_items, total=total, customer_id=customer_id, insufficient_stock=insufficient_stock)

@app.route('/confirm_purchasebill', methods=['POST'])
def confirm_purchasebill():
    customer_id = session.get('customer_id')  # Retrieve the customer_id from the session

    if not customer_id:
        flash('No customer ID found in session. Please try again.', 'danger')
        return redirect(url_for('billing_employee'))

    # Fetch the cart items
    cart_items = db.session.query(CustomersCart, Medicines, Stock).filter(
        CustomersCart.customer_id == customer_id,
        CustomersCart.medicine_id == Medicines.medicine_id,
        Medicines.medicine_id == Stock.medicine_id
    ).all()

    for item, medicine, stock in cart_items:
        if item.quantity > stock.quantity:
            flash(f'Not enough stock for {medicine.name}. Available: {stock.quantity}', 'danger')
            return redirect(url_for('checkout2'))

        total = item.quantity * stock.price

        new_order = OrderHistory(
            customer_id=customer_id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            price=stock.price,
            total=total
        )

        # Update stock
        stock.quantity -= item.quantity

        # Add new order to the session
        db.session.add(new_order)

    # Clear the cart
    db.session.query(CustomersCart).filter_by(customer_id=customer_id).delete()

    # Commit all changes
    db.session.commit()

    flash('Purchase completed successfully!', 'success')
    return redirect(url_for('billing_employee'))

@app.route('/medicine_suggestions', methods=['GET'])
def medicine_suggestions():
    query = request.args.get('query', '')
    if query:
        medicines = Medicines.query.filter(Medicines.name.ilike(f'{query}%')).all()  # Query medicines that start with the input
        suggestions = [{'name': medicine.name} for medicine in medicines]  # Prepare the response
        return jsonify(suggestions)
    return jsonify([])  # Return an empty list if no query # Error if file type is not allowed
def get_next_banner_id():
    """Return the next available banner_id."""
    last_banner = db.session.query(Banner).order_by(Banner.banner_id.desc()).first()
    return (last_banner.banner_id + 1) if last_banner else 1

@app.route('/banner/<int:banner_id>')
def serve_banner(banner_id):
    banner = Banner.query.filter_by(banner_id=banner_id).first()
    if banner:
        image_path = os.path.join(app.config['UPLOAD_FOLDER1'], banner.image_name)  
        print(f"Looking for image at {image_path}")  # Debugging statement
        if os.path.exists(image_path):
            return send_file(image_path)  
        else:
            return "Banner image not found", 404  
    else:
        return "Banner not found", 404  
# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Create Database and Tables
with app.app_context():
    db.create_all()  # This will now create the employee_details table as well

if __name__ == '__main__':
   app.run(debug=True)
