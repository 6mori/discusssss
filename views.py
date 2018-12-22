from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
from flask import abort
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from wtforms import SelectMultipleField

from datetime import datetime

from setup import app, db, login_manager
from forms import LoginForm, RegisterForm, TopicForm, CommentForm, SearchForm, ManageTagForm, CreateTagForm
from models import User, Topic, Comment, Tag, Board, Associated

@app.route('/', methods=['GET', 'POST'])
def index():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(url_for('search', select=search_form.select.data, searchContext=search_form.search.data))
    return render_template('index.html', user=current_user, boards=Board.query.all(), tags=Tag.query.all(), form=search_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(uname=login_form.username.data).first()
        if user:
            if user.password == login_form.userpass.data:
                login_user(user)
                flash('登陆成功')
                return redirect(url_for('index'))
            else:
                flash('密码错误')
        else:
            flash('用户名不存在')
    return render_template('login.html', form=login_form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('登出成功')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        if not User.query.filter_by(uname=register_form.username.data).first():
            new_user = User()
            new_user.uname = register_form.username.data
            new_user.password = register_form.userpass.data
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('注册成功')
            return redirect(url_for('index'))
        else:
            flash('用户名已存在')
    return render_template('register.html', form=register_form)

@app.route("/b/<int:boardId>")
def board(boardId):
    board = Board.query.filter_by(bid=boardId).first()
    if not board:
        abort(404)
    return render_template('board.html', \
        board=board, \
        topics=Topic.query.filter_by(bid=boardId).join(User).order_by(Topic.updated_at.desc()).all())

@app.route("/t/<int:topicId>")
def topic(topicId):
    topic = Topic.query.filter_by(pid=topicId).first()
    if not topic:
        abort(404)
    return render_template('topic.html', \
        topic=topic, \
        comments=Comment.query.filter_by(pid=topicId).join(User).order_by(Comment.created_at).all(), \
        tags=Associated.query.join(Tag, Topic).filter(Topic.pid==topicId).with_entities(Tag.tname, Tag.tid).all())

@app.route("/b/<int:boardId>/new_topic", methods=['GET', 'POST'])
@login_required
def new_topic(boardId):
    board = Board.query.filter_by(bid=boardId).first()
    if not board:
        abort(404)
    topic_form = TopicForm()
    if topic_form.validate_on_submit():
        new_topic = Topic()
        new_topic.title = topic_form.title.data
        new_topic.bid = boardId
        new_topic.uid = current_user.uid
        db.session.add(new_topic)
        db.session.commit()

        new_comment = Comment()
        new_comment.context = topic_form.context.data
        new_comment.pid = new_topic.pid
        new_comment.uid = current_user.uid
        db.session.add(new_comment)
        db.session.commit()
        flash('发帖成功')
        return redirect(url_for('topic', topicId=new_topic.pid))
    return render_template('new_topic.html', form=topic_form)

@app.route("/t/<int:topicId>/delete_topic")
@login_required
def delete_topic(topicId):
    topic = Topic.query.filter_by(pid=topicId).first()
    if not topic:
        abort(404)
    checkIfOwner(topic.pid)
    boardId = topic.bid
    db.session.delete(topic)
    db.session.commit()
    return redirect(url_for('board', boardId=boardId))

@app.route("/t/<int:topicId>/new_comment", methods=['GET', 'POST'])
@login_required
def new_comment(topicId):
    topic = Topic.query.filter_by(pid=topicId).first()
    if not topic:
        abort(404)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        new_comment = Comment()
        new_comment.context = comment_form.context.data
        new_comment.pid = topicId
        new_comment.uid = current_user.uid
        db.session.add(new_comment)
        db.session.commit()

        topic = Topic.query.filter_by(pid=topicId).first()
        topic.updated_at = datetime.now()
        db.session.commit()
        flash('回复成功')
        return redirect(url_for('topic', topicId=topicId))
    return render_template('new_comment.html', topic=Topic.query.filter_by(pid=topicId).first(), form=comment_form)

@app.route("/c/<int:commentId>", methods=['GET', 'POST'])
@login_required
def edit_comment(commentId):
    comment = Comment.query.filter_by(cid=commentId).first()
    if not comment:
        abort(404)
    checkIfOwner(comment.uid)
    topic = Topic.query.filter_by(pid=comment.pid).first()
    edit_comment_form = CommentForm(context=comment.context)
    if edit_comment_form.validate_on_submit():
        comment.context = edit_comment_form.context.data
        print(edit_comment_form.context.data)
        db.session.commit()
        flash('编辑成功')
        return redirect(url_for('topic', topicId=topic.pid))
    return render_template('new_comment.html', topic=topic, form=edit_comment_form)

@app.route("/u/<int:userId>")
def user(userId):
    user = User.query.filter_by(uid=userId).first()
    if not user:
        abort(404)
    return render_template('user.html', user=user, \
        topics=Topic.query.filter_by(uid=userId).order_by(Topic.created_at.desc()).all(), \
        comments=Comment.query.filter_by(uid=userId).join(Topic) \
            .order_by(Comment.created_at.desc(), Topic.created_at.desc()).all())

@app.route("/s/<select>/<searchContext>")
def search(select, searchContext):
    if select == 'user':
        user = User.query.filter_by(uname=searchContext).first()
        if user:
            return redirect(url_for('user', userId=user.uid))
        else:
            flash('用户不存在')
            return redirect(url_for('index'))
    if select == 'topic':
        return render_template('search.html', searchContext=searchContext, \
            topics=Topic.query.filter(Topic.title.contains(searchContext)).join(User).all())
    if select == 'comment':
        return render_template('search.html', searchContext=searchContext, \
            comments=Comment.query.filter(Comment.context.contains(searchContext)).join(User).join(Topic).all())
    # if select == 'tag':
    #     tag = Tag.query.filter_by(tname=searchContext).first()
    #     if tag:
    #         return redirect(url_for('tag', tagId=tag.tid))
    #     else:
    #         flash('标签不存在')
    #         return redirect(url_for('index'))

@app.route("/t/<int:topicId>/manage_tag", methods=['GET', 'POST'])
def manage_tag(topicId):
    topic = Topic.query.filter_by(pid=topicId).first()
    if not topic:
        abort(404)
    checkIfOwner(topic.uid)
    tags = Tag.query.all()
    manage_tag_form = ManageTagForm()
    if tags:
        tag_choices = [(tag.tname, tag.tname) for tag in tags]
        selected_tag = Tag.query.outerjoin(Associated).filter(Associated.pid==topicId).all()
        selected_tname = [tag.tname for tag in selected_tag]
        manage_tag_form = ManageTagForm(tags=selected_tname)
        manage_tag_form.tags.choices = tag_choices
        # manage_tag_form.process()
    else:
        flash('没有可用标签')
        return render_template('manage_tag.html', topic=topic)
    if manage_tag_form.validate_on_submit():
        for tag in tags[:]:
            if tag.tname in selected_tname and tag.tname not in manage_tag_form.tags.data:
                del_association = Associated.query.filter_by(tid=tag.tid, pid=topicId).first()
                db.session.delete(del_association)
                db.session.commit()
            elif tag.tname not in selected_tname and tag.tname in manage_tag_form.tags.data:
                new_association = Associated()
                new_association.tid = tag.tid
                new_association.pid = topicId
                new_association.uid = current_user.uid
                db.session.add(new_association)
                db.session.commit()
        flash('管理标签成功')
        return redirect(url_for('topic', topicId=topicId))
    return render_template('manage_tag.html', topic=topic, form=manage_tag_form)

@app.route("/t/<int:topicId>/create_tag", methods=['GET', 'POST'])
def create_tag(topicId):
    create_tag_form = CreateTagForm()
    if create_tag_form.validate_on_submit():
        new_tag = Tag()
        new_tag.tname = create_tag_form.new_tag.data
        db.session.add(new_tag)
        db.session.commit()
        flash('创建标签成功')
        return redirect(url_for('manage_tag', topicId=topicId))
    return render_template('create_tag.html', topicId=topicId, form=create_tag_form)

@app.route("/tag/<int:tagId>")
def tag(tagId):
    tag = Tag.query.filter_by(tid=tagId).first()
    if not tag:
        abort(404)
    return render_template('tag.html', tag=tag, \
        topics=Associated.query.join(Tag, Topic).join(User, User.uid==Topic.uid) \
            .filter(Tag.tid==tagId).with_entities(Topic.title, Topic.pid, Topic.created_at, User.uname).all())


def checkIfOwner(uid):
    if current_user.uid != uid:
        abort(403)

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(uid=int(userid)).first()