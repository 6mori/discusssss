from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import Length,DataRequired

class LoginForm(FlaskForm):
    username = StringField('用户名',validators=[Length(min=1,max=64,message='用户名长度为1~64位'),DataRequired(message='用户名不能为空')])
    userpass = PasswordField('密码',validators=[Length(min=1,max=64,message='密码长度为1~64位'),DataRequired(message='密码不能为空')])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名',validators=[Length(min=1,max=64,message='用户名长度为1~64位'),DataRequired(message='用户名不能为空')])
    userpass = PasswordField('密码',validators=[Length(min=1,max=64,message='密码长度为1~64位'),DataRequired(message='密码不能为空')])
    submit = SubmitField('注册')

class TopicForm(FlaskForm):
    title = StringField('标题',validators=[Length(min=1,max=64,message='标题长度为1~64位'),DataRequired(message='标题不能为空')])
    context = StringField('内容',validators=[Length(min=1,max=512,message='内容长度为1~512位'),DataRequired(message='内容不能为空')])
    submit = SubmitField('发帖')

class CommentForm(FlaskForm):
    context = StringField('内容',validators=[Length(min=1,max=512,message='内容长度为1~512位'),DataRequired(message='内容不能为空')])
    submit = SubmitField('提交')

class SearchForm(FlaskForm):
    choices = [('user', '用户'),
               ('topic', '主题'),
               ('comment', '回复')]
            #    ('tag', '标签')]
    select = SelectField('搜索:', choices=choices)
    search = StringField('',validators=[DataRequired(message='内容不能为空')])
    submit = SubmitField('搜索')

class ManageTagForm(FlaskForm):
    tags = SelectMultipleField('标签', choices=[])
    submit = SubmitField('提交')

class CreateTagForm(FlaskForm):
    new_tag = StringField('新建标签',validators=[Length(min=1,max=64,message='标题长度为1~64位'),DataRequired(message='标题不能为空')])
    submit = SubmitField('提交')

