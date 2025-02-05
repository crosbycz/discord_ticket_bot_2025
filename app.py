

#   ████████╗██╗ ██████╗██╗  ██╗███████╗████████╗    ██████╗  ██████╗ ████████╗    ██╗   ██╗██████╗ 
#   ╚══██╔══╝██║██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝    ██║   ██║╚════██╗
#      ██║   ██║██║     █████╔╝ █████╗     ██║       ██████╔╝██║   ██║   ██║       ██║   ██║ █████╔╝
#      ██║   ██║██║     ██╔═██╗ ██╔══╝     ██║       ██╔══██╗██║   ██║   ██║       ╚██╗ ██╔╝██╔═══╝ 
#      ██║   ██║╚██████╗██║  ██╗███████╗   ██║       ██████╔╝╚██████╔╝   ██║        ╚████╔╝ ███████╗
#      ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝       ╚═════╝  ╚═════╝    ╚═╝         ╚═══╝  ╚══════╝
# Welcome to ticket bot V2.0.0
# made by me
# If you have any questions or problems, please contact me on discord: netext_office
# i write notes for u in the code, so u can customize it for your own and i explain here about the system
# dont delete .env and json files. json files is = database of the bot based on the text
# .env file is for your token of the bot .env file is hidden and secure the token of your bot
# Please install Packages for smooth run of the bot 
# Transcript contributor is chat_exporter on  github.com/1j01/chat-exporter
# have fun!                                                                                               
# If u dont know how to get url of images and ID of tickets read readme.md file
# If u open the code in visual studio code the orange text is (strings) u can customize it for your own
# other info in the readme.md
# Happy styling!
# This ticket bot gots updates and actualizations

# Support me : 
#https://cybrancee.com/client/aff.php?aff=325
# https://bunny.net/?ref=zxjk9bxh54
# https://datalix.eu/a/crosbyy 	





import nextcord # For install use: pip install nextcord
from nextcord.ext import commands
from nextcord import Embed, ButtonStyle, TextChannel, PermissionOverwrite
from nextcord.ui import Button, View, Modal, TextInput
import asyncio # for install use: pip install asyncio
from datetime import datetime, timedelta # for install use: pip install datetime
import chat_exporter # for install use: pip install chat_exporter
import io # for install use: pip install io
import json 
import os 
from dotenv import load_dotenv

load_dotenv()

# Configuration of bot
intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration of categories and channels read down => 
TICKET_CATEGORY_ID = enter_id  #=> ID category for opened tickets
LOG_CHANNEL_ID = enter_id      #=> ID channel for logs
PANEL_CHANNEL_ID = enter_id   #=> ID channel for panel
FEEDBACK_CHANNEL_ID = enter_id #=> ID channel for feedback
ALLOWED_ROLES = [                    #=> ID roles for allowed roles
    1525225205202562,      # Example role ID - replace with your own
    1525225205202562
]
token = os.getenv("BOT_TOKEN") # => Token of your bot setup token of your bot in .env file

# Dictionary to store the number of active tickets per user
user_ticket_counts = {}

# Dictionary to store cooldowns for the "Call Team" button
call_team_cooldowns = {}

# Load blocked users from blocked.json
blocked_users = []
if os.path.exists('blocked.json'):
    with open('blocked.json', 'r') as f:
        blocked_users = json.load(f)
        if not isinstance(blocked_users, list):
            blocked_users = []

# Load active tickets from tickets.json
active_tickets = {}
if os.path.exists('tickets.json'):
    with open('tickets.json', 'r') as f:
        active_tickets = json.load(f)
        if not isinstance(active_tickets, dict):
            active_tickets = {}

def save_tickets():
    with open('tickets.json', 'w') as f:
        json.dump(active_tickets, f)

# Initialize user_ticket_counts from active_tickets
for ticket in active_tickets.values():
    user_id = ticket["user_id"]
    user_ticket_counts[user_id] = user_ticket_counts.get(user_id, 0) + 1

