from django.contrib import admin
#from .models import PlayerModel,GameModel,ScoreModel
from .models import *

# Register your models here.
admin.site.register(PlayerModel)
admin.site.register(GameModel)
admin.site.register(ScoreModel)
admin.site.register(RoundModel)
admin.site.register(GameSettingModel)