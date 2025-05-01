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

    setting = models.ForeignKey(
        'GameSettingModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='適用する設定'
    )

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

    # 同着処理の上書き（未設定ならゲームの設定に従う）
    override_tie_rule = models.CharField(
        max_length=15,
        choices=[
            ('', 'ゲーム設定に従う'),
            ('split', '均等分配'),
            ('prefer_early', '順位順（早い人優先）')
        ],
        default='',
        blank=True,
        verbose_name="この対局での同着処理"
    )

    def get_tie_rule(self):
        """
        このラウンドの tie_rule を返す。
        上書き設定がある場合はそれを返す。
        なければ GameSetting に従う。
        """
        if self.override_tie_rule:
            return self.override_tie_rule
        return self.game.setting.tie_rule if self.game.setting else 'split'


    def __str__(self):
        return f"{self.game.date} - 第{self.number}回戦 - {self.game.id}"


class ScoreModel(models.Model):
    round = models.ForeignKey('RoundModel', on_delete=models.CASCADE)
    player = models.ForeignKey('PlayerModel', on_delete=models.CASCADE)

    # 入力される素点（例：25000）
    raw_score = models.IntegerField(default=25000, verbose_name="素点")

    # 計算後のポイント（(素点 - 返し) を丸めて1000で割って、ウマを足した値）
    point = models.FloatField(null=True, blank=True, verbose_name="ポイント")

    class Meta:
        unique_together = ('round', 'player')

    def __str__(self):
        return f"{self.player.name} - 第{self.round.number}回戦"


class GameSettingModel(models.Model):
    return_score = models.IntegerField(default=30000)
    uma_2 = models.IntegerField(default=10)
    uma_3 = models.IntegerField(default=-10)
    uma_4 = models.IntegerField(default=-30)
    tie_rule = models.CharField(
        max_length=20,
        choices=[('split', 'ウマを分配する'), ('prefer_early', '上位優先')],
        default='split'
    )

    def save(self, *args, **kwargs):
        self.uma_3 = -self.uma_2  # 2着の逆に自動設定
        super().save(*args, **kwargs)

    def __str__(self):
        return f"設定#{self.id} ウマ: {self.uma_2} - {abs(self.uma_4)}"

    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['return_score', 'uma_2', 'uma_3', 'uma_4', 'tie_rule'],
                name='unique_game_setting'
            )
        ]
    
