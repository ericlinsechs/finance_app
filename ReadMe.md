<h1 align="center">
<br>FINANCE_APP</h1>

##  Overview

The finance_app is a Flask-based financial application that offers functions such as user registration, login, stock buying and selling, transaction history management, and stock quotes. Using SQLite3, the app handles user session data, and secures routes for logged-in users.


##  Modules

| File                                                                                       | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ---                                                                                        | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| db_module.py | The code is for the Database class within a financial application. It establishes a database connection, manages queries, and creation of tables. The entire database operations are handled using SQLite3.            |
| app.py | This flask-based finance app manages user registries, login, logout, and session handling. It allows users to buy and sell shares, validate share transactions and symbol, display an overview of their portfolio and transaction history, request stock quotes, and update transaction records and current balances in an SQLite database.                                 |
| helpers.py | The code offers helper functions for a financial web application. It features `apology` to render a customised error page, `login_required` to secure certain routes for logged-in users, and `lookup` to fetch current stock prices from Yahoo Finance API. |

---

##  Getting Started

**Dependencies**

Please ensure you have the following dependencies installed on your system:

- Python 3.10.4
- pip 22.0.4

###  Installation

1. Clone the finance_app repository:
```sh
git clone https://github.com/ericlinsechs/finance_app.git
```

2. Change to the project directory:
```sh
cd finance_app
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

###  Running finance_app

```sh
flask run
```

###  Tests
```sh
make test
```

## Reference
The source code for this project is based on the [Harvard University’s CS50 course](https://cs50.harvard.edu/x/2023/). You can find the problem description from the ["C$50 Finance" problem set](https://cs50.harvard.edu/x/2023/psets/9/finance/#c50-finance).