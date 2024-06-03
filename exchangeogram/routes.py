from exchangeogram import app, db, mail
from exchangeogram.middleware import auth as auth_middleware
from exchangeogram.models import User, Post, Notification, Like, encoder
from exchangeogram.forms import SignupForm, LoginForm, PostForm
from flask import Flask, flash, redirect, render_template, request, Response, send_file
from flask_mail import Message
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import os
import uuid
import pathlib
import json

# main page, render application


@app.route('/', methods=["GET"])
@auth_middleware.auth_required_redirect('/landing')
def homepage():
    return render_template('app/home.html', postform=PostForm())


@app.route('/landing', methods=["GET"])
def landing():
    return render_template('landing/main.html')


@app.route('/login', methods=["GET", "POST"])
@auth_middleware.unauth_required_redirect('/')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect('/')

    return render_template('landing/login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=["GET", "POST"])
@auth_middleware.unauth_required_redirect('/')
def register():
    form = SignupForm()
    if form.validate_on_submit():
        token = uuid.uuid4().hex
        user = User(form.username.data, form.displayname.data, form.email.data,
                    form.password.data, token)
        db.session.add(user)
        db.session.commit()

        msg = Message('Exchange-O-Gram Confirm Registration',
                      sender=('Exchange-O-Gram Friendly Bot', 'exchangeogram-noreply@rakagunarto.com'), recipients=[form.email.data])
        msg.body = "Hello {0}, please click on the link below to complete your registration!\n\nhttps://exchangeogram.rakagunarto.com/confirm/{1}".format(
            form.username.data, token)
        mail.send(msg)
        flash('A confirmation email is on its way!')
        return redirect('/register')

    return render_template('landing/register.html', form=form)


@app.route('/confirm/<token>')
def confirm_registration(token=None):
    if token == None:
        return redirect('/')

    user = User.query.filter_by(confirm_token=token).first()
    if user is None:
        return redirect('/')

    user.confirm_token = ''
    db.session.commit()
    return redirect('/login')


@app.route('/app/profile/check', methods=["GET"])
def profile_dupcheck():
    check_type = request.args.get('type')
    check_val = request.args.get('val')

    if check_type is None or check_val is None:  # bad request
        return Response('{"err": "Invalid Request"}', status=400, mimetype="application/json")

    if check_type == 'username':
        if User.query.filter_by(username=check_val).first():
            return Response('{"data": true}', status=200, mimetype="application/json")
        return Response('{"data": false}', status=200, mimetype="application/json")

    if check_type == 'email':
        if User.query.filter_by(email=check_val).first():
            return Response('{"data": true}', status=200, mimetype="application/json")
        return Response('{"data": false}', status=200, mimetype="application/json")

    return Response('{"err": "Invalid Request Type"}', status=400, mimetype="application/json")


@app.route('/app/post/upload', methods=["POST"])
@auth_middleware.auth_required_403
def post_upload():
    form = PostForm()
    if form.validate_on_submit():
        img = form.image.data
        imgname = "{0}.{1}".format(
            uuid.uuid4().hex, img.filename.split('.')[-1])
        pathlib.Path(app.instance_path, 'posts', str(
            current_user.id)).mkdir(exist_ok=True, parents=True)
        img.save(
            os.path.join(
                app.instance_path,
                'posts',
                str(current_user.id),
                imgname
            )
        )
        post = Post(current_user.id, imgname, form.caption.data)
        db.session.add(post)
        db.session.commit()
        return redirect('/')
    return Response('{"err": "Bad Request"}', status=400, mimetype='application/json')

@app.route('/app/posts/<uid>')
@app.route('/app/posts/<uid>/<imgid>')
@auth_middleware.auth_required_403
def get_image(uid=None, imgid=None):
    if uid is None:
        return Response(status=400)
    if imgid is not None:
        try:
            return send_file(os.path.join(
                app.instance_path,
                'posts',
                secure_filename(uid),
                secure_filename(imgid)
            ))
        except Exception as e:
            return Response(status=400)

    posts = Post.query.filter(
        Post.user_id == uid,
    ).order_by(
        Post.date_added.desc()
    ).all()

    return Response(json.dumps(posts, cls=encoder()), status=200, mimetype="application/json")

@app.route('/app/follow/<uid>')
@auth_middleware.auth_required_403
def follow_user(uid=None):
    if uid is None:
        return redirect('/')
    user = User.query.filter_by(id=uid).first()
    if user is None:
        return redirect('/')
    
    myuser = User.query.filter_by(id=current_user.id).first()
    myuser.following.append(user)

    notif = Notification(uid, "{0} just followed you!".format(myuser.displayname))
    db.session.add(notif)

    db.session.commit();
    return redirect('/u/{0}'.format(uid))

@app.route('/u/<uid>', methods=["GET"])
@auth_middleware.auth_required_login
def profile_page(uid=None):
    if uid is None:
        return redirect('/')
    user = User.query.filter_by(id=uid).first()
    if user is None:
        return redirect('/')
    return render_template('app/profile.html', user=user)

@app.route('/app/post/<postid>/like', methods=["POST"])
@auth_middleware.auth_required_403
def like_post(postid=None):
    if postid is None:
        return Response(status=400)
    post = Post.query.filter_by(id=postid).first()
    if post is None:
        return Response(status=400)

    like = Like(current_user.id, post_id=postid)
    db.session.add(like)

    notif = Notification(post.user_id, "{0} liked one of your posts!".format(current_user.displayname))
    db.session.add(notif)

    db.session.commit()
    return Response(status=200)

@app.route('/app/notifications', methods=["GET"])
@auth_middleware.auth_required_403
def get_notifs():
    notifs = Notification.query.filter(
        Notification.user_id == current_user.id
    ).order_by(
        Notification.date_added.desc()
    ).limit(
        6
    ).all()

    return Response(json.dumps(notifs, cls=encoder()), status=200, mimetype='application/json')

@app.route('/app/feed', methods=["GET"])
@auth_middleware.auth_required_403
def feed():
    followinglist = [x.id for x in current_user.following]
    posts = Post.query.filter(
        or_(
            Post.user_id == current_user.id,
            Post.user_id.in_(followinglist)
        ),
    ).order_by(
        Post.date_added.desc()
    ).offset(
        request.args.get('offset') if request.args.get(
            'offset') is not None else 0
    ).limit(
        request.args.get('limit') if request.args.get(
            'limit') is not None else 20
    ).all()

    return Response(json.dumps(posts, cls=encoder()), status=200, mimetype="application/json")
