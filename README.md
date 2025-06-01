# CureCart 💊🛒

CureCart is a complete **online pharmacy management system** built with Flask and MySQL. It includes role-based access for customers and employees (billing, stock manager, manager), with capabilities such as medicine management, cart operations, checkout, and order tracking.

## 🚀 Features

### 🧑‍💼 Customer Features
- Signup/Login system
- Dashboard with medicine catalog
- Add medicines to cart
- Update/Delete cart items
- Checkout and order history
- View and edit profile
- View medicine details and banner promotions

### 🏢 Employee Roles

#### 1. **Billing Employee**
- Add items to cart
- Remove or checkout cart
- Handles billing and stock deduction

#### 2. **Stock Manager**
- Add new medicines with images and details
- Update stock quantity and price
- Manage medicine info

#### 3. **Manager**
- View employees by role
- Upload and delete banners
- Update employee roles and salaries
- Add or remove employees

## 🗃️ Tech Stack

- **Backend**: Python, Flask
- **Database**: MySQL (via SQLAlchemy ORM)
- **Frontend**: HTML, CSS, Jinja2 templates
- **Hosting**: Render
- **File Uploads**: Banner and medicine images (JPG)
- **Session Management**: Flask sessions

## 📁 Project Structure

```
CureCart/
├── static/                  # Contains images (medicine & banner)
├── templates/               # HTML templates for all pages
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
```

## 🔧 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/nosij-playz/Curecart.git
   cd Curecart
   ```

2. **Create a virtual environment and activate it**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL URI**
   Inside `app.py`, edit the following line with your database credentials:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://<username>:<password>@<host>:<port>/<database>'
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access it**
   Visit `http://127.0.0.1:5000/` in your browser.

## 📦 Using CureCart

### Customer:
- Go to `/signup` → Register
- Login and browse medicines
- Add to cart and checkout
- Track orders and manage profile

### Employee:
- Login with role credentials
- Billing → `/billing_employee`
- Stock manager → `/stock_manager`
- Manager → `/manager`

## 🙋‍♂️ Developer

**👨‍💻 Jison Joseph Sebastian**  

For suggestions or queries, [contact me here](https://myporfolio-1o1h.onrender.com/contact)

---

💡 **Suggestions to Improve CureCart**
- Add password hashing (e.g., with `werkzeug.security`)
- Implement pagination in medicine listing
- Add email verification
- Use environment variables for secret keys and DB credentials
- Add automated tests with `pytest`

---

© 2025 Jison Joseph Sebastian – All Rights Reserved.