class ConfirmCloseView(View):
    def __init__(self, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
# => [STYLING]
# Close button u can customize for your own
# label = name of your button ( write text by your style example : Close ticket)
# style = style of your button (red, green, blue, grey)
# emoji = emoji of your button (example: ✅)
    @nextcord.ui.button(label="Close ticket", style=ButtonStyle.red, emoji="✅")
    async def close_ticket(self, button: Button, interaction: nextcord.Interaction):
        # Open a modal to ask for a reason
        modal = CloseTicketModal(self.ticket_channel, interaction.user)
        await interaction.response.send_modal(modal)
# => [STYLING]
# Cancel button u can customize for your own
# label = name of your button ( write text by your style example : Dont close)
# style = style of your button (red, green, blue, grey)
# emoji = emoji of your button (example: 🔓)
    @nextcord.ui.button(label="Dont close", style=ButtonStyle.green, emoji="🔓")
    async def cancel_close(self, button: Button, interaction: nextcord.Interaction):
        embed = Embed(description="Ticket byl zanechán <:verifyvlc:1330645909763264563>", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CloseTicketModal(Modal):
    def __init__(self, ticket_channel, closer):
        super().__init__(title="Close Ticket")
        self.ticket_channel = ticket_channel
        self.closer = closer
        self.reason = TextInput(label="Reason", required=False)
        self.add_item(self.reason)  # Ensure the TextInput is added to the modal

    async def callback(self, interaction: nextcord.Interaction):
        reason = self.reason.value or "None"
        channel_name = self.ticket_channel.name
        closer_name = self.closer.name

        # Acknowledge the interaction to avoid timing out
        await interaction.response.defer()
        print(f"Interaction deferred for closing ticket: {channel_name}")

        # Notify the ticket channel that the ticket will be closed in 3 seconds
        close_warning_embed = Embed(description="<:markvlc:1331344586282631221> **pozor za 3 sekundy se zavře ticket**", color=0xff0000)
        await self.ticket_channel.send(embed=close_warning_embed)
        print(f"Sent close warning to ticket channel: {channel_name}")

        # Try to extract creator_id from the channel name
        try:
            creator_id = int(self.ticket_channel.name.split('-')[-1])
            print(f"Extracted creator ID: {creator_id}")
        except ValueError:
            creator_id = None
            print("Failed to extract creator ID")

        # Decrease the active ticket count for the creator
        if creator_id:
            if creator_id in user_ticket_counts:
                user_ticket_counts[creator_id] -= 1
                if user_ticket_counts[creator_id] <= 0:
                    del user_ticket_counts[creator_id]
                print(f"Updated user ticket count for creator ID: {creator_id}")

            # Remove the ticket from active_tickets and save the file
            if self.ticket_channel.id in active_tickets:
                del active_tickets[self.ticket_channel.id]
                save_tickets()
                print(f"Removed ticket from active tickets: {channel_name}")

            # Send DM to the ticket creator
            try:
                creator = await self.ticket_channel.guild.fetch_member(creator_id)
                if creator:
                    dm_embed = Embed(
                        title="Your ticket has been closed.",
                        description=f"Ticket has been closed by: {closer_name}\nReason: {reason}",
                        color=0xff0000
                    )
                    dm_embed.add_field(name="Rate us!", value="Please rate our support service:", inline=False)
                    dm_embed.set_footer(text="hazens tickets.gg")
                    rating_view = RatingView(creator, self.ticket_channel.guild, closer_name)
                    await creator.send(embed=dm_embed, view=rating_view)
                    print(f"Sent DM to ticket creator: {creator.name}")
            except Exception as e:
                print(f"Failed to send DM to the ticket creator: {e}")
                await interaction.followup.send(f"Failed to send DM to the ticket creator: {e}", ephemeral=True)

        # Creating of transcript
        transcript = await chat_exporter.export(self.ticket_channel)

        #  sending log to the log channel bcs the ticket is closed
        log_channel = self.ticket_channel.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            close_embed = Embed(
                title=f"Ticket closed by {closer_name} <:novlc:1331348383100702810>",
                color=0xff0000
            )
            close_embed.add_field(
                name="**Logged info <:markvlc:1331344586282631221>**",
                value=f"- <:arrowvlc:1330990464475594772> **User který vytvořil ticket:** {creator_id}\n- <:arrowvlc:1330990464475594772> **Jméno ticketu:** {channel_name}",
                inline=False
            )
            close_embed.set_footer(text="velcord.net ticket")
            
            # function of sending transcript to the log channel 
            if transcript:
                file = nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{channel_name}.html"
                )
                await log_channel.send(embed=close_embed, file=file)
                print("Sent transcript to log channel")
            else:
                await log_channel.send(embed=close_embed)
                print("Sent log to log channel without transcript")

        await asyncio.sleep(3)
        await self.ticket_channel.delete()
        print(f"Deleted ticket channel: {channel_name}")

class RatingView(View):
    def __init__(self, creator, guild, closer_name):
        super().__init__(timeout=None)
        self.creator = creator
        self.guild = guild
        self.closer_name = closer_name
        self.has_rated = False

        for i in range(1, 6):
            button = Button(label=str(i), style=ButtonStyle.primary, emoji="⭐")
            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, rating):
        async def callback(interaction: nextcord.Interaction):
            if self.has_rated:
                await interaction.response.send_message("You have already rated.", ephemeral=True)
                return
            self.has_rated = True

            feedback_channel = self.guild.get_channel(FEEDBACK_CHANNEL_ID)
            if feedback_channel is None:
                print("Feedback channel not found")
                await interaction.response.send_message("Error: Feedback channel not found.", ephemeral=True)
                return

            feedback_embed = Embed(
                title="New rate!",
                description=f"Uživatel od kterého přichází rate: {self.creator.name}\nPočet hvězd: {rating}",
                color=0x00ff00
            )
            feedback_embed.set_footer(text="hazens tickets")
            feedback_embed.set_image(url="https://media.discordapp.net/attachments/1327571827538792542/1331662288142467153/new_rating.png?ex=67926ea6&is=67911d26&hm=c0440170df9b51e0bc157b067015b7852cf31a91623cfaef73d914a5e7e52509&=&format=webp&quality=lossless&width=687&height=355")
            await feedback_channel.send(embed=feedback_embed)

            await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)
            print(f"User {self.creator.name} rated: {rating} stars")

        return callback

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
# => [STYLING]
# Create tciekt button u can customize for your own
# label = name of your button ( write text by your style example : Create ticket)
# style = style of your button (red, green, blue, grey)
# emoji = emoji of your button (example: 📨)
    @nextcord.ui.button(label="Create Ticket", style=ButtonStyle.green, emoji="📨")
    async def create_ticket(self, button: Button, interaction: nextcord.Interaction):
        user_id = interaction.user.id

        # Check if the user is blocked
        # [STYLING] u can customize for your own
        # U can customize and rewrite the text in the send_message
        # ephmeral = True - message will be visible only for the user who created the ticket
        # ephemeral = False - message will be visible for all users in the channel
        if user_id in blocked_users:
            await interaction.response.send_message("You cannot create a ticket because you are a blocked user ❌ ", ephemeral=True)
            return

        # Check if the user has reached the maximum number of tickets
        # [STYLING] u can customize for your own
        # U can customize and rewrite the text in the send_message
        # ephmeral = True - message will be visible only for the user who created the ticket
        # ephemeral = False - message will be visible for all users in the channel
        if user_ticket_counts.get(user_id, 0) >= 2:
            await interaction.response.send_message("You can't create multiple tickets You have reached the maximum number of tickets ❌", ephemeral=True)
            return

        # Increase the active ticket count for the user
        user_ticket_counts[user_id] = user_ticket_counts.get(user_id, 0) + 1

        # Create a ticket name based on the user's name and ID
        # U can customize if u know how to do it
        ticket_name = f"ticket-{interaction.user.name.lower()}-{interaction.user.id}"

        # Creating override permissions
        overwrites = {
            interaction.guild.default_role: PermissionOverwrite(read_messages=False),
            interaction.user: PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # To add permissions for enabled roles
        for role_id in ALLOWED_ROLES:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = PermissionOverwrite(read_messages=True, send_messages=True)

        # Verify that the TICKET_CATEGORY_ID refers to a valid category
        # [STYLING] u can customize for your own
        # U can customize and rewrite the text in the send_message
        # ephmeral = True - message will be visible only for the user who created the ticket
        # ephemeral = False - message will be visible for all users in the channel
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, nextcord.CategoryChannel):
            await interaction.response.send_message(
                "the specified category for tickets is not valid. Contact the administrator.",
                ephemeral=True
            )
            return

        # Create a new ticket channel
        ticket_channel = await category.create_text_channel(
            name=ticket_name,
            overwrites=overwrites
        )

        # Save the new ticket to active_tickets and save the file
        active_tickets[ticket_channel.id] = {
            "user_id": user_id,
            "channel_id": ticket_channel.id,
            "channel_name": ticket_channel.name
        }
        save_tickets()

       # [MEGA STYLING] u can customize for your own
       # tittle = title of your embed 
         # description = description of your embed
            # color = color of your embed
            # embed.set_footer = footer of your embed
            # embed.set_image = image of your embed
            #  close_button = button for close ticket label = name of your button ( write text by your style example : Close ticket)
            # call_team_button = button for call team label = name of your button ( write text by your style example : Call Team)
            # emoji of the buttons = emoji of your button (example: 🔒
        embed = Embed(
            title="Welcome in the ticket ✨",
            description=" Welcome to our tickets. We're always happy to help if we don't respond within 24 hours you can call our team. ",
            color=0x0099ff
        )
        embed.set_footer(text="your_footer.com", icon_url="enter url of icon image or delete it just")
        embed.set_image(url="enter url of your image")
        
        # Přidání tlačítek pro zavření a zavolání týmu
        close_button = Button(label="Close ticket", style=ButtonStyle.red, emoji="🔒")
        call_team_button = Button(label="Call Team", style=ButtonStyle.blurple, emoji="📞")
        # [STYLING] u can customize for your own
        # tittle = title of your embed
        # description = description of your embed
        # color = color of your embed
        # If u have hex code of your color just add 0x before your hex code and delete hastag # 
        async def close_callback(interaction: nextcord.Interaction):
            confirm_embed = Embed(
                title="Do you really want close the ticket?",
                description=" *If no, click on the don't close button if yes, click on close* ",
                color=0xff0000
            )
            await interaction.response.send_message(
                embed=confirm_embed,
                view=ConfirmCloseView(ticket_channel),
                ephemeral=True
            )
        
        async def call_team_callback(interaction: nextcord.Interaction):
            user_id = interaction.user.id
            now = datetime.now()
            cooldown_period = timedelta(hours=2)
            
            # Check if the user is on cooldown
            # [STYLING] u can customize for your own
            # u can customize send_messega dont delete reamining_time and etc... just change the text (strings)
            if user_id in call_team_cooldowns:
                last_called = call_team_cooldowns[user_id]
                if now - last_called < cooldown_period:
                    remaining_time = cooldown_period - (now - last_called)
                    await interaction.response.send_message(
                        f"You can't call the team again right away. Try for {remaining_time.seconds // 3600} hours and {(remaining_time.seconds // 60) % 60} minutes.",
                        ephemeral=True
                    )
                    return
            
            # Update the cooldown for the user
            call_team_cooldowns[user_id] = now
            # [STYLING] u can customize for your own
            # tittle = title of your embed
            # description = description of your embed
            # color = color of your embed
            general_embed = Embed(
                title="Calling staff team 📞",
                description="Our team has been alerted to this ticket. Please wait for a response. ",
                color=0x0099ff
            )
            await ticket_channel.send(content="@everyone", embed=general_embed)
            await interaction.response.send_message("Staff team has been notified ❗", ephemeral=True)

        close_button.callback = close_callback
        call_team_button.callback = call_team_callback

        action_view = View(timeout=None)
        action_view.add_item(close_button)
        action_view.add_item(call_team_button)

        # Send a message pinging the user who created the ticket along with the embed
        await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=action_view)

        await interaction.response.send_message(f"Ticket has been created: {ticket_channel.mention}", ephemeral=True)

        # Sending the ticket creation log
        # [STYLING] u can customize for your own
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = Embed(
                title="New ticket created ✨",
                color=0x00ff00
            )
            log_embed.add_field(
                name="**Logged info ℹ️  **",
                value=f"- <:arrowvlc:1330990464475594772> User that created ticket: {interaction.user.id}\n- > Name of the ticket: {ticket_name}",
                inline=False
            )
            log_embed.set_footer(text="your footer ticket")
            await log_channel.send(embed=log_embed)
