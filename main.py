from datetime import datetime
from flask import Flask,  render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_list.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    is_complete = db.Column(db.Boolean, nullable=False)
    created_datetime =  db.Column(db.DateTime, nullable=False)
    completed_datetime =  db.Column(db.DateTime, nullable=True)

db.create_all()


def update_items(form, is_complete:int) -> None:
    """* Update Items Helper Function. 
    * Updates items status

    Args:
        form (ImmutableMultiDict[str, str]): Submitted Form
        is_complete (int): 0 or 1 indicating true or false.
    """
    items = db.session.query(Item).filter(Item.is_complete == is_complete).all()
    for item in items:
        key = f'{item.id}_checkbox'
        print(key)
        is_checked = form.get(key, False)
        if is_checked: 
            item.is_complete = True
            item.completed_datetime = datetime.now()
        else:
            item.is_complete = False
            item.completed_datetime = None

        db.session.commit()


@app.route("/new", methods=['POST']) 
def add_new_item():
    print(request.form.get("new-item"))
    new_item = Item(
        name=request.form.get("new-item"),
        is_complete=False,
        created_datetime=datetime.now(),
        completed_datetime=None
    )
    try:
        db.session.add(new_item)
        db.session.commit()
    except Exception as e:
        print(e)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route("/complete", methods=['POST']) 
def complete_items():
    update_items(request.form, 0)
    return redirect(url_for('home'))

@app.route("/revert", methods=['POST']) 
def revert_item_status():
    update_items(request.form, 1)
    return redirect(url_for('home'))

@app.route("/", methods=['GET', 'POST']) 
def home():
    todo_items = db.session.query(Item).filter(Item.is_complete == 0).order_by(Item.created_datetime.asc()).all()
    completed_items = db.session.query(Item).filter(Item.is_complete == 1).order_by(Item.completed_datetime.desc()).all()
    return render_template("index.html", items = todo_items, completed_items = completed_items)


if __name__ == '__main__':
    app.run(debug=True)
