
import emoji
from loguru import logger


from src.bot import bot
from src.constants import keyboards, keys, states
from src.filters import IsAdmin
from src.db import db


class Bot:
    """
    Template for telegram bot.
    """
    def __init__(self, telebot):
        self.bot = telebot

        # add custom filters

        # register handlers
        self.handlers()

        # run bot
        logger.info('Bot is running...')
        self.bot.infinity_polling()

    def handlers(self):
        
        @self.bot.message_handler(commands=['start'])
        def start(message):
                self.bot.send_message(message.chat.id, f"Howdy, how are you doing {message.chat.first_name}?",reply_markup=keyboards.main)
                
                db.users.update_one(
                {'chat.id:': message.chat.id}, 
                {'$set' :message.json},
                 upsert=True
                 )
                self.update_state(message.chat.id, states.main)



      

        @self.bot.message_handler(text=[keys.random_connect])
        def random_connect(message):
            """
            Randomly connect to another user.
            """
            self.send_message(
                message.chat.id,
                ':busts_in_silhouette: Connecting you to a random stranger...',
                reply_markup=keyboards.exit
            )
            self.update_state(message.chat.id, states.random_connect)

            other_user = db.users.find_one(
                {
                    'state': states.random_connect,
                    'chat.id': {'$ne': message.chat.id}
                }
            )

            if not other_user:
                return
            # update other user state
            self.update_state(other_user["chat"]["id"], states.connected)
            self.send_message(
                other_user["chat"]["id"],
                f'Connected to {other_user["chat"]["id"]}...'
            )

            # update current user state
            self.update_state(message.chat.id, states.connected)
            self.send_message(
                message.chat.id,
                f'Connected to {other_user["chat"]["id"]}...'
            )

            # store connected users
            db.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': {'connected_to': other_user["chat"]["id"]}}
            )
            db.users.update_one(
                {'chat.id': other_user["chat"]["id"]},
                {'$set': {'connected_to': message.chat.id}}
            )

        @self.bot.message_handler(text=[keys.exit])
        def exit(message):
            """
            Exit from chat or connecting state.
            """
            self.send_message(
                message.chat.id,
                keys.exit,
                reply_markup=keyboards.main
            )
            self.update_state(message.chat.id, states.main)

            # get connected to user
            other_user =db.users.find_one(
                {'chat.id': message.chat.id}
            )
            if not other_user.get('connected_to'):
                return

            # update connected to user state and terminate the connection
            other_chat_id = other_user['connected_to']
            self.update_state(other_chat_id, states.main)
            self.send_message(
                other_chat_id,
                keys.exit,
                reply_markup=keyboards.main
            )

            # remove connected users
            db.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': {'connected_to': None}}
            )
            db.users.update_one(
                {'chat.id': other_chat_id},
                {'$set': {'connected_to': None}}
            )
            




           





        @self.bot.message_handler(func=lambda ـ: True)
        def echo(message):

            user = db.users.find_one({'chat.id': message.chat.id})
            if user['state'] != states.connected or  user['connected_to'] is None:
                return


            self.send_message(user['connected_to'], message.text)

            

    def send_message(self, chat_id, text, reply_markup=None, emojize=True):
        """
        Send message to telegram bot.
        """
        if emojize:
            text = emoji.emojize(text, use_aliases=True)

        self.bot.send_message(chat_id, text, reply_markup=reply_markup)
    def update_state(self, chat_id, state ):
        """
        Update user state in database.
        """
        db.users.update_one(
            {'chat.id': chat_id},
            {'$set': {'state': state}}
        )

if __name__ == '__main__':
    logger.info('Bot started')
    nashenas_bot = Bot(telebot=bot)
    nashenas_bot.run()
