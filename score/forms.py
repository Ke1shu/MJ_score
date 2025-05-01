from django import forms
from .models import *

from django.forms import BaseModelFormSet, ValidationError


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


class ScoreBaseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        total = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
            raw_score = form.cleaned_data.get('raw_score')
            if raw_score is not None:
                total += raw_score
        if total != 100000:
            raise ValidationError(
                f'素点の合計が {total} 点になっています。合計はちょうど 100000 点である必要があります。'
            )

class GameSettingForm(forms.ModelForm):
    class Meta:
        model = GameSettingModel
        exclude = ['uma_3']
