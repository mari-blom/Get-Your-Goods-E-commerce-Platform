# Get Your Goods

## Overview

**Get Your Goods** is a full-stack e-commerce web application built with **Django**. The platform allows vendors to create and manage online stores, while buyers can browse products, manage a shopping cart, leave reviews, and complete purchases.

The project demonstrates authentication, role-based permissions, database management, REST API development, and responsive web design.

---

## Features

### User Authentication

* User registration and login
* Role selection during registration:

  * Buyer
  * Vendor
* Password reset via email

### Vendor Features

* Create and manage stores
* Add, edit, and delete products
* View reviews on products
* Manage store inventory

### Buyer Features

* Browse all stores
* View products by store
* Product detail pages
* Add products to a shopping cart
* Checkout functionality
* Leave product reviews

### Shopping Cart

* Session-based shopping cart
* Update product quantities
* Remove products from the cart
* Automatic cart clearing after successful checkout

### Checkout

* Purchase products in the cart
* Generate an invoice
* Send the invoice to the buyer via email

### Reviews

* Buyers can review products
* Verified purchase reviews are distinguished from unverified reviews

### REST API

The project also includes a Django REST Framework API allowing authenticated vendors to:

* Create stores
* Add products
* Retrieve stores
* Retrieve products
* View reviews

Authentication is required before modifying resources.

---

## Technologies Used

* Python
* Django
* Django REST Framework
* HTML5
* CSS3
* Bootstrap
* MariaDB / MySQL
* SQLite (during early development)
* GitHub

---

## Installation

### Clone the repository

```bash
git clone https://github.com/mari-blom/GetYourGoods.git
cd GetYourGoods
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

macOS/Linux

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure the database

Update the database settings in `settings.py`.

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create a superuser

```bash
python manage.py createsuperuser
```

### Start the development server

```bash
python manage.py runserver
```

Open your browser and visit:

```
http://127.0.0.1:8000/
```

---

## User Roles

### Buyer

A buyer can:

* Register an account
* Browse stores
* View products
* Add products to a shopping cart
* Purchase products
* Leave product reviews

### Vendor

A vendor can:

* Register an account
* Create stores
* Add products
* Edit products
* Delete products
* View customer reviews

---

## API

The application includes a REST API built using Django REST Framework.

Example endpoints include:

```
/api/vendors/
/api/stores/
/api/products/
/api/reviews/
```

Authentication is required for endpoints that create or modify data.

---

## Future Improvements

Possible future enhancements include:

* Product search
* Product categories
* Wishlist functionality
* Product images
* Payment gateway integration
* Order history
* Sales dashboard for vendors
* Product filtering and sorting
* User profile management

---

## Learning Outcomes

This project provided practical experience with:

* Django Models
* Django Views
* Django Templates
* User Authentication
* Authorization and Permissions
* Django Groups
* Sessions
* CRUD Operations
* Django REST Framework
* Database Design
* MariaDB
* Email functionality

---

## Author

**Mari Blom**

GitHub: https://github.com/mari-blom

Software Engineering Bootcamp Student at HyperionDev.
