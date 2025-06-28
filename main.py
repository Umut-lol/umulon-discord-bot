import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
from PIL import Image, ImageDraw, ImageFont
import tempfile
from datetime import datetime, timedelta, timezone

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Cooldown per guild/server for /stupid_pings
last_stupid_ping_time = {}

@bot.event
async def on_ready():
    print(f"We are ready, {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name="ping", description="Check if Umulon is awake.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! Umulon is here.")

@bot.tree.command(name="rules", description="Ask the prioritized rule.")
async def rules(interaction: discord.Interaction):
    await interaction.response.send_message("Just be cool to others, or I'll kill you.")

@bot.tree.command(name="stupid_pings", description="Stupids the ping")
async def stupid_pings(interaction: discord.Interaction):
    global last_stupid_ping_time
    now = datetime.now(timezone.utc)

    guild_id = interaction.guild.id
    if guild_id in last_stupid_ping_time and now - last_stupid_ping_time[guild_id] < timedelta(hours=1):
        remaining = timedelta(hours=1) - (now - last_stupid_ping_time[guild_id])
        total_seconds = int(remaining.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        time_left = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
        await interaction.response.send_message(
            f"The stupid ping has already been used recently. Try again in {time_left}.",
            ephemeral=True
        )
        return

    last_stupid_ping_time[guild_id] = now

    role = discord.utils.get(interaction.guild.roles, name="stupid pings")
    if not role:
        await interaction.response.send_message("The role 'stupid pings' does not exist.", ephemeral=True)
        return

    try:
        # Temporarily make the role mentionable
        await role.edit(mentionable=True, reason="Temporarily enabling mention for stupid_pings command")
        allowed = discord.AllowedMentions(roles=[role])
        await interaction.response.send_message(
            content=f"{role.mention} has been stupidly pinged by {interaction.user.mention}",
            allowed_mentions=allowed
        )
    finally:
        # Revert the mentionable state
        await role.edit(mentionable=False, reason="Reverting mentionable after stupid_pings command")

@bot.tree.command(name="shitspire", description="Unfiltered, incoherent wisdom from the dumpster gods.")
async def shitspire(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        beginnings = [
            "Once upon a time", "like", "Honestly,", "No cap,", "Listen,", "Deadass,",
            "One time,", "A legend says", "It used to be like", "In the alley behind Taco Bell,", "I was born ready to",
        ]
        subjects = [
            "a raccoon with Wi-Fi", "your ex", "Shrek's third cousin",
            "a sentient beanbag", "Gandalf on ketamine", "a soggy Big Mac",
            "that creepy doll from grandma's attic", "my sleep paralysis demon",
            "a microwaved fork", "the ghost of Blockbuster"
        ]
        verbs = [
            "yeeted itself", "gave birth to ideas", "started screaming", "committed tax fraud",
            "teleported behind me", "challenged gravity", "did Fortnite dances", "ate drywall",
            "sniffed glue", "vibed aggressively"
        ]
        objects = [
            "for a Klondike bar", "in front of 12 ducks", "while on fire", "with no context",
            "", "at the speed of cringe", "into the 5th layer of hell",
            "in my DMs", "next to a urinal", "because why not"
        ]
        endings = [
            "and honestly? Mood.", "Jesus wept.", "no thoughts, only beans.",
            "this is why we can't have nice things.", "the prophecy was true.",
            "don’t ask me why.", "the vibes were rancid.", "therapist left the chat.",
            "We too aspire to that energy.", "and that’s how democracy works."
        ]

        text = f"{random.choice(beginnings)} {random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}, {random.choice(endings)}"

        scenery_dir = r"C:\Users\PC\Desktop\DiscordBot\scenery"
        bg_path = os.path.join(scenery_dir, random.choice(os.listdir(scenery_dir)))
        image = Image.open(bg_path).convert("RGBA")

        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", size=20)
        except IOError:
            font = ImageFont.load_default()

        def get_text_size(font, text):
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]

        def wrap_text(text, font, max_width):
            lines = []
            words = text.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                w, _ = get_text_size(font, test_line)
                if w <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            return lines

        lines = wrap_text(text, font, image.size[0] - 40)
        y_text = image.size[1] // 2 - len(lines) * 20

        for line in lines:
            w, h = get_text_size(font, line)
            draw.text(
                ((image.size[0] - w) / 2, y_text),
                line,
                font=font,
                fill="white",
                stroke_width=2,
                stroke_fill="black"
            )
            y_text += h + 5

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image_path = tmp.name
            image.save(image_path)

        await interaction.followup.send(file=discord.File(image_path))

    except Exception as e:
        await interaction.followup.send(f"Oops, something went wrong:\n```{e}```")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "i love you umulon" in message.content.lower():
        await message.channel.send(f"{message.author.mention} :3")

    if bot.user.mentioned_in(message):
        random_replies = [
            "Makes sense.",
            "Hmm, interesting.",
            "Well, okay then!",
            "I’ll take that personally.",
            "Could be worse!",
            "Thanks for sharing!",
            "Noted.",
            "I'm listening!",
            "What's up?",
            "Tell me more!",
            "Weirdo...",
            "I'm more into boys.",
            "I'm more into girls.",
        ]
        await message.channel.send(random.choice(random_replies))

    if "surprise me" in message.content.lower():
        action_replies = [
            "*Dies*",
            "Ok *hands you a bomb*",
            "*No.*",
            "*explodes*",
            "*Kills you to death*",
            "Huh?",
            "Um",
            "*hands you a rubber duck and walks away*",
            "fuck you",
            "*logs off*",
        ]
        await message.channel.send(random.choice(action_replies))

    await bot.process_commands(message)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)