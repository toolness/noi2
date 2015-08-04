'''
NoI Views

All views in the app, as a blueprint
'''

from flask import (Blueprint, render_template, session, request, flash,
                   redirect, url_for)

from app import CONTENT, COUNTRIES, LANGS
from app.models import db

import copy
import json

views = Blueprint('views', __name__)


@views.route('/')
def main_page():
    print session

    return render_template('main.html', **{'SKIP_NAV_BAR': False})


@views.route('/test-template')
def test_template():
    return render_template('test.html', **{'SKIP_NAV_BAR': False})


@views.route('/about')
def about_page():
    return render_template('about.html', **{})


@views.route('/test-hello')
def test_hello():
    return render_template('test-hello.html', **{})


#@views.route('/login', methods=['GET', 'POST'])
#def login():
#    print session
#    if request.method == 'GET':
#        return render_template('login-page.html', **{'SKIP_NAV_BAR': False})
#    if request.method == 'POST':
#        social_login = json.loads(request.form.get('social-login'))
#        session['social-login'] = social_login
#        userid = social_login['userid']
#        userProfile = db.getUser(userid)
#        if userProfile:
#            session['user-profile'] = userProfile
#        else:
#            db.createNewUser(userid, social_login['first_name'],
#            social_login['last_name'], social_login['picture'])
#            userProfile = db.getUser(userid)
#            session['user-profile'] = userProfile
#        flash('You are authenticated using your %s Credentials.' % social_login['idp'])
#        g.is_logged_in = True
#        return jsonify({'result': 0})


#@views.route('/logout')
#def logout():
#    idp = session['social-login']['idp']
#    session.clear()
#    return redirect(url_for('main_page', **{'logout': idp}))


@views.route('/edit/<userid>', methods=['GET', 'POST'])
def edit_user(userid):
    if request.method == 'GET':
        userProfile = db.getUser(userid)  # We get some stuff from the DB.
        return render_template('my-profile.html',
                               **{'userProfile': userProfile})
    if request.method == 'POST':
        userProfile = json.loads(request.form.get('me'))
        session['user-profile'] = userProfile
        db.updateCoreProfile(userProfile)
        flash('Your profile has been saved.')
        return render_template('my-profile.html', **{'userProfile': userProfile})


@views.route('/me', methods=['GET', 'POST'])
def my_profile():
    if request.method == 'GET':
        social_login = session['social-login']
        print "Looking up %s" % social_login['userid']
        userProfile = db.getUser(social_login['userid'])  # We get some stuff from the DB.
        print userProfile
        return render_template('my-profile.html',
                               **{'userProfile': userProfile})
    if request.method == 'POST':
        userProfile = json.loads(request.form.get('me'))
        session['user-profile'] = userProfile
        db.updateCoreProfile(userProfile)
        flash('Your profile has been saved. <br/>You may also want to <a'
              'href="/my-expertise">tell us what you know</a>.')
        session['has_created_profile'] = True
        #return render_template('my-profile.html', **{'userProfile': userProfile})
        return redirect(url_for('main_page'))



@views.route('/my-expertise', methods=['GET', 'POST'])
def my_expertise():
    if 'social-login' not in session:
        flash('You need to be authenticated in order to fill your expertise.', 'error')
        return redirect(url_for('login'))
    social_login = session['social-login']
    userid = social_login['userid']
    if request.method == 'GET':
        userProfile = db.getUser(userid)
        print userProfile
        userExpertise = userProfile['skills']
        return render_template('my-expertise.html', **{'AREAS': CONTENT['areas'],
                                                       'userExpertise': userExpertise})
    if request.method == 'POST':
        userExpertise = json.loads(request.form.get('my-expertise-as-json'))
        session['user-expertise'] = userExpertise
        db.updateExpertise(userid, userExpertise)
        flash("""Your expertise has been updated.<br/>
        What you can do next:
        <ul>
        <li><a href="/search">Search for innovators</a></li>
        <li>Fill another expertise questionnaire below</li>
        <li>View your <a href="/user/%s">public profile</a></li>
        """ % social_login['userid'])
        session['has_filled_expertise'] = True
        #return render_template('my-expertise.html', **{'userExpertise':
        #    userExpertise, 'AREAS': CONTENT['areas']})
        return redirect(url_for('main_page'))


@views.route('/dashboard')
def dashboard():
    top_countries = db.top_countries()
    ALL_USERS = db.getAllUsers()
    OCCUPATIONS = db.getUserOccupations()
    return render_template('dashboard.html', **{'top_countries': top_countries,
                                                'ALL_USERS': ALL_USERS, 'OCCUPATIONS': OCCUPATIONS})

