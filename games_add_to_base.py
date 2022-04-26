from tg.models import Game


games = ['Warframe', 'Fortnite']
for game in games:
    g = Game(title=game)
    g.save()
