import discord
import os
from dotenv import load_dotenv, set_key
from random import randint


os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

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
async def on_ready():
    print(f'{client.user} is ready to rumble!')

"""
BOT LOADING - End -------------------------------------------------------------------------------------------



TRUSTED Commands - Begin ------------------------------------------------------------------------------------
"""
def is_author(interaction: discord.Interaction) -> bool:
    """checks if the user is the author"""
    return interaction.user.id == int(os.getenv('AUTHOR_ID'))


def is_trusted(interaction: discord.Interaction) -> bool:
    """checks if the user is a bot trusted user"""
    return str(interaction.user.id) in os.getenv('TRUSTED') or is_author(interaction)


@client.tree.command()
async def add_trusted(interaction: discord.Interaction, user_id: int) -> None:
    """adds a user to the trusted list"""
    if not is_author(interaction):
        await interaction.response.send_message("You don't have permission to run this command.")
    elif is_trusted(interaction):
        print(f'{interaction.user.id} already in TRUSTED')
        await interaction.response.send_message("This user is already trusted.")
    else:
        trusted = list(eval(os.getenv('TRUSTED')))
        trusted.append(int(user_id))
        set_key('.env', 'TRUSTED', str(trusted))
        interaction.response.send_message("Success")
    

@client.tree.command()
async def remove_trusted(interaction: discord.Interaction, user_id: int) -> None:
    if not is_author(interaction):
        await interaction.response.send_message("You don't have permission to run this command.")
    elif not is_trusted(interaction):
        await interaction.response.send_message("This user is not trusted.")
    else:
        trusted = set(eval(os.getenv('TRUSTED')))
        trusted.remove(int(interaction.user.id))
        set_key('.env', 'TRUSTED', str(trusted))
        interaction.response.send_message("Success")


"""
TRUSTED Commands - End --------------------------------------------------------------------------------------

---

QOTD Commands - Begin ---------------------------------------------------------------------------------------
"""
def gen_qotd_obj() -> list:
    with open('qotd.txt', 'r') as qotdfile:
        return [line[:-1] for line in qotdfile.readlines()]

#TODO: when resetting qotd, /qotd still returns old qotd
@client.tree.command(
        name='qotd',
        description='Output the question of the day'
        )
async def qotd(interaction) -> None:
    """Returns the Question of the Day"""
    await interaction.response.send_message(f'Current QOTD:\n**{os.getenv("QOTD")}**')


@client.tree.command(
        description='Set the QOTD channel to the current channel'
        )
async def setqotdchannel(interaction: discord.Interaction) -> None:
    if not interaction.user.guild_permissions.manage_channels and not is_author(interaction):
        await interaction.response.send_message(f'**You do not have sufficient server permissions to run this command!**' \
              '\nTo use this command, you need to have permission to manage this server\'s channels.')
        return 0

    channel = str(interaction.channel_id)
    set_key('.env', 'QOTD_CHANNEL', channel)
    await interaction.response.send_message(f'QOTD Channel set to **#{client.get_channel(int(channel))}**')
    print(f"{interaction.user.name} set the QOTD channel to #{client.get_channel(int(channel))} (id: {channel})")


@client.tree.command(
        description='currently dummy command, will add a QOTD to the list of questions'
        )
async def addqotd(interaction: discord.Interaction, question: str) -> None:
    """Add a question to the QOTD list"""
    if is_trusted(interaction):
        questions = gen_qotd_obj()
        questions.append(question)
        [q+'\n' for q in questions]

        with open('qotd.txt', 'w') as qotdfile:
            qotdfile.writelines(questions)
        set_key('.env', 'QOTD', resetqotd())
        await interaction.response.send_message(f'Question Added: {question}\n(A question wasn\'t added this is a placeholder)')


@client.tree.command(
        description="Reset the QOTD"
        )
async def resetqotd(interaction: discord.Interaction) -> None:
    if not is_trusted(interaction):
        await interaction.response.send_message("You do not have permission to run this command.")
        return

    questions = gen_qotd_obj()
    qotd_ind = randint(0, len(questions)-1)
    while questions[qotd_ind] == os.getenv('QOTD'):
        qotd_ind = randint(0, len(questions)-1)

    set_key('.env', 'QOTD', questions[qotd_ind])
    await interaction.response.send_message(f"QOTD has been reset. New QOTD:\n**{questions[qotd_ind]}**")


@client.tree.command(
        description='Deletes the current QOTD and resets it.'
)
async def removeqotd(interaction: discord.Interaction) -> None:
    if not is_trusted(interaction):
        await interaction.response.send_message("You do not have permission to run this command.")
    else:
        questions = gen_qotd_obj()
        old_qotd = os.getenv('QOTD')
        questions.remove(old_qotd)

        qotd_ind = randint(0, len(questions)-1)
        set_key('.env', 'QOTD', questions[qotd_ind])

        await interaction.response.send_message(f"QOTD Removed:\n**{old_qotd}**\nNew QOTD:\n**{questions[qotd_ind]}**")
        os.putenv()


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


@client.tree.command(description='shuts down the bot')
async def exit(interaction: discord.Interaction):
    if is_author(interaction):  # checks if the user is me (author), only I can run this
        await interaction.response.send_message(':zzz: I\'m feeling sleepy...')  # sends a little status message
        quit("Bot execution shut down by author")  # kills the script w/ string exit code
    else:
        print(interaction.user.id)
        await interaction.response.send_message('You\'re not that guy pal.')  # failure msg for anyone else running

client.run(bot_token)  # run the bot