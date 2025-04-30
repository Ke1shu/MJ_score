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
    # ウマ設定（2〜4位）
    uma_2 = models.IntegerField(default=10, verbose_name="2位のウマ")
    uma_3 = models.IntegerField(default=-10, verbose_name="3位のウマ")
    uma_4 = models.IntegerField(default=-30, verbose_name="4位のウマ")

    # 返し点（基本点）
    return_score = models.IntegerField(default=30000, verbose_name="返し点")

    # 丸め方法（100の位で）
    rounding_rule = models.CharField(
        max_length=10,
        choices=[
            ('round', '四捨五入'),
            ('floor', '切り捨て（5捨6入）'),
            ('ceil', '切り上げ')
        ],
        default='floor',
        verbose_name="丸め処理方法"
    )

    # 同着処理方法（ウマの分配）
    tie_rule = models.CharField(
        max_length=15,
        choices=[
            ('split', '均等分配（同着者でウマを割る）'),
            ('prefer_early', '順位順（早く登録された人に全部与える）')
        ],
        default='split',
        verbose_name="同着ウマ処理方法"
    )

    def get_uma_top(self):
        """
        1位のウマは、2〜4位の合計と逆符号で自動調整する
        """
        return -(self.uma_2 + self.uma_3 + self.uma_4)

    def __str__(self):
        return f"設定#{self.id} ウマ: {self.get_uma_top()}/{self.uma_2}/{self.uma_3}/{self.uma_4}"



    
