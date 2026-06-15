-- Create customers table with primary key constraint on customerID
CREATE TABLE customers (
  customerID TEXT PRIMARY KEY,
  firstName TEXT,
  lastName TEXT,
  birthDay date
);

-- Create employee table with primary key constraint on employeeID
CREATE TABLE employees (
  employeeID TEXT PRIMARY KEY,
  firstName TEXT,
  lastName TEXT,
  birthDay date
);

-- Create orders table with primary key constraint on orderID and foreign key constraint referencing customers.customerID and employees.employeeID
CREATE TABLE orders (
  orderID TEXT PRIMARY KEY,
  customerID TEXT,
  employeeID TEXT,
  orderDate date,
  FOREIGN KEY (customerID) REFERENCES customers(customerID),
  FOREIGN KEY (employeeID) REFERENCES employee(employeeID)
);

-- Create products table with primary key constraint on productID
CREATE TABLE products (
  productID TEXT PRIMARY KEY,
  productName TEXT,
  catagory TEXT,
  itemPrice number
);

-- Create order_items table with primary key constraint on orderID and productID and foreign key constraints referencing orders and products
CREATE TABLE order_items (
  orderID TEXT,
  productID TEXT,
  itemCount number,
  salePrice number,
  PRIMARY KEY (orderID, productID),
  FOREIGN KEY (orderID) REFERENCES orders(orderID),
  FOREIGN KEY (productID) REFERENCES products(productID)
);
