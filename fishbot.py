import json
import discord
import os
from dotenv import load_dotenv, set_key
from random import randint


os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(override=True)

bot_token = str(os.getenv('TOKEN'))
MY_GUILD = discord.Object(id="1014601291755954236")


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

@client.event
async def on_ready() -> None:
    print(f'{client.user} is ready to rumble!')


def get_ext_vars() -> dict:
    with open('external_vars.json', 'r') as file:
        return dict(json.load(file))

"""
BOT LOADING - End -------------------------------------------------------------------------------------------



TRUSTED Commands - Begin ------------------------------------------------------------------------------------
"""
def is_author(interaction: discord.Interaction) -> bool:
    """checks if the user is the author"""
    return interaction.user.id == int(os.getenv('AUTHOR_ID'))


def is_user_trusted(interaction: discord.Interaction) -> bool:
    """checks if the user is a bot trusted user using a discord interaction input"""
    return interaction.user.id in get_ext_vars()['TRUSTED'] or is_author(interaction)


def is_id_trusted(user_id: int) -> bool:  
    """checks if the user is a bot trusted user using an integer input (the user ID)"""
    return int(user_id) in get_ext_vars()['TRUSTED'] or user_id == int(os.getenv('AUTHOR_ID'))


@client.tree.command()
async def add_trusted(interaction: discord.Interaction, user_id: str) -> None:
    """Adds a user to the trusted list, this command can only be run by the author."""

    if not is_author(interaction):  # catches non-author users running command
        print(f'Unauthorized user {interaction.user} ({interaction.user.id}) attempted running /add_trusted.')
        await interaction.response.send_message("You don't have permission to run this command.", ephemeral=True)

    elif is_id_trusted(int(user_id)):  # catches when author tries to trust someone already trusted
        print(f'Trusting Failed: {user_id} already in TRUSTED')  # log to stdout
        await interaction.response.send_message("This user is already trusted.", ephemeral=True)  # log to discord channel of execution

    else:  # no hiccups with trusting
        jsonfile = get_ext_vars()  # get dict of external vars
        jsonfile['TRUSTED'].append(int(user_id))  # add user id to list of trusted user ids
        with open('external_vars.json', 'w') as file:  
            json.dump(jsonfile, file, indent=4)  # rewrite external_vars.json with updated list of trusted user ids

        print(f'User {user_id} has been trusted.')  # log to stdout
        await interaction.response.send_message("Successfully trusted a user.", ephemeral=True)  # log to discord channel of execution
    

@client.tree.command()
async def remove_trusted(interaction: discord.Interaction, user_id: str) -> None:
    """Removes a user's trusted status, this command can only be run by the author."""

    if not is_author(interaction): # catches non-author users running command
        print(f'Unauthorized user {interaction.user} ({interaction.user.id}) attempted running /remove_trusted.')  # log to stdout
        await interaction.response.send_message("You don't have permission to run this command.", ephemeral=True)  # log to discord

    elif not is_id_trusted(user_id):  # catches when author tries remove trusted status from a user without trusted status
        print(f'Removal Failed: {user_id} was not in TRUSTED')  # log to stdout
        await interaction.response.send_message("This user is not trusted.", ephemeral=True)  # log to discord

    else:
        jsonfile = get_ext_vars()  # get dict of external vars
        jsonfile['TRUSTED'].remove(int(user_id))  # remove user id from list of trusted user ids
        with open('external_vars.json', 'w') as file:
            json.dump(jsonfile, file, indent=4)  # rewrite external_vars.json with updated list of trusted user ids

        print(f'User {user_id} has been un-trusted')  # log to stdout
        await interaction.response.send_message("Successfully revoked user's trusted status.", ephemeral=True)  # log to discord
        

"""
TRUSTED Commands - End --------------------------------------------------------------------------------------

---

QOTD Commands - Begin ---------------------------------------------------------------------------------------
"""
def gen_qotd_obj() -> list:
    with open('qotd.txt', 'r') as qotdfile:
        return [line[:-1] for line in qotdfile.readlines()]


@client.tree.command(
        name='qotd',
        description='Output the question of the day'
        )
async def qotd(interaction) -> None:
    """Returns the Question of the Day"""
    qotd_ = get_ext_vars()['QOTD']
    await interaction.response.send_message(f'Current QOTD:\n**{qotd_}**')


@client.tree.command(
        description='Set the QOTD channel to the current channel'
        )
async def setqotdchannel(interaction: discord.Interaction) -> None:
    """Set the discord channel where this command was called as the designated QOTD channel"""

    if not interaction.user.guild_permissions.manage_channels and not is_author(interaction):  # handles users with insufficient permissions
        await interaction.response.send_message(f'**You do not have sufficient server permissions to run this command!**' \
              '\nTo use this command, you need to have permission to manage this server\'s channels.', ephemeral=True)  # log to discord
        
    else:  # execute as planned
        channel = interaction.channel_id  # channel: the id of the channel in which the interaction occured
        jsonfile = get_ext_vars()  # getting the contents of external_vars.json as a dict jsonfile
        jsonfile['QOTD_CHANNEL'] = channel  # setting the new qotd channel in jsonfile
        channel_name = client.get_channel(channel)  # getting the name associated with channel (a channel id) as channel_name

        with open('external_vars.json', 'w') as file:
            json.dump(jsonfile, file, indent=4)  # rewrite external_vars.json with updated qotd channel id
        await interaction.response.send_message(f'QOTD Channel set to **#{channel_name}**')  # log to discord
        print(f"{interaction.user.name} set the QOTD channel to #{channel_name} (id: {channel})")  # log to stdout


@client.tree.command(
        description='currently dummy command, will add a QOTD to the list of questions'
        )
