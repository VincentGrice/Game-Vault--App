#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify
from flask import session as login_session
from flask import make_response

# importing SqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, GameDB, User
import random
import string
import httplib2
import json
import requests

# importing oauth

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

# app configuration

app = Flask(__name__)

# google client secret
secret_file = json.loads(open('client_secret.json', 'r').read())
CLIENT_ID = secret_file['web']['client_id']
APPLICATION_NAME = 'Item-Catalog'

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

engine = create_engine('sqlite:///GameCatalog.db', connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# validating current loggedin user

def find_user():
    email = login_session['email']
    return session.query(User).filter_by(email=email).one_or_none()


# retreive admin user details

def check_admin():
    return session.query(User).filter_by(
        email='vincent_grice@hotmail.com').one_or_none()


# Add new user into database

def createUser():
    name = login_session['name']
    email = login_session['email']
    url = login_session['img']
    provider = login_session['provider']
    newUser = User(name=name, email=email, image=url, provider=provider)
    session.add(newUser)
    session.commit()


def new_state():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return state


def queryAllGames():
    return session.query(GameDB).all()


# App Routes

# main page

@app.route('/')
@app.route('/games/')
def showGames():
    games = queryAllGames()
    state = new_state()
    return render_template('main.html', games=games, currentPage='main',
                           state=state, login_session=login_session)


# To add new game

@app.route('/game/new/', methods=['GET', 'POST'])
def newGame():
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and \
                    login_session['provider'] != 'null':
            gameName = request.form['gameName']
            coverUrl = request.form['gameImage']
            description = request.form['gameDescription']
            description = description.replace('\n', '<br>')
            gameCategory = request.form['category']
            user_id = find_user().id

            if gameName and coverUrl and description \
                    and gameCategory:
                newGame = GameDB(
                    gameName=gameName,
                    coverUrl=coverUrl,
                    description=description,
                    category=gameCategory,
                    user_id=user_id,
                    )
                session.add(newGame)
                session.commit()
                return redirect(url_for('showGames'))
            else:
                state = new_state()
                return render_template(
                    'newItem.html',
                    currentPage='new',
                    title='Add New Game',
                    errorMsg='All Fields are Required!',
                    state=state,
                    login_session=login_session,
                    )
        else:
            state = new_state()
            games = queryAllGames()
            return render_template(
                'main.html',
                games=games,
                currentPage='main',
                state=state,
                login_session=login_session,
                errorMsg='Please Login first to Add Game!',
                )
    elif 'provider' in login_session and login_session['provider'] \
            != 'null':
        state = new_state()
        return render_template('newItem.html', currentPage='new',
                               title='Add New Game', state=state,
                               login_session=login_session)
    else:
        state = new_state()
        games = queryAllGames()
        return render_template(
            'main.html',
            games=games,
            currentPage='main',
            state=state,
            login_session=login_session,
            errorMsg='Please Login first to Add Game!',
            )


# To show game of different category

@app.route('/games/category/<string:category>/')
def sortGames(category):
    games = session.query(GameDB).filter_by(category=category).all()
    state = new_state()
    return render_template(
        'main.html',
        games=games,
        currentPage='main',
        error='Sorry! No Game in Database With This Category :(',
        state=state,
        login_session=login_session)


# To show game detail

@app.route('/games/category/<string:category>/<int:gameId>/')
def gameDetail(category, gameId):
    game = session.query(GameDB).filter_by(id=gameId,
                                           category=category).first()
    state = new_state()
    if game:
        return render_template('itemDetail.html', game=game,
                               currentPage='detail', state=state,
                               login_session=login_session)
    else:
        return render_template('main.html', currentPage='main',
                               error="""No Game Found with this Category
                               and Game Id :(""",
                               state=state,
                               login_session=login_session)


# To edit game detail

@app.route('/games/category/<string:category>/<int:gameId>/edit/',
           methods=['GET', 'POST'])
def editGameDetails(category, gameId):
    game = session.query(GameDB).filter_by(id=gameId,
                                           category=category).first()
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            gameName = request.form['gameName']
            coverUrl = request.form['gameImage']
            description = request.form['gameDescription']
            gameCategory = request.form['category']
            user_id = find_user().id
            admin_id = check_admin().id

            # check if game owner is same as logged in user or admin or not

            if game.user_id == user_id or user_id == admin_id:
                if gameName and coverUrl and description \
                        and gameCategory:
                    game.gameName = gameName
                    game.coverUrl = coverUrl
                    description = description.replace('\n', '<br>')
                    game.description = description
                    game.category = gameCategory
                    session.add(game)
                    session.commit()
                    return redirect(url_for('gameDetail',
                                    category=game.category,
                                    gameId=game.id))
                else:
                    state = new_state()
                    return render_template(
                        'editItem.html',
                        currentPage='edit',
                        title='Edit Game Details',
                        game=game,
                        state=state,
                        login_session=login_session,
                        errorMsg='All Fields are Required!',
                        )
            else:
                state = new_state()
                return render_template(
                    'itemDetail.html',
                    game=game,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! Only the owner can edit games!')
        else:
            state = new_state()
            return render_template(
                'itemDetail.html',
                game=game,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Game Details!',
                )
    elif game:
        state = new_state()
        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = find_user().id
            admin_id = check_admin().id
            if user_id == game.user_id or user_id == admin_id:
                game.description = game.description.replace('<br>', '\n')
                return render_template(
                    'editItem.html',
                    currentPage='edit',
                    title='Edit Game Details',
                    game=game,
                    state=state,
                    login_session=login_session,
                    )
            else:
                return render_template(
                    'itemDetail.html',
                    game=game,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! Only the owner can edit games!')
        else:
            return render_template(
                'itemDetail.html',
                game=game,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Game Details!',
                )
    else:
        state = new_state()
        return render_template('main.html', currentPage='main',
                               error="""Error Editing Game! No Game Found
                               with this Category and Game Id :(""",
                               state=state,
                               login_session=login_session)


# To delete games

@app.route('/games/category/<string:category>/<int:gameId>/delete/')
def deleteGame(category, gameId):
    game = session.query(GameDB).filter_by(category=category,
                                           id=gameId).first()
    state = new_state()
    if game:

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = find_user().id
            admin_id = check_admin().id
            if user_id == game.user_id or user_id == admin_id:
                session.delete(game)
                session.commit()
                return redirect(url_for('showGames'))
            else:
                return render_template(
                    'itemDetail.html',
                    game=game,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! Only the Owner Can delete the game'
                    )
        else:
            return render_template(
                'itemDetail.html',
                game=game,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Delete the Game!',
                )
    else:
        return render_template('main.html', currentPage='main',
                               error="""Error Deleting Game! No Game Found
                               with this Category and Game Id :(""",
                               state=state,
                               login_session=login_session)


# JSON Endpoints

@app.route('/games.json/')
def gamesJSON():
    games = session.query(GameDB).all()
    return jsonify(Games=[game.serialize for game in games])


@app.route('/games/category/<string:category>.json/')
def gameCategoryJSON(category):
    games = session.query(GameDB).filter_by(category=category).all()
    return jsonify(Games=[game.serialize for game in games])


@app.route('/games/category/<string:category>/<int:gameId>.json/')
def gameJSON(category, gameId):
    game = session.query(GameDB).filter_by(category=category,
                                           id=gameId).first()
    return jsonify(Game=game.serialize)


# google signin function

@app.route('/gconnect', methods=['POST'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'),
                               401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data
    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secret.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("""Failed to upgrade the
        authorisation code"""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    header = httplib2.Http()
    result = json.loads(header.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                          200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = access_token
    login_session['id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION

    login_session['name'] = data['name']
    login_session['img'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    if not find_user():
        createUser()
    return jsonify(name=login_session['name'],
                   email=login_session['email'],
                   img=login_session['img'])


# logout user

@app.route('/logout', methods=['post'])
def logout():

    # Disconnect based on provider

    if login_session.get('provider') == 'google':
        return gdisconnect()
    else:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']

    # Only disconnect a connected user.

    if access_token is None:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del login_session['credentials']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']
        login_session['provider'] = 'null'
        response = make_response(json.dumps({'state': 'loggedOut'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        # if given token is invalid, unable to revoke token

        response = make_response(json.dumps({'state': 'errorRevoke'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.secret_key = 'itsasecret'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
