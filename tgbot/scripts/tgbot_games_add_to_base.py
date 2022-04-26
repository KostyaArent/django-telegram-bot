from tgbot.models import Game

def run():
    games = [
        'Warframe', 'Fortnite', 'Counter-Strike GO', 'StarCraft2',
        'Back4Blood', 'Left 4 Dead 2', 'Empire Earth III']

    for game in games:
        g, create = Game.objects.get_or_create(title=game)
        if create:
            g.save()
