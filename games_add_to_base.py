from tg.models import Game


games = [
    'Warframe', 'Fortnite', 'Counter-Strike GO',
    'StarCraft2', 'Back4Blood', 'Sid Meier\'s Civilization 6',
    'Left 4 Dead 2', 'Empire Earth III'
    ]

for game in games:
    g, create = Game.object.get_or_create(
        title=game
    )
    if create:
        g.save()
