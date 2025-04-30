from django import forms
from .models import GameModel, PlayerModel

class GameCreateForm(forms.ModelForm):
    player1 = forms.ModelChoiceField(queryset=PlayerModel.objects.all(), label="プレイヤー1")
    player2 = forms.ModelChoiceField(queryset=PlayerModel.objects.all(), label="プレイヤー2")
    player3 = forms.ModelChoiceField(queryset=PlayerModel.objects.all(), label="プレイヤー3")
    player4 = forms.ModelChoiceField(queryset=PlayerModel.objects.all(), label="プレイヤー4")

    class Meta:
        model = GameModel
        fields = ['player1', 'player2', 'player3', 'player4']

    def clean(self):
        cleaned_data = super().clean()
        players = [
            cleaned_data.get('player1'),
            cleaned_data.get('player2'),
            cleaned_data.get('player3'),
            cleaned_data.get('player4'),
        ]
        if None in players:
            return  # 未入力がある場合、Djangoのバリデーションに任せる

        if len(set(players)) != 4:
            raise forms.ValidationError("4人のプレイヤーはすべて異なる必要があります。")