@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

    # Odeslání hlavního embedu do kanálu
    channel = bot.get_channel(PANEL_CHANNEL_ID)
    if isinstance(channel, TextChannel):
        # Clear all messages in the channel before sending the panel message
        await channel.purge()
# [STYLING] u can customize for your own
# tittle = title of your embed
# description = description of your embed
# color = color of your embed
# embed.set_footer = footer of your embed
# embed.set_image = image of your embed
        embed = Embed(
            title="Support Ticket 📨",
            description="Welcome to the Ticket section 📨 If you need help or advice or to purchase a server you have come to the right place. To create a ticket click on the response below ⬇️",
            color=0x0099ff
        )
        embed.set_image(url="your image url here")
        embed.set_footer(text="🎫 your footer")
        await channel.send(embed=embed, view=TicketView())

    # Reinitialize ticket views for active tickets
    for ticket in active_tickets.values():
        ticket_channel = bot.get_channel(ticket["channel_id"])
        if ticket_channel:
            view = ConfirmCloseView(ticket_channel)
            await ticket_channel.send(view=view)

# Slash command to block a user
@bot.slash_command(name="block_user", description="Block a user from creating tickets")
@commands.has_permissions(administrator=True)
async def block_user(interaction: nextcord.Interaction, user_id: str):
    try:
        user_id = int(user_id)
        if user_id not in blocked_users:
            blocked_users.append(user_id)
            with open('blocked.json', 'w') as f:
                json.dump(blocked_users, f)
            await interaction.response.send_message(f"User with ID {user_id} has been blocked.", ephemeral=True)
        else:
            await interaction.response.send_message(f"User with ID {user_id} is already blocked.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Enter a valid user ID.", ephemeral=True)

# token for run bot
bot.run(token) # setup your token in .env file
