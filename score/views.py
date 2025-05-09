from django.shortcuts import render,redirect, get_object_or_404
#from .models import PlayerModel
from .models import *

from django.views.generic import CreateView,DeleteView,UpdateView
from django.urls import reverse_lazy

from .forms import *

from django.db.models import Sum
from django.forms import modelformset_factory,formset_factory
from django import forms
from .utils import calculate_points


# Create your views here.

def homefunc(request):
    return render(request, 'home.html', {})

def player_listfunc(request):
    object_player = PlayerModel.objects.all()
    return render(request, 'player_list.html',{'object_player':object_player})

def player_detailfunc(request,pk):
    object = get_object_or_404(PlayerModel, pk=pk)
    return render(request,'player_detail.html',{'object':object})

class PlayerCreateView(CreateView):
    template_name = 'player_create.html'
    model = PlayerModel
    fields = ('name',)
    success_url = reverse_lazy('player_list')


class PlayerUpdateView(UpdateView):
    template_name = 'player_update.html'
    model = PlayerModel
    fields = ('player_name',)
    success_url = reverse_lazy('player_list')

class PlayerDeleteView(DeleteView):
    template_name = 'player_delete.html'
    model = PlayerModel
    success_url = reverse_lazy('player_list')


def game_listfunc(request):
    game_list = GameModel.objects.all()
    return render(request,'game_list.html',{'game_list':game_list})

class GameCreateView(CreateView):
    template_name = 'game_create.html'
    form_class = GameCreateForm
    model = GameModel
    #fields = ('player1','player2','player3','player4')
    #success_url = reverse_lazy('game_list')
    def get_success_url(self):
        return reverse_lazy('game_detail', kwargs={'pk': self.object.pk})


def game_detailfunc(request, pk):
    game = get_object_or_404(GameModel, pk=pk)
    rounds = RoundModel.objects.filter(game=game).order_by('number')

    players = [game.player1, game.player2, game.player3, game.player4]

    # 対局スコアテーブルを構築
    table = []
    for round in rounds:
        row = {
            'round': round,      # RoundModel
            'scores': []         # 各プレイヤーの得点
        }
        for player in players:
            score = ScoreModel.objects.filter(round=round, player=player).first()
            row['scores'].append(score.point if score else "-")
        table.append(row)

    # 合計行を構築（辞書形式で統一）
    totals = []
    for player in players:
        total = ScoreModel.objects.filter(round__game=game, player=player).aggregate(Sum('point'))['point__sum'] or 0
        totals.append(total)

    total_row = {
        'round': None,
        'scores': totals,
        'label': '合計'
    }
    table.append(total_row)

    context = {
        'game': game,
        'players': players,
        'score_table': table,
    }

    return render(request, 'game_detail.html', context)


class ScoreForm(forms.Form):
    player = forms.CharField(widget=forms.HiddenInput)
    point = forms.IntegerField(label='スコア')

    ScoreFormSet = modelformset_factory(
    ScoreModel,
    fields=('raw_score',),  # 素点のみ表示
    extra=0,
    formset=ScoreBaseFormSet
    )

def round_create_view(request, pk):
    game = get_object_or_404(GameModel, pk=pk)
    players = [game.player1, game.player2, game.player3, game.player4]
    ScoreFormSet = modelformset_factory(ScoreModel, fields=('raw_score',), extra=4,formset=ScoreBaseFormSet)

    if request.method == 'POST':
        round_number = RoundModel.objects.filter(game=game).count() + 1
        round_obj = RoundModel.objects.create(game=game, number=round_number)

        # POSTデータに基づき4人分のスコアを作成
        formset = ScoreFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            raw_scores = {}
            for i, instance in enumerate(instances):
                instance.round = round_obj
                instance.player = players[i]
                instance.save()
                raw_scores[instance.player.id] = instance.raw_score

            # ポイント計算
            setting = game.setting
            tie_rule = round_obj.get_tie_rule()
            points = calculate_points(raw_scores, setting, tie_rule)

            for score in ScoreModel.objects.filter(round=round_obj):
                score.point = points[score.player.id]
                score.save()

            return redirect('game_detail', pk=game.pk)
        else:
            round_obj.delete()

    else:
        # GET時は空のフォームのみ表示（DBに何も書かない）
        formset = ScoreFormSet(queryset=ScoreModel.objects.none())

    return render(request, 'round_create.html', {
        'formset': formset,
        'round': None,
        'game': game,
    })



def round_edit_view(request, round_pk):
    round_obj = get_object_or_404(RoundModel, id=round_pk)
    game = round_obj.game

    ScoreFormSet = modelformset_factory(
        ScoreModel,
        fields=('raw_score',),
        extra=0,
        formset=ScoreBaseFormSet
    )

    score_queryset = ScoreModel.objects.filter(round=round_obj)

    if request.method == 'POST':
        formset = ScoreFormSet(request.POST, queryset=score_queryset)
        if formset.is_valid():
            instances = formset.save(commit=False)

            # raw_scoreを収集（Noneを除外）
            raw_scores = {}
            for form in formset:
                if form.cleaned_data and form.cleaned_data.get('raw_score') is not None:
                    player_id = form.instance.player.id
                    raw_scores[player_id] = form.cleaned_data['raw_score']

            # 安全チェック：プレイヤー数が4人未満ならエラー
            if len(raw_scores) != 4:
                formset._non_form_errors = ['4人全員分の素点を正しく入力してください。']
            else:
                # 設定取得とポイント再計算
                setting = game.setting
                tie_rule = round_obj.get_tie_rule()
                points = calculate_points(raw_scores, setting, tie_rule)

                # ポイントを設定して保存
                for instance in instances:
                    instance.point = points[instance.player.id]
                    instance.save()

                return redirect('game_detail', pk=game.pk)
    else:
        formset = ScoreFormSet(queryset=score_queryset)

    return render(request, 'round_edit.html', {
        'formset': formset,
        'round': round_obj,
    })



def setting_list(request):
    settings = GameSettingModel.objects.all()
    return render(request, 'setting_list.html', {'settings': settings})

def setting_detail(request, pk):
    setting = get_object_or_404(GameSettingModel, pk=pk)
    return render(request, 'setting_detail.html', {'setting': setting})

def setting_create(request):
    if request.method == 'POST':
        form = GameSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('setting_list')
    else:
        form = GameSettingForm()
    return render(request, 'setting_form.html', {'form': form})

def setting_update(request, pk):
    setting = get_object_or_404(GameSettingModel, pk=pk)
    if request.method == 'POST':
        form = GameSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('setting_detail', pk=pk)
    else:
        form = GameSettingForm(instance=setting)
    return render(request, 'setting_form.html', {'form': form})

def setting_delete(request, pk):
    setting = get_object_or_404(GameSettingModel, pk=pk)
    if request.method == 'POST':
        setting.delete()
        return redirect('setting_list')
    return render(request, 'setting_confirm_delete.html', {'setting': setting})