async def addqotd(interaction: discord.Interaction, question: str, setqotd: bool = False) -> None:
    """Add a question to the QOTD list"""

    if not is_user_trusted(interaction):  # handles unauthorized users
        print(f'Unauthorized user {interaction.user} ({interaction.user.id}) attempted running /addqotd.')  # log to stdout
        await interaction.response.send_message(f'You don\'t have permission to run this command!', ephemeral=True)  # log to discord

    else:  # executes as planned
        questions = gen_qotd_obj()  # retrieve list of questions from qotd.txt
        questions.append(question)  # add question to questions
        [q+'\n' for q in questions]  # give each question a newline character in prep for rewriting qotd.txt

        with open('qotd.txt', 'w') as qotdfile:
            qotdfile.writelines(questions)  # rewrites qotd.txt with new question
        
        new_qotd_str = ''  # initialize new_qotd_str, updates if setqotd is True
        if setqotd:
            jsonfile = get_ext_vars()  # get python dict from external_vars.json contents
            jsonfile['QOTD'] = question  # set current qotd to new qotd
            with open("external_vars.json", 'w') as file:
                json.dump(jsonfile, file, indent=4)  # update json file with updated jsonfile dict
            new_qotd_str = '\nQOTD set to the above question.'  # update new_qotd_str

        print(f'User {interaction.user} ({interaction.user.id}) added QOTD \"{question}\"')  # log stdout
        await interaction.response.send_message(f'Question Added to QOTD List: \n{question}' + new_qotd_str)
        # log discord


@client.tree.command(
        description="Reset the QOTD"
        )
async def resetqotd(interaction: discord.Interaction) -> None:
    if not is_user_trusted(interaction):
        await interaction.response.send_message("You do not have permission to run this command.", ephemeral=True)
    else:
        jsonfile = get_ext_vars()
        questions = gen_qotd_obj()
        qotd_ind = randint(0, len(questions)-1)
        while questions[qotd_ind] == jsonfile['QOTD']:
            qotd_ind = randint(0, len(questions)-1)
        jsonfile['QOTD'] = questions[qotd_ind]

        with open('external_vars.json', 'w') as file:
            json.dump(jsonfile, file, indent=4)  # rewrite the json file with the updated jsonfile dict object
        
        print(f"User {interaction.user} ({interaction.user.id}) reset the QOTD on {interaction.guild} ({interaction.guild.id})")
        # ^ log to stdout
        await interaction.response.send_message(f"QOTD has been reset. New QOTD:\n**{questions[qotd_ind]}**")  # log to discord


@client.tree.command(
        description='Deletes the current QOTD and resets it.'
)
async def removeqotd(interaction: discord.Interaction) -> None:
    if not is_user_trusted(interaction):
        await interaction.response.send_message("You do not have permission to run this command.", ephemeral=True)
    else:
        jsonfile = get_ext_vars()
        questions = gen_qotd_obj()
        old_qotd = jsonfile['QOTD']
        questions.remove(old_qotd)

        qotd_ind = randint(0, len(questions)-1)
        jsonfile['QOTD'] = questions[qotd_ind]
        
        with open("external_vars.json", 'w') as file:
            json.dump(jsonfile, file, indent=4)

        print(f'User {interaction.user} ({interaction.user.id}) removed qotd \"{old_qotd}\".')
        await interaction.response.send_message(f"QOTD Removed:\n**{old_qotd}**\nNew QOTD:\n**{questions[qotd_ind]}**")


@client.tree.command(
    description="Returns the current QOTD channel."
    )
async def getqotdchannel(interaction: discord.Interaction) -> None:
    jsonfile = get_ext_vars()  # load in external_vars.json as python dict
    channel_name = client.get_channel(jsonfile['QOTD_CHANNEL'])  # get discord channel name
    await interaction.response.send_message(f"This server's QOTD channel is **#{channel_name}**.", ephemeral=True)
    # log discord


"""
QOTD Commands - End ------------------------------------------------------------------------------------------
"""

@client.tree.command(description='jerma gif')
async def jerma(interaction):
    await interaction.response.defer()  # dummy cmd in case it's taking a while to load
    await interaction.followup.send('https://media.tenor.com/jOwV06mYU2YAAAAd/jerma-discord.gif')
    # loads gif of content creator jerma eating a sandwich


@client.tree.command(description='Lists things that are WIP or planned')
async def tbd(interaction):
    tbd_list = (
        "Add functionality for setting QOTD, exists as python func but not added as cmd w/ perms",
        "Add functionality for generating and outputting new QOTD at specified system time",
        "Add command to change bot's nickname to string of choice",
        "Allow /jerma to cycle between a selection of GIFs",
        "Create a /help command with a list of all commands, parameters, and functionalities"
    )
    msg = '**Things to be done:**'
    for i in tbd_list:
        msg += f'\n- {i}'  # add the contents of tbd list to msg
    await interaction.response.send_message(msg)


@client.tree.command(description='Returns a link to this bot\'s source code in its github repository')
async def src(interaction):
    await interaction.response.send_message('**View my source code here!**\nhttps://github.com/akash-pandit/FishBot')


@client.tree.command(description='shuts down the bot')
async def exit(interaction: discord.Interaction):
    if is_author(interaction):  # checks if the user is me (author), only I can run this
        await interaction.response.send_message(':zzz: I\'m feeling sleepy...')  # sends a little status message
        quit("Bot execution shut down by author")  # kills the script w/ string exit code
    else:
        print(f'Unauthorized user {interaction.user} ({interaction.user.id}) attempted running /exit.')
        await interaction.response.send_message('You\'re not that guy pal.', ephemeral=True)  # failure msg for anyone else running

client.run(bot_token)  # run the bot