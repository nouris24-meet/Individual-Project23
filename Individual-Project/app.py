from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

config={
  "apiKey": "AIzaSyCCrC2z_QcYPEx8xKyMmDcGX_1qSPoMI5E",
  "authDomain": "y2personalproject.firebaseapp.com",
  "projectId": "y2personalproject",
  "storageBucket": "y2personalproject.appspot.com",
  "messagingSenderId": "792218777455",
  "appId": "1:792218777455:web:b6ccbad1bad3a69eff9a9a",
  "measurementId": "G-5R3YWZFLGS",
  "databaseURL":"https://y2personalproject-default-rtdb.europe-west1.firebasedatabase.app/"
    
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db=firebase.database()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'


#Code goes below here
@app.route('/', methods=['GET', 'POST'])
def signin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('chat'))
        except:
            error = "Authentication failed"
    return render_template("sign_in.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            updated = {"email":email,  "username":username, "first_name":first_name, "last_name":last_name}
            db.child("Users").child(UID).set(updated)
            return redirect(url_for('chat'))
        except:
            error = "Authentication failed"
    return render_template("sign_up.html")

@app.route('/home')
def home():
    return render_template("index.html")
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        try:
            artist_name = request.form.get('an')
            if not artist_name:
                raise ValueError("Artist name not provided in the form.")

            # Create or update the artist node with the 'artist_name' key
            db.child('Artists').child(artist_name).set({"artist_name": artist_name})

            return redirect(url_for('ac_chat', artist=artist_name))
        except Exception as e:
            print("Couldn't create group chat")
            print(e)

    artists = db.child('Artists').get().val()
    artists_names = []
    if artists:
        artists = list(artists.values())
        for item in artists:
            # Check if 'artist_name' key exists in the item dictionary
            if 'artist_name' in item:
                artists_names.append(item['artist_name'])
            else:
                print("Artist node doesn't have 'artist_name' key:", item)

    print(artists_names)
    return render_template("chat.html", artists_names=artists_names)




@app.route('/ac_chat/<string:artist>', methods=['GET', 'POST'])
def ac_chat(artist):
    if request.method=='POST':
        try:
            me=request.form['message']
            mes={'message':me}
            db.child('Messages').child(artist).push(mes)
            UID=login_session['user']['localId']
            user=db.child("Users").child(UID).get().val()
            chat = db.child('Messages').child(artist).get().val()
            return render_template('ac_chat.html', artist=artist, message=me, us=user, chat=chat)
        except:
            print("Couldn't find a message or a user")
    user=db.child("Users").child(login_session['user']['localId']).get().val()
    chat = db.child('Messages').child(artist).get().val()
    return render_template('ac_chat.html', artist=artist,us = user, chat=chat)

@app.route('/ST', methods=['GET', 'POST'])
def ST():
    if request.method=='POST':
        try:
            t=request.form['title']
            dis=request.form['dis']
            imgin=request.form['imgin']
            u=request.form['url']
            s_tea={'Title':t, 'Discription': dis, 'Image':imgin, 'URL':u}
            db.child('Tea').push(s_tea)
            redirect(url_for('home'))
        except:
            print("Couldn't spill the tea")
    return render_template('ST.html')




@app.route('/gossip')
def gossip():
    teas=db.child('Tea').get().val()
    return render_template('gossip.html', teas=teas)





#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)