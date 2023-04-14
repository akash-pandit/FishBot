# FishBot

FishBot is a 'pilot' discord bot for me to learn how to write a bot through hands-on experience.

This bot is written in python using discord's discord.py library.

What I have learned so far through this project:
- handling environment variables in python
- asynchronous programming in python (coroutines)
- implementing python decorators
- (discord.py) implementing slash commands
- (discord.py) implementing permission-locked commands

### Bot Functionality:
FishBot comes with a variety of slash commands executable through the discord client by users of varying permission levels:

/add_trusted - Only I can run this command, "trusts" a discord user to run trusted level commands through the bot by manipulating a list  of user IDs in .env

/remove_trusted - Only I can run this command, "un-trusts" a discord user who is currently "trusted", through the bot by manipulating a list of user IDs in .env

/qotd - returns the current question of the day (qotd)

/setqotdchannel - (trusted level command) designates a channel to be the channel where the qotd will be displayed by grabbing the channel id and storing it in .env

/addqotd (question) - (trusted level command) adds a new qotd (question) to qotd.txt

/resetqotd - (trusted level command) picks a qotd different from the current qotd from qotd.txt and designates it the new qotd

/removeqotd - (trusted level command) removes the current qotd from qotd.txt and resets the qotd to a new qotd

/jerma - added due to a request of a friend, the bot links a tenor GIF of content creator jerma eating a burger

/tbd - the bot returns a bulleted list of things I would like to add to it

/exit - Only I can run this command, runs the python quit() function and the bot feels sleepy... and terminates
