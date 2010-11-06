from django.db import models
from django.contrib.auth.models import User, Group, Permission


class Language(models.Model):
    name = models.CharField(max_length=100)
    designed_by = models.CharField(max_length=255,blank=True,null=True)
    icon = models.URLField(blank=True,null=True)

    def __unicode__(self):
        return self.name

class Dummy(models.Model):

    user1 = models.ForeignKey(User, related_name='dummies1', null=True,
            verbose_name='an user',
            help_text=u"""\
Default settings (uses unicode(obj) for both "label" and "value").
""")
    user2 = models.ForeignKey(User, related_name='dummies2', null=True,
            blank=True, limit_choices_to={'username__startswith': 'g'},
            verbose_name='an other user',
            help_text=u"""\
This field uses <tt>limit_choices_to</tt> to exclude all users whose username starts
with <em>t</em>.<br>
Settings are customized, <tt>"label"</tt> is <tt>u"%(first_name)s
%(last_name)s"</tt> and <tt>"value"</tt>
is <tt>"id"</tt>. \
""")
    email = models.EmailField(max_length=100, blank=True, help_text="""\
Select an existing email, or <em>insert a new one</em>.<br />
This field is an <tt>EmailField</tt>! It uses a custom queryset
(<tt>User.objects.all()</tt>) to retrieve its choices.<br>
The autocomplete box is scrollable (<tt>height: 100px;</tt> in the css) because
there is no limit to the number of results (<tt>"limit"</tt> is
<tt>None</tt>).\
""")
    favorite_language = models.ForeignKey(Language, blank=True, null=True,
            verbose_name='your favorite language',
            help_text=u"""\
Select your favorite programming language (hint: first letter "p").<br>
<tt>"label"</tt> is customized using a formatter function.\
""")
    friends = models.ManyToManyField(User,)
            #help_text=u"select all your friends.")
