import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import datetime

# --- CONFIGURAZIONE ---
TOKEN = ""
ID_RUOLO_STAFF = 1434510519737385030 
ID_CATEGORIA_TICKET = 1430421191230754846 

blacklist_ticket = []
warns_staff = {} 

class MetaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        await self.tree.sync()

bot = MetaBot()

# --- VIEW MATRIMONIO ---
class MarryView(discord.ui.View):
    def __init__(self, author, target):
        super().__init__(timeout=60)
        self.author, self.target = author, target

    @discord.ui.button(label="Accetto ❤️", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.target: return
        emb = discord.Embed(title="💖 Matrimonio Celebrato!", description=f"Festeggiamo l'unione tra **{self.author.display_name}** e **{self.target.display_name}**! 🎉", color=0xff69b4)
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="Rifiuto 💔", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.target: return
        await interaction.response.edit_message(content=f"💔 {self.author.mention}, è stato un secco NO.", embed=None, view=None)

# --- VIEW TICKET ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi Ticket 🔒", style=discord.ButtonStyle.danger, custom_id="close_btn_global")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ Chiusura del ticket in corso...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_tk(self, interaction, name, emoji, desc):
        if interaction.user.id in blacklist_ticket:
            return await interaction.response.send_message("❌ Sei in blacklist.", ephemeral=True)

        guild = interaction.guild
        staff_role = guild.get_role(ID_RUOLO_STAFF)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        chan = await guild.create_text_channel(name=f"{emoji}-{name}-{interaction.user.name}", overwrites=overwrites, category=guild.get_channel(ID_CATEGORIA_TICKET))
        await interaction.response.send_message(f"✅ Ticket creato: {chan.mention}", ephemeral=True)
        emb = discord.Embed(title=f"{emoji} Supporto {name.upper()}", description=f"Ciao {interaction.user.mention},\n{desc}", color=0x2b2d31)
        await chan.send(embed=emb, view=CloseTicketView())

    @discord.ui.button(label="Supporto Modalità", style=discord.ButtonStyle.success, emoji="🎮", custom_id="tk_mod")
    async def tk_mod(self, i, b): await self.create_tk(i, "modalità", "🎮", "Problemi tecnici o bug in-game.")
    @discord.ui.button(label="Supporto Account", style=discord.ButtonStyle.primary, emoji="🔑", custom_id="tk_acc")
    async def tk_acc(self, i, b): await self.create_tk(i, "account", "🔑", "Problemi di login o dati.")
    @discord.ui.button(label="Richiesta Rimborso", style=discord.ButtonStyle.secondary, emoji="💰", custom_id="tk_rimb")
    async def tk_rimb(self, i, b): await self.create_tk(i, "rimborso", "💰", "Invia ricevute per rimborsi.")
    @discord.ui.button(label="Candidature", style=discord.ButtonStyle.secondary, emoji="📝", custom_id="tk_cand")
    async def tk_cand(self, i, b): await self.create_tk(i, "candidatura", "📝", "Invia il tuo modulo staff.")
    @discord.ui.button(label="Segnalazioni", style=discord.ButtonStyle.success, emoji="📸", custom_id="tk_rep")
    async def tk_rep(self, i, b): await self.create_tk(i, "segnalazioni", "📸", "Segnala giocatori o bug.")

# --- COMANDI SOCIAL ---
@bot.tree.command(name="marry", description="Fai una proposta di matrimonio")
async def marry(interaction: discord.Interaction, utente: discord.Member):
    if utente == interaction.user: return await interaction.response.send_message("❌", ephemeral=True)
    emb = discord.Embed(title="💍 Proposta", description=f"{utente.mention}, accetti {interaction.user.mention}?", color=0xff69b4)
    await interaction.response.send_message(embed=emb, view=MarryView(interaction.user, utente))

@bot.tree.command(name="throw", description="Lancia un oggetto con effetti casuali")
async def throw(interaction: discord.Interaction, utente: discord.Member):
    items = [("🏗️ un'incudine", 0xffd700), ("🐟 un pesce", 0x00ff00), ("⌨️ una tastiera", 0x5865F2), ("💥 un creeper", 0xff0000)]
    obj, color = random.choice(items)
    luck = random.randint(1, 100)
    
    if luck > 80: res = f"🔥 **CRITICO!** {interaction.user.mention} ha distrutto {utente.mention} con {obj}!"
    elif luck > 30: res = f"🎯 {interaction.user.mention} ha colpito {utente.mention} con {obj}."
    else: res = f"💨 {interaction.user.mention} ha lanciato {obj} ma ha mancato il bersaglio!"
    
    await interaction.response.send_message(embed=discord.Embed(description=res, color=color))

# --- COMANDI ADMIN & BLACKLIST ---
@bot.tree.command(name="blacklist_ticket", description="Banna utente dai ticket")
@app_commands.checks.has_permissions(administrator=True)
async def bl_add(interaction: discord.Interaction, utente: discord.Member):
    if utente.id not in blacklist_ticket: blacklist_ticket.append(utente.id)
    await interaction.response.send_message(f"🚫 {utente.display_name} bloccato.", ephemeral=True)

@bot.tree.command(name="unblacklist_ticket", description="Sblocca utente dai ticket")
@app_commands.checks.has_permissions(administrator=True)
async def bl_rem(interaction: discord.Interaction, utente: discord.Member):
    if utente.id in blacklist_ticket: blacklist_ticket.remove(utente.id)
    await interaction.response.send_message(f"✅ {utente.display_name} sbloccato.", ephemeral=True)

@bot.tree.command(name="warn_staff", description="Ammonisce uno staffer")
@app_commands.checks.has_permissions(administrator=True)
async def warn_staff(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    warns_staff[membro.id] = warns_staff.get(membro.id, 0) + 1
    count = warns_staff[membro.id]
    emb = discord.Embed(title="⚠️ Staff Warning", description=f"**Staffer:** {membro.mention}\n**Motivo:** {motivo}\n**Warn:** {count}/3", color=0xffa500)
    await interaction.response.send_message(embed=emb)
    if count >= 3: await interaction.channel.send(f"🚨 {membro.mention} ha raggiunto la soglia massima di warn!")

@bot.tree.command(name="clear", description="Pulisce chat")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, quantità: int):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=quantità)
    await interaction.followup.send("🧹 Chat pulita.", ephemeral=True)

@bot.tree.command(name="setup_ticket", description="Pannello Ticket")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="🎫 Supporto AethonMC", description="Usa i bottoni per assistenza.", color=0x2b2d31)
    await interaction.channel.send(embed=emb, view=TicketView())
    await interaction.response.send_message("Inviato.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Online: {bot.user}")

bot.run(TOKEN)