@views.route('/dashboard-2')
def dashboard2():
    top_countries = db.top_countries()
    return render_template('dashboard-2.html', **{'top_countries': top_countries})

#@views.route('/vcard/<userid>')
#def vcard(userid):
#    user = db.getUser(userid)
#    if user:
#        card = make_vCard(user['first_name'], user['last_name'], user['org'],
#        user['title'], user['email'], user['city'], user['country'])
#        return Response(card, mimetype='text/vcard')
#    else:
#        flash('This is does not correspond to a valid user.')
#        return redirect(url_for('main_page'))


@views.route('/user/<userid>')
def get_user(userid):
    user = db.getUser(userid)
    if user:
        if 'social-login' in session:
            my_userid = session['social-login']['userid']
        else:
            my_userid = 'anonymous'
        query_info = {'user-agent': request.headers.get('User-Agent'),
                      'type': '/user', 'userid': my_userid}
        db.logQuery(my_userid, query_info)
        return render_template('user-profile.html',
                               **{'user': user, 'userid': userid, 'SKILLS': []})
    else:
        flash('This is does not correspond to a valid user.')
        return redirect(url_for('search'))


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html', **{'LANGS': LANGS, 'COUNTRIES':
                                                 COUNTRIES, 'AREAS':
                                                 CONTENT['areas']})
    if request.method == 'POST':
        print request
        country = request.values.get('country', '')
        langs = request.values.getlist('langs')
        skills = request.values.getlist('skills')
        domains = request.values.getlist('domains')
        fulltext = request.values.get('fulltext', '')
        query = {'location': country, 'langs': langs, 'skills': skills,
                 'fulltext': fulltext, 'domains': domains}
        print query
        if 'social-login' in session:
            my_userid = session['social-login']['userid']
        else:
            my_userid = 'anonymous'
        query_info = copy.deepcopy(query)
        query_info['type'] = '/search'
        query_info['user-agent'] = request.headers.get('User-Agent')
        db.logQuery(my_userid, query_info)
        experts = db.findExpertsAsJSON(**query)
        session['has_done_search'] = True
        return render_template('search-results.html',
                               **{'title': 'Expertise search', 'results': experts, 'query': query})


@views.route('/match')
def match():
    if 'user-expertise' not in session:
        flash('Before we can match you with fellow innovators, you need to <a'
              'href="/my-expertise">enter your expertise</a> first.', 'error')
        return redirect(url_for('main_page'))
    social_login = session['social-login']
    userid = social_login['userid']
    query = {'location': '', 'langs': [], 'skills': [], 'fulltext': ''}
    if 'skills' not in session['user-expertise']:
        userProfile = db.getUser(userid)
        userExpertise = userProfile['skills']
        session['user-expertise'] = userExpertise
    print "user expertise: ", json.dumps(session['user-expertise'])
    skills = session['user-expertise']
    my_needs = [k for k, v in skills.iteritems() if int(v) == -1]
    print my_needs
    experts = db.findMatchAsJSON(my_needs)
    session['has_done_search'] = True
    return render_template('search-results.html',
                           **{'title': 'People Who Know what I do not',
                              'results': experts, 'query': query})


@views.route('/match-knn')
def knn():
    if 'user-expertise' not in session:
        flash('Before we can find innovators like you, you need to '
              '<a href="/my-expertise">fill your expertise</a> first.', 'error')
        return redirect(url_for('main_page'))
    query = {}
    if 'user-expertise' not in session:
        print "User expertise not in session"
        #my_needs = []
    else:
        skills = session['user-expertise']
    print skills
    experts = db.findMatchKnnAsJSON(skills)
    session['has_done_search'] = True
    return render_template('search-results.html',
                           **{'title': 'People most like me',
                              'results': experts, 'query': query})


@views.route('/users/recent')
def recent_users():
    users = db.getRecentUsers()
    return render_template('search-results.html',
                           **{'title': 'Our Ten most recent members', 'results': users,
                              'query': ''})


@views.route('/feedback')
def feedback():
    return render_template('feedback.html', **{})


@views.route('/match-test')
def match_test():
    print session
    query = {'location': '', 'langs': [], 'skills': [], 'fulltext': 'NYU'}
    if 'user-expertise' not in session:
        session['user-expertise'] = {}
    experts = db.findMatchAsJSON(session['user-expertise'])
    return render_template('test.html',
                           **{'title': 'Matching search', 'results': experts, 'query': query})
