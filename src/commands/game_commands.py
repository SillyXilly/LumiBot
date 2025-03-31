"""
Game-related commands for the Discord bot.
"""
import discord
from discord.ext import commands
import random

class GameCommands(commands.Cog):
    """
    Cog containing game-related commands.
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='team')
    async def team_command(self, ctx, *, players: str):
        """
        Randomly assign players to League of Legends lanes.
        
        Args:
            ctx (commands.Context): Command context
            players (str): Comma-separated list of players (2-5 players)
        """
        # Split players by comma and clean up whitespace
        player_list = [p.strip() for p in players.split(',')]
        
        # Validate number of players
        if len(player_list) < 2:
            await ctx.send("You need at least 2 players to form a team!")
            return
        if len(player_list) > 5:
            await ctx.send("You can only have up to 5 players in a team!")
            return
        
        # Define all possible lanes
        lanes = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
        
        # Randomly shuffle players
        random.shuffle(player_list)
        
        # Create assignments
        assignments = []
        for i, player in enumerate(player_list):
            assignments.append(f"{lanes[i]}: {player}")
        
        # Create embed for better presentation
        embed = discord.Embed(
            title="League of Legends Team Assignment",
            description="Here's your randomly assigned team composition!",
            color=discord.Color.blue()
        )
        
        # Add assignments to embed
        for assignment in assignments:
            embed.add_field(name=assignment.split(':')[0], value=assignment.split(':')[1], inline=True)
        
        # Add footer with player count
        embed.set_footer(text=f"Total Players: {len(player_list)}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(GameCommands(bot)) 