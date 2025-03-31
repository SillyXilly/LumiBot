"""
Game-related commands for the Discord bot.
"""
import discord
from discord.ext import commands
import random
import aiohttp
import json
from src.config import DATA_DRAGON_CHAMPION_URL

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
    
    @commands.command(name='assign')
    async def assign_command(self, ctx, *, players: str):
        """
        Randomly assign players to League of Legends lanes and suggest champions.
        
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
        
        # Fetch champion data from Data Dragon API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DATA_DRAGON_CHAMPION_URL) as response:
                    if response.status != 200:
                        await ctx.send("Failed to fetch champion data. Please try again later.")
                        return
                    
                    champion_data = await response.json()
                    champions = list(champion_data['data'].values())
                    
                    # Create assignments with champion suggestions
                    assignments = []
                    for i, player in enumerate(player_list):
                        lane = lanes[i]
                        # Get 3 random champions
                        suggested_champs = random.sample(champions, 3)
                        assignments.append({
                            'lane': lane,
                            'player': player,
                            'champions': [champ['name'] for champ in suggested_champs]
                        })
                    
                    # Create embed for better presentation
                    embed = discord.Embed(
                        title="League of Legends Team Assignment",
                        description="Here's your randomly assigned team composition with champion suggestions!",
                        color=discord.Color.blue()
                    )
                    
                    # Add assignments to embed
                    for assignment in assignments:
                        # Format champion suggestions
                        champs_str = " | ".join(assignment['champions'])
                        embed.add_field(
                            name=f"{assignment['lane']}: {assignment['player']}", 
                            value=f"Suggested champions: {champs_str}", 
                            inline=False
                        )
                    
                    # Add footer with player count
                    embed.set_footer(text=f"Total Players: {len(player_list)}")
                    
                    await ctx.send(embed=embed)
                    
        except Exception as e:
            print(f"Error fetching champion data: {e}")
            await ctx.send("An error occurred while fetching champion data. Please try again later.")

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(GameCommands(bot)) 