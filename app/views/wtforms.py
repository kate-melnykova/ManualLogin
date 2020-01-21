from wtforms import Form
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import validators


strip_filter = lambda x: x.strip() if x else None


class BlogForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=255)],
                        filters=[strip_filter])
    content = TextAreaField('Content', filters=[strip_filter])
    id = None
