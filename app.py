import os

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
)
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from db_module import Database


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

app.config["SECRET_KEY"] = "default_secret_key"

# Configure SQLite database
db_path = os.path.join(os.path.dirname(__file__), "finance.db")
db = Database(db_path)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session.get("user_id")

    # Get user's cash
    query = "SELECT cash FROM users WHERE id = ?"
    rows = db.execute_query(query, user_id)

    if not rows:
        return apology("Failed to retrieve user ID", 500)

    cash = round(rows[0]["cash"], 2)

    # Calculate total asset
    total = cash

    # Get the user's transaction records
    query = "SELECT symbol, price, shares FROM transactions WHERE user_id = ?"
    rows = db.execute_query(query, user_id)

    if not rows:
        return render_template(
            "index.html",
            cash="{:.2f}".format(cash),
            total="{:.2f}".format(total),
        )

    # Calculate shares, holding, and current price
    shares = {}
    holding = {}
    current_price = {}

    # Collect unique symbols
    unique_symbols = set(row["symbol"] for row in rows)

    # Retrieve current prices for unique symbols
    for symbol in unique_symbols:
        current_price[symbol] = "{:.2f}".format(lookup(symbol)["price"])

    for row in rows:
        symbol = row["symbol"]
        total_price = round(float(row["price"] * row["shares"]), 2)

        shares.setdefault(symbol, 0)
        holding.setdefault(symbol, 0)

        shares[symbol] += row["shares"]
        holding[symbol] += total_price
        total += total_price

    return render_template(
        "index.html",
        shares=shares,
        current_price=current_price,
        holding={symbol: "{:.2f}".format(value) for symbol, value in holding.items()},
        cash="{:.2f}".format(cash),
        total="{:.2f}".format(total),
    )


def validate_symbol(symbol):
    # Ensure symbol was submitted
    if not symbol:
        return "must provide symbol", 400
    if not symbol.isalpha():
        return "invalid symbol", 400

    return None, None  # No validation errors


def validate_shares(shares):
    try:
        shares = int(shares)
        # Ensure shares was submitted
        if not shares:
            return "must provide shares", 400

        if shares < 1:
            return "value must be greater than or equal to 1", 400

        if shares != float(shares):
            return "value must be a positive integer", 400

    except ValueError:
        return "invalid shares", 400

    return None, None  # No validation errors


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate symbol
        error_message, error_code = validate_symbol(symbol)
        if error_message:
            return apology(error_message, error_code)

        # Validate shares
        error_message, error_code = validate_shares(shares)
        if error_message:
            return apology(error_message, error_code)

        symbol = symbol.upper()
        quote = lookup(symbol)

        if not quote:
            return apology("invalid symbol", 400)

        # Get the user cash
        query = "SELECT cash FROM users WHERE id = ?"
        args = session.get("user_id")
        rows = db.execute_query(query, args)

        if not rows:
            return apology("Failed to retrieve user ID", 500)

        cash = rows[0]["cash"]

        shares = int(shares)
        buy = float(quote["price"]) * shares
        if buy > cash:
            return apology("can't afford", 400)

        # Update transaction
        query = "INSERT INTO transactions (user_id, symbol, price, shares) VALUES (?, ?, ?, ?)"
        args = (session.get("user_id"), symbol, float(quote["price"]), shares)
        db.execute_query(query, *args)

        # Update user cash
        query = "UPDATE users SET cash = ? WHERE id = ?"
        args = (cash - buy, session.get("user_id"))
        db.execute_query(query, *args)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session.get("user_id")
    # Retrieve all transaction records of the user ordered by timestamp
    query = (
        "SELECT symbol, price, shares, timestamp FROM transactions WHERE user_id = ?"
        "ORDER BY timestamp ASC"
    )
    transactions = db.execute_query(query, user_id)

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute_query(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 400)

        quote = lookup(symbol)

        if quote:
            quote["price"] = "{:.2f}".format(quote["price"])
            return render_template("quoted.html", quote=quote), 200
        else:
            return apology("Invalid symbol", 400)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not confirmation:
            return apology("must provide repeat password", 400)

        # Query database for username
        rows = db.execute_query("SELECT * FROM users WHERE username = ?", username)

        # Ensure username not exists
        if len(rows) > 0:
            return apology("username already exists", 400)

        # Ensure password do match
        if password != confirmation:
            return apology("password doesn't match", 400)

        # Insert new user into database
        query = "INSERT INTO users (username, hash) VALUES (?, ?)"
        args = (username, generate_password_hash(password, method="pbkdf2"))
        db.execute_query(query, *args)

        # Get the user ID for the newly registered user
        query = "SELECT id FROM users WHERE username = ?"
        args = username
        rows = db.execute_query(query, args)

        if not rows:
            return apology("Failed to retrieve user ID", 500)

        # Set the user ID in the session
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_sell = request.form.get("shares")

        # Validate symbol
        error_message, error_code = validate_symbol(symbol)
        if error_message:
            return apology(error_message, error_code)

        # Validate shares
        error_message, error_code = validate_shares(shares_sell)
        if error_message:
            return apology(error_message, error_code)

        symbol = symbol.upper()
        # Look up for the symbol
        quote = lookup(symbol)

        if not quote:
            return apology("invalid symbol", 400)

        # Check if the user owns enough shares of stock
        user_id = session.get("user_id")
        query = "SELECT shares FROM transactions WHERE user_id = ? AND symbol = ?"
        args = (user_id, symbol)
        rows = db.execute_query(query, *args)

        shares_hold = 0
        shares_sell = int(shares_sell)
        for row in rows:
            shares_hold += row["shares"]

        if shares_hold < shares_sell:
            return apology("too many shares", 400)

        # Get selling price
        price_sell = round(float(quote["price"] * shares_sell), 2)

        # Update user's cash by adding the selling price
        query = "UPDATE users SET cash = cash + ? WHERE id = ?"
        args = (
            price_sell,
            user_id,
        )
        db.execute_query(query, *args)

        # Update transaction record
        query = "INSERT INTO transactions (user_id, symbol, price, shares) VALUES (?, ?, ?, ?)"
        args = (user_id, symbol, quote["price"], -shares_sell)
        db.execute_query(query, *args)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        user_id = session.get("user_id")
        # Fetch the symbols of stocks the user currently holds
        query = "SELECT DISTINCT symbol FROM transactions WHERE user_id = ?"
        rows = db.execute_query(query, user_id)
        symbols = [item["symbol"] for item in rows]

        return render_template("sell.html", symbols=symbols)


if __name__ == "__main__":
    app.run(debug=True)
