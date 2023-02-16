from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import numpy as np


app=Flask(__name__,template_folder='template')
app.config['SECRET_KEY'] = 'housePrice'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'housesystem'
mysql = MySQL(app)
   
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

      
        # Check if account exists 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in users table in database
        if account:
            # Create session data
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            session['username'] = account['username']
            session['position'] = account['position']
            flash('Logged in successfully!', category='success')
            return redirect(url_for('home'))

        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect Email/ password!', category='error')
            return redirect(url_for('home'))

    return render_template("login.html")

@app.route('/home')
def home():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        if session['position'] == 'buyer':  
            return redirect(url_for('buyer'))
        else:
            return redirect(url_for('agent'))

    return redirect(url_for('login'))

@app.route('/home/agent')
def agent():
    username = session['username']
    id=session['id']
    return render_template('home.html', username=username,id=id)


@app.route('/home/buyer')
def buyer():
    username=session['username']
    id=session['id']
    return render_template('homeBuyer.html', username=username,id=id)



@app.route('/logout')
#@login_required
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    session.pop('username', None)
    session.pop('position', None)

    # Redirect to login page
    flash('Logged out successfully!', category='success')
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
    # get data from form
        name = request.form.get('name')
        email = request.form.get('email')
        phoneNo = request.form.get('phoneNo')
        username = request.form.get('username')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        position = request.form.get('position')

                # Check if account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        # If account exists show error and validation checks
        if account:
            flash('Username already taken!', category='error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address', category='error')
        elif cpassword != password:
            flash('Confirmation password does not match!', category='error')
        elif not username or not password or not email or not position or not phoneNo or not name:
            flash('Please fill out the form!', category='error')         
        else:
            # Satisfied requirements to register
            cursor.execute(
                'INSERT INTO users (name, email, phoneNo, username, password, position) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (name, email, phoneNo, username, password, position,))
            mysql.connection.commit()
            flash('You have successfully registered!', category='success')
            return redirect(url_for('home'))
    # Show registration form with message (if any)
    return render_template("signup.html")


@app.route('/myProfile',methods=['GET','POST'])
def myProfile():
    username=session['username']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * from users where username=%s',(username,))
    accounts=cur.fetchall()
    return render_template('myProfile.html', accounts=accounts)

@app.route('/updateProfileLink',methods=['GET','POST'])
def updateProfileLink():
    id=session['id']
    print(id)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * from users where id=%s',(id,))
    accounts=cur.fetchall()
    return render_template('updateProfile.html', accounts=accounts)

@app.route('/updateProfile', methods=['GET', 'POST'])
def updateProfile():
    if request.method == 'POST':
    # get data from form
        name = request.form.get('name')
        email = request.form.get('email')
        phoneNo = request.form.get('phoneNo')
        username = request.form.get('username')
        oldpass = request.form.get('oldpass')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')

                # Check if account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE name = %s AND password=%s', (name,oldpass,))
        accounts = cursor.fetchone()
        
        if accounts: 
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address', category='error')                
            elif cpassword != password:
                flash('Confirmation password does not match!', category='error')
            elif not username or not password or not email or not phoneNo or not name:
                flash('Please fill out the form!', category='error')         
            else:
                cursor.execute('UPDATE users SET email=%s, phoneNo=%s, username=%s, password=%s WHERE name=%s',
                    (email, phoneNo, username, password, name,))
                mysql.connection.commit()
                flash('You have successfully updated!', category='success')
                return render_template("myProfile.html",accounts=accounts)
        else:
            flash('Old password is wrong!', category='error')
            return redirect(url_for('updateProfileLink'))

    return render_template("updateProfile.html",accounts=accounts)

@app.route('/buyerList',methods=['GET','POST'])
def buyerList():
    HouseID=request.form.get('houseID')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT users.*,favourite.Created_At,house.HouseTitle FROM users Join favourite on users.id=favourite.id JOIN house ON house.HouseID=favourite.HouseID WHERE favourite.HouseID=%s ORDER BY favourite.Created_At DESC',(HouseID,))
    buyers=cur.fetchall()
    print(buyers)
    houseTitle=""
    for buyer in buyers:
        houseTitle=buyer['HouseTitle']
    return render_template('buyerList.html', buyers=buyers, houseTitle=houseTitle)

@app.route('/inputHouse')
def inputHouse():
   if session['position'] == 'agent':
      return render_template("housepredict.html")


@app.route('/result',methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        agentid         = session['id']
        username        = session['username']
        HouseTitle      = request.form.get('title')
        HouseAddress    = request.form.get('address')
        HouseYear       = request.form.get('year')
        HouseType       = int(request.form.get('type'))
        HouseStatus     = int(request.form.get('status'))
        Bedroom         = int(request.form.get('Bedroom'))
        Bathroom        = int(request.form.get('Bathroom'))
        SizeArea        = int(request.form.get('SizeArea'))
        transportation  = int(request.form.get('transportation'))
        shop            = int(request.form.get('shop'))
        playground      = int(request.form.get('playground'))
        school          = int(request.form.get('school'))
        pool            = int(request.form.get('pool'))
        sport_facility  = int(request.form.get('sport_facility'))
        medical_Centre  = int(request.form.get('medical_Centre'))
        islamic_Centre  = int(request.form.get('islamic_Centre'))
        furnished       = int(request.form['furnish'])
        
        #HouseYear,shop,medical_Centre
        X =np.array([SizeArea,furnished,HouseStatus,transportation,
                 playground,pool,sport_facility,Bedroom,Bathroom,school,
                 HouseType,islamic_Centre]).reshape(1, -1)
  
        # Restore tuple
        mdl, accuracy = pickle.load(open("model/predictive_model.sav", 'rb'))

        price = "%.2f" % mdl.predict(X)

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('INSERT INTO house( houseTitle, HouseAddress, HouseYear, Price, HouseType, HouseStatus, Bedroom, Bathroom,SizeArea,'
                   'transportation, shop, playground, school,islamic_Centre, pool, sport_facility, medical_Centre, furnished,id)'
                  'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)',
                  (HouseTitle, HouseAddress, HouseYear, price, HouseType, HouseStatus, Bedroom, Bathroom,SizeArea, transportation, shop, 
                   playground, school,islamic_Centre, pool, sport_facility, medical_Centre, furnished,agentid,))
        mysql.connection.commit()
     
        return render_template('result.html', price=price, accuracy=accuracy)



@app.route('/updateHouse',methods=['GET','POST'])
def updateHouse():
    agentid=session['id']
    username=session['username']
    houseID= int(request.form.get('houseID'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM house WHERE houseID= %s',(houseID,))
    houses=cur.fetchall()
    return render_template('houseUpdate.html',houses=houses)

@app.route('/deleteHouse',methods=['GET','POST'])
def deleteHouse():
    agentid=session['id']
    username=session['username']
    houseID= int(request.form.get('houseID'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('Delete FROM house WHERE houseID= %s',(houseID,))
    mysql.connection.commit()
    flash('You have successfully deleted a house details!', category='success')
    return redirect(url_for('houselist'))


@app.route('/resultupdate',methods=['GET','POST'])
def resultupdate():
    if request.method=='POST':
        houseID= int(request.form.get('houseID'))
        HouseTitle      = request.form.get('title')
        HouseAddress    = request.form.get('address')
        HouseYear       = request.form.get('year')
        HouseType       = int(request.form.get('type'))
        HouseStatus     = int(request.form.get('status'))
        Bedroom         = int(request.form.get('Bedroom'))
        Bathroom        = int(request.form.get('Bathroom'))
        SizeArea        = int(request.form.get('SizeArea'))
        transportation  = int(request.form.get('transportation'))
        shop            = int(request.form.get('shop'))
        playground      = int(request.form.get('playground'))
        school          = int(request.form.get('school'))
        pool            = int(request.form.get('pool'))
        sport_facility  = int(request.form.get('sport_facility'))
        medical_Centre  = int(request.form.get('medical_Centre'))
        islamic_Centre  = int(request.form.get('islamic_Centre'))
        furnished       = int(request.form['furnish'])
        #HouseYear,shop,medical_Centre,
        X =np.array([SizeArea,furnished,HouseStatus,transportation,
                 playground,pool,sport_facility,Bedroom,Bathroom,school,
                 HouseType,islamic_Centre]).reshape(1, -1)
  
        # Restore tuple
        mdl, accuracy = pickle.load(open("model/predictive_model.sav", 'rb'))

        price = "%.2f" % mdl.predict(X)

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('UPDATE house SET houseTitle=%s, HouseAddress=%s, HouseYear=%s, Price=%s, HouseType=%s, HouseStatus=%s,'
                   'Bedroom=%s,Bathroom=%s,SizeArea=%s,transportation=%s, shop=%s, playground=%s, school=%s,islamic_Centre=%s, pool=%s,'
                  'sport_facility=%s, medical_Centre=%s, furnished=%s WHERE houseID=%s',
                  (HouseTitle, HouseAddress, HouseYear, price, HouseType, HouseStatus, Bedroom, Bathroom,SizeArea, transportation, 
                   shop, playground, school,islamic_Centre, pool, sport_facility, medical_Centre, furnished,houseID,))
        mysql.connection.commit()
        return render_template('result.html', price=price, accuracy=accuracy)

@app.route('/addtofav',methods=['GET','POST'])
def addtofav():
    buyerid=session['id']
    houseID= int(request.form.get('houseID'))
    print(buyerid)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('INSERT INTO favourite (id,HouseID) values (%s,%s)',(buyerid,houseID,))
    mysql.connection.commit()
    flash('Add to favourite successfully!', category='success')
    
    return redirect(url_for('houselist2'))

@app.route('/deletefav',methods=['GET','POST'])
def deletefav():
    agentid=session['id']
    username=session['username']
    houseID= int(request.form.get('houseID'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('Delete FROM favourite WHERE houseID= %s',(houseID,))
    mysql.connection.commit()
    flash('You have successfully deleted a favourite house!', category='success')
    return redirect(url_for('favouriteList'))

@app.route('/search',methods=['GET','POST'])
def search():
    buyerid=session['id']
    state           = request.form.get('state')
    HouseType       = request.form.get('type')
    HouseStatus     = request.form.get('status')
    Bedroom         = request.form.get('Bedroom')
    Bathroom        = request.form.get('Bathroom')
   
    sql= "SELECT * FROM house WHERE "
    if state=='0':
        sql += ""
    elif state !='0':
        sql += " HouseAddress LIKE '%"+state+"%'"
    if HouseType=='0':
        sql+=""
    elif state !='0' and HouseType!='0':
        sql +=" AND HouseType="+ HouseType
    elif HouseType!='0' and state =='0':
        sql +=" HouseType="+ HouseType
    if HouseStatus=='0':
        sql+=""
    if HouseStatus!='0' and (state !='0'  or HouseType!='0'):
        sql +=" AND HouseStatus="+ HouseStatus
    if HouseStatus!='0' and state =='0'  and HouseType=='0':
        sql +=" HouseStatus="+ HouseStatus
    if Bedroom=='0':
        sql+=""
    if Bedroom!='0' and (state !='0'  or HouseType!='0' or HouseStatus!='0'):
        sql +=" AND Bedroom="+ Bedroom
    elif Bedroom!='0' and state =='0'  and HouseType=='0' and HouseStatus=='0':
        sql +=" Bedroom="+ Bedroom
    if Bathroom=='0':
        sql+=""
    elif Bathroom!='0' and (state !='0'  or HouseType!='0' or HouseStatus!='0' or Bedroom!='0' ):
        sql +=" AND Bathroom="+ Bathroom
    elif Bathroom!='0' and state =='0'  and HouseType=='0' and HouseStatus=='0' and Bedroom!='0' :
        sql +=" Bathroom="+ Bathroom

    sql+=" ORDER BY Created_At DESC"

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute(sql)
    houses=cur.fetchall()

    for house in houses:
        if house['HouseType']==1:
            house['HouseType']="Apartment"
        if house['HouseType']==2:
            house['HouseType']="Town House"
        if house['HouseType']==3:
            house['HouseType']="1 Storey Terrace House"
        if house['HouseType']==4:
            house['HouseType']="1.5 Storey Terrace House"
        if house['HouseType']==5:
            house['HouseType']="2 Storey Terrace House"
        if house['HouseType']==6:
            house['HouseType']="2.5 Storey Terrace House"
        if house['HouseType']==7:
            house['HouseType']="3 Storey Terrace House"
        if house['HouseType']==8:
            house['HouseType']="Bungalow"
        if house['HouseType']==9:
            house['HouseType']="Flat"
        if house['HouseType']==10:
            house['HouseType']="Twin House"
        if house['HouseType']==11:
            house['HouseType']="Terrace House"
        if house['HouseType']==12:
            house['HouseType']="Servis Apartment"
        if house['HouseType']==13:
            house['HouseType']="Dupleks"
        if house['HouseType']==14:
            house['HouseType']="Linked Bungalow"
        if house['HouseType']==15:
            house['HouseType']="Condominium"
        if house['HouseType']==16:
            house['HouseType']="Cluster"

        if house['HouseStatus']==1:
            house['HouseStatus']="Leasehold"
        if house['HouseStatus']==2:
            house['HouseStatus']="Freehold"

        if house['transportation'] == 1:
            house['transportation']="Yes"
        if house['shop'] == 1:
            house['shop'] ="Yes"
        if house['islamic_Centre'] == 1:
            house['islamic_Centre'] ="Yes"
        if house['pool'] == 1:
            house['pool'] ="Yes"
        if house['sport_facility'] == 1:
            house['sport_facility'] ="Yes"
        if house['medical_Centre'] == 1:
            house['medical_Centre'] ="Yes"
        if house['playground'] == 1:
            house['playground'] ="Yes"
        if house['school'] == 1:
            house['school'] ="Yes"

        if house['transportation'] == 0:
            house['transportation']="No"
        if house['shop'] == 0:
            house['shop'] ="No"
        if house['islamic_Centre'] == 0:
            house['islamic_Centre'] ="No"
        if house['pool'] == 0:
            house['pool'] ="No"
        if house['sport_facility'] == 0:
            house['sport_facility'] ="No"
        if house['medical_Centre'] == 0:
            house['medical_Centre'] ="No"
        if house['playground'] == 0:
            house['playground'] ="No"
        if house['school'] == 0:
            house['school'] ="No"
        
        if house['furnished']==0:
            house['furnished']="Not Furnished"
        if house['furnished']==1:
            house['furnished']="Fully Furnished"
        if house['furnished']==2:
            house['furnished']="Half Furnished"

    return render_template('houseList2.html', houses=houses)

    
@app.route('/favouriteList',methods=['GET','POST'])
def favouriteList():
    buyerid=session['id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT house.*,users.name,users.phoneNo,users.email FROM house Join favourite on house.HouseID=favourite.HouseID Join users on users.id=house.id WHERE favourite.id=%s ORDER BY favourite.Created_At DESC',(buyerid,))
    houses=cur.fetchall()

    for house in houses:
        if house['HouseType']==1:
           house['HouseType']="Apartment"
        if house['HouseType']==2:
           house['HouseType']="Town House"
        if house['HouseType']==3:
           house['HouseType']="1 Storey Terrace House"
        if house['HouseType']==4:
           house['HouseType']="1.5 Storey Terrace House"
        if house['HouseType']==5:
           house['HouseType']="2 Storey Terrace House"
        if house['HouseType']==6:
           house['HouseType']="2.5 Storey Terrace House"
        if house['HouseType']==7:
           house['HouseType']="3 Storey Terrace House"
        if house['HouseType']==8:
           house['HouseType']="Bungalow"
        if house['HouseType']==9:
           house['HouseType']="Flat"
        if house['HouseType']==10:
           house['HouseType']="Twin House"
        if house['HouseType']==11:
           house['HouseType']="Terrace House"
        if house['HouseType']==12:
           house['HouseType']="Servis Apartment"
        if house['HouseType']==13:
           house['HouseType']="Dupleks"
        if house['HouseType']==14:
           house['HouseType']="Linked Bungalow"
        if house['HouseType']==15:
           house['HouseType']="Condominium"
        if house['HouseType']==16:
           house['HouseType']="Cluster"

        if house['HouseStatus']==1:
           house['HouseStatus']="Leasehold"
        if house['HouseStatus']==2:
           house['HouseStatus']="Freehold"

        if house['transportation'] == 1:
           house['transportation']="Yes"
        if house['shop'] == 1:
           house['shop'] ="Yes"
        if house['islamic_Centre'] == 1:
           house['islamic_Centre'] ="Yes"
        if house['pool'] == 1:
           house['pool'] ="Yes"
        if house['sport_facility'] == 1:
           house['sport_facility'] ="Yes"
        if house['medical_Centre'] == 1:
           house['medical_Centre'] ="Yes"
        if house['playground'] == 1:
           house['playground'] ="Yes"
        if house['school'] == 1:
           house['school'] ="Yes"

        if house['transportation'] == 0:
           house['transportation']="No"
        if house['shop'] == 0:
           house['shop'] ="No"
        if house['islamic_Centre'] == 0:
           house['islamic_Centre'] ="No"
        if house['pool'] == 0:
           house['pool'] ="No"
        if house['sport_facility'] == 0:
           house['sport_facility'] ="No"
        if house['medical_Centre'] == 0:
           house['medical_Centre'] ="No"
        if house['playground'] == 0:
           house['playground'] ="No"
        if house['school'] == 0:
           house['school'] ="No"
        
        if house['furnished']==0:
           house['furnished']="Not Furnished"
        if house['furnished']==1:
           house['furnished']="Fully Furnished"
        if house['furnished']==2:
           house['furnished']="Half Furnished"

    return render_template('favouriteList.html', houses=houses)


    
@app.route('/houselist',methods=['GET', 'POST'])
def houselist():
    agentid = session['id']

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM house WHERE id=%s ORDER BY Created_At DESC',(agentid,))
    houses=cur.fetchall()

    for house in houses:
        if house['HouseType']==1:
           house['HouseType']="Apartment"
        if house['HouseType']==2:
           house['HouseType']="Town House"
        if house['HouseType']==3:
           house['HouseType']="1 Storey Terrace House"
        if house['HouseType']==4:
           house['HouseType']="1.5 Storey Terrace House"
        if house['HouseType']==5:
           house['HouseType']="2 Storey Terrace House"
        if house['HouseType']==6:
           house['HouseType']="2.5 Storey Terrace House"
        if house['HouseType']==7:
           house['HouseType']="3 Storey Terrace House"
        if house['HouseType']==8:
           house['HouseType']="Bungalow"
        if house['HouseType']==9:
           house['HouseType']="Flat"
        if house['HouseType']==10:
           house['HouseType']="Twin House"
        if house['HouseType']==11:
           house['HouseType']="Terrace House"
        if house['HouseType']==12:
           house['HouseType']="Servis Apartment"
        if house['HouseType']==13:
           house['HouseType']="Dupleks"
        if house['HouseType']==14:
           house['HouseType']="Linked Bungalow"
        if house['HouseType']==15:
           house['HouseType']="Condominium"
        if house['HouseType']==16:
           house['HouseType']="Cluster"

        if house['HouseStatus']==1:
           house['HouseStatus']="Leasehold"
        if house['HouseStatus']==2:
           house['HouseStatus']="Freehold"

        if house['transportation'] == 1:
           house['transportation']="Yes"
        if house['shop'] == 1:
           house['shop'] ="Yes"
        if house['islamic_Centre'] == 1:
           house['islamic_Centre'] ="Yes"
        if house['pool'] == 1:
           house['pool'] ="Yes"
        if house['sport_facility'] == 1:
           house['sport_facility'] ="Yes"
        if house['medical_Centre'] == 1:
           house['medical_Centre'] ="Yes"
        if house['playground'] == 1:
           house['playground'] ="Yes"
        if house['school'] == 1:
           house['school'] ="Yes"

        if house['transportation'] == 0:
           house['transportation']="No"
        if house['shop'] == 0:
           house['shop'] ="No"
        if house['islamic_Centre'] == 0:
           house['islamic_Centre'] ="No"
        if house['pool'] == 0:
           house['pool'] ="No"
        if house['sport_facility'] == 0:
           house['sport_facility'] ="No"
        if house['medical_Centre'] == 0:
           house['medical_Centre'] ="No"
        if house['playground'] == 0:
           house['playground'] ="No"
        if house['school'] == 0:
           house['school'] ="No"
        
        if house['furnished']==0:
           house['furnished']="Not Furnished"
        if house['furnished']==1:
           house['furnished']="Fully Furnished"
        if house['furnished']==2:
           house['furnished']="Half Furnished"

    return render_template('houseList.html', houses=houses)



@app.route('/houselist2',methods=['GET', 'POST'])
def houselist2():
    buyerid = session['id']

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM house ORDER BY Created_At DESC')
    houses=cur.fetchall()

    for house in houses:
        if house['HouseType']==1:
           house['HouseType']="Apartment"
        if house['HouseType']==2:
           house['HouseType']="Town House"
        if house['HouseType']==3:
           house['HouseType']="1 Storey Terrace House"
        if house['HouseType']==4:
           house['HouseType']="1.5 Storey Terrace House"
        if house['HouseType']==5:
           house['HouseType']="2 Storey Terrace House"
        if house['HouseType']==6:
           house['HouseType']="2.5 Storey Terrace House"
        if house['HouseType']==7:
           house['HouseType']="3 Storey Terrace House"
        if house['HouseType']==8:
           house['HouseType']="Bungalow"
        if house['HouseType']==9:
           house['HouseType']="Flat"
        if house['HouseType']==10:
           house['HouseType']="Twin House"
        if house['HouseType']==11:
           house['HouseType']="Terrace House"
        if house['HouseType']==12:
           house['HouseType']="Servis Apartment"
        if house['HouseType']==13:
           house['HouseType']="Dupleks"
        if house['HouseType']==14:
           house['HouseType']="Linked Bungalow"
        if house['HouseType']==15:
           house['HouseType']="Condominium"
        if house['HouseType']==16:
           house['HouseType']="Cluster"

        if house['HouseStatus']==1:
           house['HouseStatus']="Leasehold"
        if house['HouseStatus']==2:
           house['HouseStatus']="Freehold"

        if house['transportation'] == 1:
           house['transportation']="Yes"
        if house['shop'] == 1:
           house['shop'] ="Yes"
        if house['islamic_Centre'] == 1:
           house['islamic_Centre'] ="Yes"
        if house['pool'] == 1:
           house['pool'] ="Yes"
        if house['sport_facility'] == 1:
           house['sport_facility'] ="Yes"
        if house['medical_Centre'] == 1:
           house['medical_Centre'] ="Yes"
        if house['playground'] == 1:
           house['playground'] ="Yes"
        if house['school'] == 1:
           house['school'] ="Yes"

        if house['transportation'] == 0:
           house['transportation']="No"
        if house['shop'] == 0:
           house['shop'] ="No"
        if house['islamic_Centre'] == 0:
           house['islamic_Centre'] ="No"
        if house['pool'] == 0:
           house['pool'] ="No"
        if house['sport_facility'] == 0:
           house['sport_facility'] ="No"
        if house['medical_Centre'] == 0:
           house['medical_Centre'] ="No"
        if house['playground'] == 0:
           house['playground'] ="No"
        if house['school'] == 0:
           house['school'] ="No"
        
        if house['furnished']==0:
           house['furnished']="Not Furnished"
        if house['furnished']==1:
           house['furnished']="Fully Furnished"
        if house['furnished']==2:
           house['furnished']="Half Furnished"

    return render_template('houseList2.html', houses=houses,buyerid=buyerid)


if __name__ =='__main__':
    
    app.run(debug=True)
