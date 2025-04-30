import uuid
from django.utils import timezone

from django.db import models

# Create your models here.

class PlayerModel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class GameModel(models.Model):  # 1日分の麻雀対局を表す
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(auto_now_add=True)
    player1 = models.ForeignKey(PlayerModel, on_delete=models.CASCADE, related_name='game_player1')
    player2 = models.ForeignKey(PlayerModel, on_delete=models.CASCADE, related_name='game_player2')
    player3 = models.ForeignKey(PlayerModel, on_delete=models.CASCADE, related_name='game_player3')
    player4 = models.ForeignKey(PlayerModel, on_delete=models.CASCADE, related_name='game_player4')

    def __str__(self):
        return f"{self.date} のゲーム {self.id}"


class RoundModel(models.Model):  # 各半荘（1回戦、2回戦など）
    game = models.ForeignKey(GameModel, on_delete=models.CASCADE) #gamemodelを所有
    number = models.PositiveIntegerField()  # 何回戦か（1, 2, 3...）

    def __str__(self):
        return f"{self.game.date} - 第{self.number}回戦 - {self.game.id}"


class ScoreModel(models.Model):  # 各プレイヤーの点数
    round = models.ForeignKey(RoundModel, on_delete=models.CASCADE) #GameModelを所有しているRoundModelを所有
    player = models.ForeignKey(PlayerModel, on_delete=models.CASCADE)
    point = models.IntegerField()

    class Meta:
        unique_together = ('round', 'player')
    
    def __str__(self):
        return f"{self.player.name} - {self.round.game.date} - 第{self.round.number}回戦"


    
