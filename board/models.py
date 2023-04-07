from django.db import models
from django.contrib.auth.models import User


# class Member(models.Model):
#    memberName = models.OneToOneField(User, on_delete=models.CASCADE)

#    def __str__(self):
#        return f'{self.memberName.username}'

#    def count_members(self):
#        members_total = self.objects.all().count()
#        return members_total


tank = 'TANK'
healer = 'HEAL'
damage_dealer = 'DDEA'
merchant = 'MERC'
guildmaster = 'GUIL'
questgiver = 'QUES'
blacksmith = 'BLSM'
tanner = 'TANN'
potions_master = 'POTM'
spell_master = 'SPEL'

msg_types = [(tank, 'танки'), (healer, 'лекари'), (damage_dealer, 'воины'),
             (merchant, 'торговцы'), (guildmaster, 'гильдмастеры'), (questgiver, 'квестгиверы'),
             (blacksmith, 'кузнецы'), (tanner, 'кожевники'), (potions_master, 'зельевары'),
             (spell_master, 'мастера_заклинаний')]


# def images_path():
#     return os.path.join(settings.LOCAL_FILE_DIR, 'images')

# def videos_path():
#     return os.path.join(settings.LOCAL_FILE_DIR, 'videos')

class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    messageDateTime = models.DateTimeField(auto_now_add=True)
    messageTitle = models.CharField(max_length=50)
    messageText = models.TextField()
    # messageImageFiles = models.FilePathField(path=images_path)
    # messageVideoFiles = models.FilePathField(path=videos_path)
    messageImage = models.ImageField(upload_to='images/', null=True, verbose_name="")
    messageVideo = models.FileField(upload_to='videos/', null=True, verbose_name="")
    messageCategory = models.CharField(max_length=4, choices=msg_types, default=damage_dealer)

    def count_publications(self, model):
        pubs_total = self.objects.all().count()
        return pubs_total

    def get_absolute_url(self):  # auto move to page after the Message creation
        return f'/messages/{self.id}

    #def __repr__(self):
    #    return f'{self.get_messageCategory_display()}'


class Post(models.Model):
    messageAuthor = models.ForeignKey(User, on_delete=models.CASCADE)
    postAuthor = models.ForeignKey(User, on_delete=models.CASCADE)
    postToMessage = models.ForeignKey(Message, on_delete=models.CASCADE)
    postText = models.TextField()
    postAccepted = models.BooleanField(default=False)
    postDateTime = models.DateTimeField(auto_now_add=True)

    def accept(self):
        self.postAccepted = True
        self.save()

    def get_absolute_url(self):  # auto move to page after the Post creation
        return f'/posts/{self.id}'

    def count_posts(self, model):
        posts_total = self.objects.all().count()
        return posts_total

class OneTimeCode(models.Model):
    code = models.CharField(max_length=8)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    codeDateTime = models.DateTimeField(auto_now_add=True)


