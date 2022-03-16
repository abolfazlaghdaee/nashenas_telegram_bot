from types import SimpleNamespace

from emoji import demojize

from src.utils.keyboard import create_keyboard
import emoji

keys = SimpleNamespace(
    settings=emoji.emojize(':gear: Settings'),
    exit=emoji.emojize(':cross_mark: Exit'),
    random_connect = emoji.emojize(':bust_in_silhouette: Random connect'),
    
    
)

keyboards = SimpleNamespace(
    main=create_keyboard(keys.settings, keys.random_connect),
    exit = create_keyboard(keys.exit)
)


states = SimpleNamespace(
       random_connect = "Random connect",
       main = "main",
       connected = 'connected'
)

