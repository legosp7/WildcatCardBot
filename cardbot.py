# bot.py
import asyncio
import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
import datetime
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?',intents=intents)
SEASON = 'season1' #hardcode this
rates = {"common":0.60,"rare":0.30,"epic":0.09,"legendary":0.01}

class Card:
    def __init__(self, id, name, rarity, image) -> None:
        self._id = id
        self._name = name
        self._rarity = rarity
        self._image = image
    def get_name(self):
        return self._name
    def get_rarity(self):
        return self._rarity
    def get_image(self):
        return self._image
    def get_id(self):
        return self._id

class CardTable:
    def __init__(self) -> None:
        self._common = []
        self._rare = []
        self._epic = []
        self._legendary = []
    def get_common(self):
        return self._common
    def get_rare(self):
        return self._rare
    def get_epic(self):
        return self._epic
    def get_legendary(self):
        return self._legendary
    def set_card(self,card):
        x = card.get_rarity()
        if x == 'common':
            self._common.append(card)
        elif x == 'rare':
            self._rare.append(card)
        elif x == 'epic':
            self._epic.append(card)
        elif x == 'legendary':
            self._legendary.append(card)

def retCard(cardtable, id):
    for obj in cardtable.get_common():
        if str(obj.get_id()) == str(id):
            return obj
    for obj in cardtable.get_rare():
        if str(obj.get_id()) == str(id):
            return obj
    for obj in cardtable.get_epic():
        if str(obj.get_id()) == str(id):
            return obj
    for obj in cardtable.get_legendary():
        if str(obj.get_id()) == str(id):
            return obj

TableofCards = CardTable()

#load cards on startup
cards = open(f'{SEASON}/cardlist.csv','r+')
for line in cards:
    if line[0] != "#":
        line = line.strip().split(',')
        tempCard = Card(line[0],line[1],line[2],line[3])
        TableofCards.set_card(tempCard)

print(TableofCards.get_common())
print(TableofCards.get_rare())
print(TableofCards.get_epic())
print(TableofCards.get_legendary())

#pull a card from the table
@bot.command()
async def pullcard(ctx):
    if ctx.author.id == 381325561655721985:
        await ctx.send("fuck you Jack")
    else:
        #create/open server + userid file. we have to initilze it here for some reason
        fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'a')
        fileopen.close()
        #now we can open
        readopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'a')
        print(ctx.author.id)
        print("Breakpoint!")
        pull = round(random.uniform(0.01,1.00),2)
        print(pull)
        '''
        rate error checking

        print(1.00-rates['common'])
        print(rates['rare'])
        print(rates['epic'])
        print(rates['legendary'])'''
        #this'll have to be rewritten eventually for better logic
        if pull >= 1.00-rates['common']:
            pull2 = random.randint(0,len(TableofCards.get_common())-1)
            card = TableofCards.get_common()[pull2]
            readopen.write(card.get_id()+"\n")
        elif pull < 1.00-rates['common'] and pull > rates['epic']:
            pull2 = random.randint(0,len(TableofCards.get_rare())-1)
            card = TableofCards.get_rare()[pull2]
            readopen.write(card.get_id()+"\n")
        elif pull <= rates['epic'] and pull > rates['legendary']:
            pull2 = random.randint(0,len(TableofCards.get_epic())-1)
            card = TableofCards.get_epic()[pull2]
            readopen.write(card.get_id()+"\n")
        elif pull == rates['legendary']:
            pull2 = random.randint(0,len(TableofCards.get_legendary())-1)
            card = TableofCards.get_legendary()[pull2]
            readopen.write(card.get_id()+"\n")
        file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
        embed=discord.Embed(title=f"{ctx.message.author.display_name} pulled a {card.get_rarity()} {card.get_name()}!", color=0xFF5733)
        embed.set_image(url = f"attachment://{file.filename}")
        await ctx.send(file=file, embed=embed)

@bot.command()
async def collection(ctx):
    rarities = ["Legendary","Epic","Rare","Common"]
    authorcards = []
    authorcardcount = {}
    print(ctx.author.display_avatar.url)
    try:
        fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'r')
        for line in fileopen:
            cardname = retCard(TableofCards,line.strip())
            authorcards.append(cardname)
            if cardname in authorcardcount:
                authorcardcount[cardname] += 1
            else:
                authorcardcount[cardname] = 1
        print(authorcardcount)
        embed=discord.Embed(color=0xFF5733)
        avatar = ctx.author.display_avatar.url
        embed.set_author(name = f"{ctx.author.display_name}'s Collection!",icon_url=avatar)
        strs = {'common':'','rare':'','epic':'','legendary':''}
        #REDO THIS TOO
        for card in authorcardcount:
                strs[card.get_rarity()] += (f'{card.get_name()}     x{authorcardcount[card]}\n')
        #REDO THIS PART LATER SO IT ISN'T SO SCUFFED
        for rarity in rarities:
            if strs[rarity.lower()] != '':
                embed.add_field(name=rarity, value=strs[rarity.lower()], inline=False)
        await ctx.send(embed=embed)
    except:
        await ctx.send("You have no cards! Pull one to start your collection!")
        
    


#ping!
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

#some testing code
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)

    if 'happy birthday' in message.content.lower():
        await message.channel.send('Happy Birthday!')

    elif message.content == 'raise-exception':
        raise discord.DiscordException 
    
    await bot.process_commands(message)



bot.run(TOKEN)


