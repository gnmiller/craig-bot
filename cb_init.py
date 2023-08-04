import discord


class init_view(discord.ui.View):

    def __init__(self, bot, guild, timeout=360):
        self.bot = bot
        self.guild = guild
        self.timeout = timeout
        super().__init__()

    @discord.ui.button(label="Confirm",
                       row=0,
                       style=discord.ButtonStyle.success)
    async def confirm_callback(self, button, interaction):
        send_str = "OK! I will upgrade the server to a community!"
        await interaction.response.send_message(send_str)

    @discord.ui.button(label="Reject",
                       row=0,
                       style=discord.ButtonStyle.danger)
    async def reject_callback(self, button, interaction):
        send_str = "OK! I will NOT upgrade the server to a community!"
        await interaction.response.send_message(send_str)

