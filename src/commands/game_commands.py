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
    
    def parse_players(self, players_str: str) -> tuple[list, dict]:
        """
        Parse player string to get list of players and pre-assigned lanes.
        
        Args:
            players_str (str): Comma-separated list of players, optionally with pre-assigned lanes
            
        Returns:
            tuple[list, dict]: List of players and dictionary of pre-assigned lanes
        """
        # Split players by comma and clean up whitespace
        player_list = [p.strip() for p in players_str.split(',')]
        
        # Define all possible lanes
        lanes = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
        
        # Initialize pre-assigned lanes dictionary
        pre_assigned = {}
        clean_players = []
        
        for player in player_list:
            # Check if player has a pre-assigned lane
            if '-' in player:
                name, lane = [p.strip() for p in player.split('-')]
                # Convert lane to proper format (first letter uppercase)
                lane = lane.capitalize()
                if lane in lanes:
                    pre_assigned[name] = lane
                    clean_players.append(name)
                else:
                    clean_players.append(player)
            else:
                clean_players.append(player)
        
        return clean_players, pre_assigned
    
    @commands.command(name='team')
    async def team_command(self, ctx, *, players: str):
        """
        Randomly assign players to League of Legends lanes.
        Players can have pre-assigned lanes using format: player-lane
        Example: !team alice,bob-jungle,steve,jeremy
        
        Args:
            ctx (commands.Context): Command context
            players (str): Comma-separated list of players (2-5 players)
        """
        # Parse players and get pre-assigned lanes
        player_list, pre_assigned = self.parse_players(players)
        
        # Validate number of players
        if len(player_list) < 2:
            await ctx.send("You need at least 2 players to form a team!")
            return
        if len(player_list) > 5:
            await ctx.send("You can only have up to 5 players in a team!")
            return
        
        # Define all possible lanes
        lanes = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
        
        # Remove pre-assigned lanes from available lanes
        available_lanes = [lane for lane in lanes if lane not in pre_assigned.values()]
        
        # Randomly shuffle remaining players
        remaining_players = [p for p in player_list if p not in pre_assigned]
        random.shuffle(remaining_players)
        
        # Create assignments
        assignments = []
        
        # First add pre-assigned players
        for player, lane in pre_assigned.items():
            assignments.append(f"{lane}: {player}")
        
        # Then add remaining players to random lanes
        for i, player in enumerate(remaining_players):
            if i < len(available_lanes):
                assignments.append(f"{available_lanes[i]}: {player}")
        
        # Create embed for better presentation
        embed = discord.Embed(
            title="League of Legends Team Assignment",
            description="Here's your team composition!",
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
        Players can have pre-assigned lanes using format: player-lane
        Example: !assign alice,bob-jungle,steve,jeremy
        
        Args:
            ctx (commands.Context): Command context
            players (str): Comma-separated list of players (2-5 players)
        """
        # Parse players and get pre-assigned lanes
        player_list, pre_assigned = self.parse_players(players)
        
        # Validate number of players
        if len(player_list) < 2:
            await ctx.send("You need at least 2 players to form a team!")
            return
        if len(player_list) > 5:
            await ctx.send("You can only have up to 5 players in a team!")
            return
        
        # Define all possible lanes
        lanes = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
        
        # Remove pre-assigned lanes from available lanes
        available_lanes = [lane for lane in lanes if lane not in pre_assigned.values()]
        
        # Randomly shuffle remaining players
        remaining_players = [p for p in player_list if p not in pre_assigned]
        random.shuffle(remaining_players)
        
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
                    
                    # First add pre-assigned players
                    for player, lane in pre_assigned.items():
                        # Get 3 random champions
                        suggested_champs = random.sample(champions, 3)
                        assignments.append({
                            'lane': lane,
                            'player': player,
                            'champions': [champ['name'] for champ in suggested_champs]
                        })
                    
                    # Then add remaining players to random lanes
                    for i, player in enumerate(remaining_players):
                        if i < len(available_lanes):
                            # Get 3 random champions
                            suggested_champs = random.sample(champions, 3)
                            assignments.append({
                                'lane': available_lanes[i],
                                'player': player,
                                'champions': [champ['name'] for champ in suggested_champs]
                            })
                    
                    # Create embed for better presentation
                    embed = discord.Embed(
                        title="League of Legends Team Assignment",
                        description="Here's your team composition with champion suggestions!",
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