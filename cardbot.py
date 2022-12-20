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
cardvalues = {"common":10,"rare":25,"epic":50,"legendary":100}
packprices = {"Common Pack":40,"Rare Pack":100,"Epic Pack":200,"Legendary Pack":400}
cooldown = 0

class Card:
    def __init__(self, id, name, rarity, image,description,packs) -> None:
        self._id = id
        self._name = name
        self._rarity = rarity
        self._image = image
        self._description = description
        self._packs = packs
    def get_name(self):
        return self._name
    def get_rarity(self):
        return self._rarity
    def get_image(self):
        return self._image
    def get_id(self):
        return self._id
    def get_description(self):
        return self._description
    def get_packs(self):
        return self._packs

class CardTable:
    def __init__(self) -> None:
        self._cards = []
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
    def get_cards(self):
        return self._cards
    def set_card(self,card):
        self._cards.append(card)
        x = card.get_rarity()
        if x == 'common':
            self._common.append(card)
        elif x == 'rare':
            self._rare.append(card)
        elif x == 'epic':
            self._epic.append(card)
        elif x == 'legendary':
            self._legendary.append(card)

class User:
    def __init__(self) -> None:
        self._cards = 0
        self._cooldown = None
        #self._rank = None
        self._description = ''
    
class CardPack:
    def __init__(self,name) -> None:
        self.packname = name
        self.cost = 50
        self._cards = []
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
    def get_cards(self):
        return self._cards
    def set_card(self,card):
        self._cards.append(card)
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
    '''returns card object'''
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
#need a filler so i can loop later
cardpackNames = {}
cardpacks = []

#load cards on startup
cards = open(f'{SEASON}/cardlist.csv','r+')
for line in cards:
    if line[0] != "#":
        line = line.strip().split(',')
        tempCard = Card(line[0],line[1],line[2],line[3],line[6],line[7:])
        TableofCards.set_card(tempCard)
        for i in line[7:]: #change this as we add more stuff like descriptions
            packname = i.split(' ')
            packname = "".join(packname)
            if packname not in cardpackNames:
                specialcardpack = CardPack(i)
                specialcardpack.set_card(tempCard)
                cardpackNames[packname] = specialcardpack
            else:
                cardpackNames[packname].set_card(tempCard)


#pull a card from the table
@bot.command()
async def pullcard(ctx):
    '''
    Pulls a random card!
    '''
    #create server + userid file if it doesn't exist
    userprofopen = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'a') #1
    #create/open server + userid file for cards. we have to initilze it here for some reason
    fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'a') 
    fileopen.close()
    #now we can open
    cardnumopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'r')
    print(ctx.author.id)
    print("Breakpoint!")
    cardsnum = len(cardnumopen.readlines())
    userprofopen.write(str(cardsnum)+"\n") #write cardsnum
    userprofopen.close() #close 1
    #i wanted to use readlines() here but you can't on a csv file i guess
    #this part just shows the number of cards/time for each user
    userprofopen = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'r') #2
    userprofopen.readline()
    lastrolltime = userprofopen.readline() 
    print(lastrolltime)
    timeofroll = time.time()
    if lastrolltime == '':
        lastrolltime = time.time()-50000.0
    userprofopen.close() #3
    cardnumopen.close()
    print(timeofroll - float(lastrolltime))
    if timeofroll - float(lastrolltime) < cooldown:
        await ctx.send(f"You still have {int(float(lastrolltime)+cooldown - timeofroll)} seconds left before you can roll again!")
    else:
        userprofopen = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'w')
        userprofopen.write(str(cardsnum)+"\n")
        userprofopen.write(str(timeofroll)+"\n")
        userprofopen.close()
        readopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'a')
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



#gonna have to slim this function down later, prob break into different functions
@bot.command()
async def openpack(ctx,pack=''):
    '''pull from a pack (rarity)'''
    if pack == "":
        await ctx.send("Please enter a pack!")
        return
    try:
        userprofopen = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'r')
        proflist = []
        for line in userprofopen:
            proflist.append(line.strip())
        print(proflist)
        print(pack)
        pulledcards = []
        rarities = ["legendary","epic","rare","common"]
        if pack.lower() not in rarities:
            await ctx.send("Please try again with a valid card pack!")
            userprofopen.close()
        elif len(proflist) < 4:
            await ctx.send("You have no packs! Use ?buypack to purchase one!")
            userprofopen.close()
        else:
            packs = proflist[3].split(',')
            print(packs)
            if pack.lower() in packs:
                fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'a')
                cardraritiespulled = [] #for keeping track of rarity of cards pulled
                packs.remove(pack.lower())
                if pack.lower() == "legendary":
                    pull2 = random.randint(0,len(TableofCards.get_legendary())-1)
                    card = TableofCards.get_legendary()[pull2]
                    fileopen.write(card.get_id()+"\n")
                    cardraritiespulled.append(card.get_rarity())
                    pulledcards.append(card)
                    card = pulledcards[0]
                    file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
                    embed=discord.Embed(title=f"{ctx.message.author.display_name} pulled a {card.get_rarity()} {card.get_name()}!",color=0xFF5733)
                    embed.set_image(url = f"attachment://{file.filename}")
                    await ctx.send(file=file, embed=embed)
                else:
                    for i in range(5):
                        #guarantees
                        if i == 4 and (pack.lower() == "rare"):
                            if "rare" not in cardraritiespulled:
                                pull = round(random.uniform(0.01,0.40),2)
                            else:
                                pull = round(random.uniform(0.01,1.00),2)
                        elif i == 4 and (pack.lower() == "epic"):
                            if "rare" not in cardraritiespulled:
                                pull = round(random.uniform(0.01,0.09),2)
                            else:
                                pull = round(random.uniform(0.01,1.00),2)
                        else:
                            pull = round(random.uniform(0.01,1.00),2)
                        print(pull)
                        if pull >= 1.00-rates['common']:
                            pull2 = random.randint(0,len(TableofCards.get_common())-1)
                            card = TableofCards.get_common()[pull2]
                            fileopen.write(card.get_id()+"\n")
                            cardraritiespulled.append(card.get_rarity())
                            pulledcards.append(card)
                        elif pull < 1.00-rates['common'] and pull > rates['epic']:
                            pull2 = random.randint(0,len(TableofCards.get_rare())-1)
                            card = TableofCards.get_rare()[pull2]
                            fileopen.write(card.get_id()+"\n")
                            cardraritiespulled.append(card.get_rarity())
                            pulledcards.append(card)
                        elif pull <= rates['epic'] and pull > rates['legendary']:
                            pull2 = random.randint(0,len(TableofCards.get_epic())-1)
                            card = TableofCards.get_epic()[pull2]
                            fileopen.write(card.get_id()+"\n")
                            cardraritiespulled.append(card.get_rarity())
                            pulledcards.append(card)
                        elif pull == rates['legendary']:
                            pull2 = random.randint(0,len(TableofCards.get_legendary())-1)
                            card = TableofCards.get_legendary()[pull2]
                            fileopen.write(card.get_id()+"\n")
                            cardraritiespulled.append(card.get_rarity())
                            pulledcards.append(card)
                    card = pulledcards[0]
                    file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
                    embed=discord.Embed(title=f"{ctx.message.author.display_name} pulled a {card.get_rarity()} {card.get_name()}!", description="1/5" ,color=0xFF5733)
                    embed.set_image(url = f"attachment://{file.filename}")
                    view = packcardbuttons(pulledcards,ctx.message.author.display_name)
                    await ctx.send(file=file, embed=embed,view = view)
                userprofopen.close() 
                userprofwrite = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'w')
                for line in proflist[:3]: #change as prof changes - packs should be last
                    userprofwrite.write(line + "\n")
                userprofwrite.write(",".join(packs) + "\n")
                userprofwrite.close()
            else:
                await ctx.send("You don't own this pack!")
                userprofopen.close()
    except FileNotFoundError:
        await ctx.send("You don't have a profile! Use ?pullcard to get started!")    

@bot.command()
async def pullcollection(ctx,pack):
    '''pull 5 cards from a collection(rare guaranteed!)'''
    print(pack)
    pulledcards = []
    if pack not in cardpackNames:
        await ctx.send("Please try again with a valid card pack name!")
    else:
        fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'a')
        cardraritiespulled = [] #for keeping track of rarity of cards pulled
        for i in range(5):
            if i == 4:
                if "rare" not in cardraritiespulled:
                    pull = round(random.uniform(0.01,0.40),2)
                else:
                    pull = round(random.uniform(0.01,1.00),2)
            else:
                pull = round(random.uniform(0.01,1.00),2)
            print(pull)
            if pull >= 1.00-rates['common']:
                pull2 = random.randint(0,len(cardpackNames[pack].get_common())-1)
                card = cardpackNames[pack].get_common()[pull2]
                fileopen.write(card.get_id()+"\n")
                cardraritiespulled.append(card.get_rarity())
                pulledcards.append(card)
            elif pull < 1.00-rates['common'] and pull > rates['epic']:
                pull2 = random.randint(0,len(cardpackNames[pack].get_rare())-1)
                card = cardpackNames[pack].get_rare()[pull2]
                fileopen.write(card.get_id()+"\n")
                cardraritiespulled.append(card.get_rarity())
                pulledcards.append(card)
            elif pull <= rates['epic'] and pull > rates['legendary']:
                pull2 = random.randint(0,len(cardpackNames[pack].get_epic())-1)
                card = cardpackNames[pack].get_epic()[pull2]
                fileopen.write(card.get_id()+"\n")
                cardraritiespulled.append(card.get_rarity())
                pulledcards.append(card)
            elif pull == rates['legendary']:
                pull2 = random.randint(0,len(cardpackNames[pack].get_legendary())-1)
                card = cardpackNames[pack].get_legendary()[pull2]
                fileopen.write(card.get_id()+"\n")
                cardraritiespulled.append(card.get_rarity())
                pulledcards.append(card)
        card = pulledcards[0]
        file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
        embed=discord.Embed(title=f"{ctx.message.author.display_name} pulled a {card.get_rarity()} {card.get_name()}!", description="1/5" ,color=0xFF5733)
        embed.set_image(url = f"attachment://{file.filename}")
        view = packcardbuttons(pulledcards,ctx.message.author.display_name)
        await ctx.send(file=file, embed=embed,view = view)


@bot.command()
async def sell(ctx,id=""):
    '''Sell a card!'''
    if id == '':
        await ctx.send("Please enter a valid card ID!")
        return
    try:
        fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'r')
        cardsid = []
        cardscollection = []
        for line in fileopen:
            cardname = retCard(TableofCards,line.strip())
            cardsid.append(line.strip())
            cardscollection.append(cardname)
        fileopen.close()
        if id in cardsid:
            index = cardsid.index(id)
            cardsid.pop(index)
            cardsold = cardscollection.pop(index)
            fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'w')
            for ci in cardsid:
                fileopen.write(ci + "\n")
            fileopen.close()
            value = cardvalues[cardsold.get_rarity()]
            try:
                userprofopen = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'r')
                proflist = []
                for line in userprofopen:
                    proflist.append(line.strip())
                if len(proflist) < 3:
                    proflist.append(0)
                print(proflist)
                userprofopen.close()
                userprofwrite = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'w')
                proflist[2] = int(proflist[2]) + value
                for line in proflist: #change as prof changes - packs should be last
                    userprofwrite.write(str(line) + "\n")
                userprofwrite.close()
                await ctx.send(f"You have sold {cardsold.get_name()} for {value} gold!")
            except FileNotFoundError:
                await ctx.send("We don't have your profile! Use ?pullcard to start!")
        else:
            await ctx.send("You don't own this card!")
    except FileNotFoundError:
        await ctx.send("You have no cards! Pull one to start your collection!")

@bot.command()
async def buy(ctx):
    '''Buy a pack!'''
    try:
        userprofopen = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'r')
        proflist = []
        for line in userprofopen:
            proflist.append(line.strip())
        if len(proflist) < 3:
            proflist.append(0)
        userprofopen.close()
        embed = discord.Embed(title = "Pack Shop!", description= "Buy a card pack!", color = 0xFF5733)
        pricesstr = ''
        i = 1 #index for number
        for k,v in packprices.items():
            pricesstr += f'{i}. {k} - {v}\n'
            i += 1
        pricesstr += "5. Exit"
        embed.add_field(name = "Prices", value = pricesstr, inline=False)
        await ctx.send(embed=embed)
        def checkvalid(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        packreply = await bot.wait_for("message", check=checkvalid)
        pack = packreply.content
        boughtpack = ''
        if len(proflist) < 4:
            packlist = []
        else:
            packlist = proflist[3].split(',')
        if pack == "5":
            await ctx.send("Thank you for your patronage!")
            return
        elif pack == "1":
            if int(proflist[2]) >= packprices["Common Pack"]:
                proflist[2] = int(proflist[2]) - packprices["Common Pack"]
                packlist.append("common")
                boughtpack = "Common Pack"
            else:
                await ctx.send("You don't have enough gold!")
                return
        elif pack == "2":
            if int(proflist[2]) >= packprices["Rare Pack"]:
                proflist[2] = int(proflist[2]) - packprices["Rare Pack"]
                packlist.append("rare")
                boughtpack = "Rare Pack"
            else:
                await ctx.send("You don't have enough gold!")
                return
        elif pack == "3":
            if int(proflist[2]) >= packprices["Epic Pack"]:
                proflist[2] = int(proflist[2]) - packprices["Epic Pack"]
                packlist.append("epic")
                boughtpack = "Epic Pack"
            else:
                await ctx.send("You don't have enough gold!")
                return
        elif pack == "4":
            if int(proflist[2]) >= packprices["Legendary Pack"]:
                proflist[2] = int(proflist[2]) - packprices["Legendary Pack"]
                packlist.append("legendary")
                boughtpack = "Legendary Pack"
            else:
                await ctx.send("You don't have enough gold!")
                return
        else: #can change this later to let user try again automatically
            await ctx.send("Please try again with a valid pack!")
            return
        userprofwrite = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'w')
        for line in proflist[:3]: #change as prof changes - packs should be last
            userprofwrite.write(str(line) + "\n")
        userprofwrite.write(",".join(packlist))
        userprofwrite.close()
        await ctx.send(f"You bought a {boughtpack}! Thank you for your patronage!")
        return
    except FileNotFoundError:
        await ctx.send("We don't have your profile! Use ?pullcard to start!")

@bot.command()
async def collection(ctx):
    '''
    Displays your collection of cards
    '''
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
        for card in authorcardcount:
                strs[card.get_rarity()] += (f'{card.get_name()}     x{authorcardcount[card]}\n')
        for rarity in rarities:
            if strs[rarity.lower()] != '':
                embed.add_field(name=rarity, value=strs[rarity.lower()], inline=False)
        await ctx.send(embed=embed)
    except:
        await ctx.send("You have no cards! Pull one to start your collection!")

#implement pcollection here with arg for rarity/id
@bot.command()
async def pcollection(ctx,type=''):
    '''view your collection with pictures!'''
    rarities = ["legendary","epic","rare","common"]
    authorcardstodisplay = []
    idlist = []
    if type.lower() not in rarities and type.lower() != "id":
        await ctx.send("Please enter a valid type! (Common/Rare/Epic/Legendary/ID)")
    else:
        try:
            fileopen = open(f"usercards/{ctx.message.guild.id}{ctx.author.id}cards.csv",'r')
            for line in fileopen:
                cardname = retCard(TableofCards,line.strip())
                if type.lower() in rarities:
                    if cardname.get_rarity() == type.lower():
                        authorcardstodisplay.append(cardname)
                elif type.lower() == "id":
                    idlist.append(int(line.strip()))
                    idlist.sort() #change this later so it's not O(n) time. it might not matter anyway
            for id in idlist:
                authorcardstodisplay.append(retCard(TableofCards,str(id)))
            if len(authorcardstodisplay) == 0:
                await ctx.send("You have no cards of this type!")
            else:
                embed=discord.Embed(color=0xFF5733)
                avatar = ctx.author.display_avatar.url
                if type.lower() in rarities:
                    embed.set_author(name = f"{ctx.author.display_name}'s {type.lower()} Collection!",icon_url=avatar)
                elif type == "id":
                    embed.set_author(name = f"{ctx.author.display_name}'s Collection by ID",icon_url=avatar)
                strs = {'common':'','rare':'','epic':'','legendary':''}
                #REDO THIS TOO
                card = authorcardstodisplay[0]
                file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
                embed.set_image(url = f"attachment://{file.filename}")
                embed.set_footer(text = f"Page 1/{len(authorcardstodisplay)}")
                view = pcollectionbuttons(authorcardstodisplay,type.lower(),ctx.author)
                await ctx.send(file=file,embed=embed,view=view)
        except:
            await ctx.send("You have no cards! Pull one to start your collection!")

@bot.command()
async def cardlist(ctx,sort=''):
    '''
    Displays all available cards
    '''
    rarities = ["Legendary","Epic","Rare","Common"]
    embed=discord.Embed(title = "All Current Cards!", color=0xFF5733)
    strs = {'common':'','rare':'','epic':'','legendary':''}
    if sort.lower() == "id":
        strid = ''
        for card in TableofCards.get_cards():
                strid += (f'{card.get_id()}    {card.get_name()}  ({card.get_rarity()})\n')
        embed.add_field(name = 'Cards Sorted by ID', value = strid,inline=False)
        await ctx.send(embed=embed)
    elif sort.lower() == "rarity":
        page = 0
        for card in TableofCards.get_cards():
                strs[card.get_rarity()] += (f'{card.get_name()}\n')
        embed.add_field(name=rarities[page], value=strs[rarities[page].lower()], inline=False)
        view = NextMenuCardList()
        await ctx.reply(embed=embed,view=view)
    else:
        await ctx.send("Please enter a valid argument! (ID/Rarity)")

@bot.command()
async def pcardlist(ctx,sort=''):
    '''
    Displays all avaiable cards (now with pictures!)
    '''
    rarities = ["Legendary","Epic","Rare","Common"]
    strs = {'common':'','rare':'','epic':'','legendary':''}
    if sort.lower() == "id":
        cardnum = 0
        card = TableofCards.get_cards()[cardnum]
        embed=discord.Embed(title = f'{card.get_name()} ({card.get_rarity()})', description = f'ID: {card.get_id()}', color=0xFF5733)
        file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
        embed.set_image(url = f"attachment://{file.filename}")
        view = pcardlistbuttons()
        await ctx.send(file=file,embed=embed,view=view)
    else:
        await ctx.send("Please enter a valid argument! (ID)")

@bot.command()
async def profile(ctx):
    '''display your profile'''
    try:
        userprofopen = open(f"userprof/{ctx.message.guild.id}{ctx.author.id}profile.csv",'r')
        proflist = []
        for lin in userprofopen:
            proflist.append(lin.strip())
        if len(proflist) < 3:
            proflist.append(0)
        if len(proflist) < 4:
            proflist.append("You have no packs! Use ?buy to purchase one!")
        if proflist[3] == "":
            proflist[3] = "You have no packs! Use ?buy to purchase one!"
        embed=discord.Embed(color=0xFF5733)
        avatar = ctx.author.display_avatar.url
        embed.set_author(name = f"{ctx.author.display_name}'s Profile!",icon_url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name = "Cards",value = proflist[0],inline=False)
        embed.add_field(name = "Gold",value = proflist[2],inline=False)
        embed.add_field(name = "Packs",value = proflist[3],inline=False)
        userprofopen.close()
        await ctx.send(embed=embed)
    except FileNotFoundError:
        await ctx.send("We don't have your profile! Use ?pullcard to start!")

@bot.command()
async def packlist(ctx):
    '''displays all card packs!'''
    strembed = ""
    for key in cardpackNames:
        strembed += (key+"\n")
    embed=discord.Embed(title = "Available Card Packs",description = strembed,color=0xFF5733)
    await ctx.send(embed=embed)
        
@bot.command()
async def packdisplay(ctx,pack=''):
    '''display all cards in a card pack!'''
    if pack not in cardpackNames:
        await ctx.send("Try again with a valid pack name!")
    else:
        namestring = ""
        for card in cardpackNames[pack].get_cards():
            namestring += (card.get_name() + " (" + card.get_rarity() + ")\n")
        embed = discord.Embed(title = cardpackNames[pack].packname, description = namestring, color=0xFF5733)
        await ctx.send(embed=embed)


#implement by name later, have it so that it gives a menu when you do by name
@bot.command()
async def carddisplay(ctx,scmd=''):
    '''display a card!
    '''
    found = False
    for card in TableofCards.get_cards():
        if card.get_id() == scmd:
            found = True
            embed = discord.Embed(title = card.get_name(), color = 0xFF5733)
            file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
            embed.set_thumbnail(url=f"attachment://{file.filename}")
            embed.add_field(name = "Rarity",value=card.get_rarity(),inline=False)
            embed.add_field(name = "ID",value=card.get_id(),inline=False)
            embed.add_field(name = "Description",value=card.get_description(),inline=False)
            if card.get_packs() != []:
                embed.add_field(name = "Part of These Packs",value="\n".join(card.get_packs()),inline = False)
            await ctx.send(embed=embed,file=file)
    if found == False:
        await ctx.send("Please enter a valid ID!")


#button classes
class NextMenuCardList(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.page = 0
        self.rarities = ["Legendary","Epic","Rare","Common"]
        self.strs = {'common':'','rare':'','epic':'','legendary':''}
        for card in TableofCards.get_cards():
                self.strs[card.get_rarity()] += (f'{card.get_name()}\n')
    
    def makeEmbed(self):
        embed=discord.Embed(title = "All Current Cards!", color=0xFF5733)
        embed.add_field(name=self.rarities[self.page], value=self.strs[self.rarities[self.page].lower()], inline=False)
        return embed

    @discord.ui.button(label='Previous',style=discord.ButtonStyle.grey)
    async def previous(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.page <= 0:
            self.page = 3
        else:
            self.page -=1
        embed = self.makeEmbed()
        await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label='Next',style=discord.ButtonStyle.grey)
    async def next(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.page >= 3:
            self.page = 0
        else:
            self.page +=1
        embed = self.makeEmbed()
        await interaction.response.edit_message(embed=embed)

class pcardlistbuttons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.cardnum = 0
        self.maxcardid = 0
        for card in TableofCards.get_cards():
            self.maxcardid += 1
    
    def makeEmbed(self):
        card = TableofCards.get_cards()[self.cardnum]
        embed=discord.Embed(title = f'{card.get_name()} ({card.get_rarity()})', description = f'ID: {card.get_id()}', color=0xFF5733)
        file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
        embed.set_image(url = f"attachment://{file.filename}")
        return (file,embed)

    @discord.ui.button(label='Previous',style=discord.ButtonStyle.grey)
    async def previous(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.cardnum <= 0:
            self.cardnum = self.maxcardid-1
        else:
            self.cardnum -=1
        retembed = self.makeEmbed()
        embed = retembed[1]
        file = retembed[0]
        await interaction.response.edit_message(embed=embed,attachments=[file])
    
    @discord.ui.button(label='Next',style=discord.ButtonStyle.grey)
    async def next(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.cardnum >= self.maxcardid-1:
            self.cardnum = 0
        else:
            self.cardnum +=1
        retembed = self.makeEmbed()
        embed = retembed[1]
        file = retembed[0]
        await interaction.response.edit_message(embed=embed,attachments=[file])

class packcardbuttons(discord.ui.View):
    def __init__(self,pulledcards,author):
        super().__init__()
        self.value = None
        self.page = 0
        self.pulledcards = pulledcards
        self.author = author
    
    def makeEmbed(self):
        card = self.pulledcards[self.page]
        embed=discord.Embed(title=f"{self.author} pulled a {card.get_rarity()} {card.get_name()}!", description = f"{self.page+1}/5",color=0xFF5733)
        file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
        embed.set_image(url = f"attachment://{file.filename}")
        return (file,embed)

    @discord.ui.button(label='Previous',style=discord.ButtonStyle.grey)
    async def previous(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.page <= 0:
            self.page = 4
        else:
            self.page -=1
        retembed = self.makeEmbed()
        embed = retembed[1]
        file = retembed[0]
        await interaction.response.edit_message(embed=embed,attachments=[file])
    
    @discord.ui.button(label='Next',style=discord.ButtonStyle.grey)
    async def next(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.page >= 4:
            self.page = 0
        else:
            self.page +=1
        retembed = self.makeEmbed()
        embed = retembed[1]
        file = retembed[0]
        await interaction.response.edit_message(embed=embed,attachments=[file])

class pcollectionbuttons(discord.ui.View):
    def __init__(self,cards,type,author):
        super().__init__()
        self.value = None
        self.cards = cards
        self.cardnum = 0
        self.type = type
        self.author = author
    
    def makeEmbed(self):
        card = self.cards[self.cardnum]
        embed=discord.Embed(title = f'{card.get_name()} ({card.get_rarity()})', color=0xFF5733)
        if self.type == "id":
            embed.set_author(name = f"{self.author.display_name}'s Collection by ID",icon_url=self.author.display_avatar.url)
        else:
            embed.set_author(name = f"{self.author.display_name}'s {self.type} Collection!",icon_url=self.author.display_avatar.url)
        file = discord.File(f'season1/{card.get_image()}',filename = card.get_image())
        embed.set_image(url = f"attachment://{file.filename}")
        embed.set_footer(text = f"Page {self.cardnum + 1}/{len(self.cards)}")
        return (file,embed)

    @discord.ui.button(label='Previous',style=discord.ButtonStyle.grey)
    async def previous(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.cardnum <= 0:
            self.cardnum = len(self.cards)-1
        else:
            self.cardnum -=1
        retembed = self.makeEmbed()
        embed = retembed[1]
        file = retembed[0]
        await interaction.response.edit_message(embed=embed,attachments=[file])
    
    @discord.ui.button(label='Next',style=discord.ButtonStyle.grey)
    async def next(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.cardnum >= len(self.cards)-1:
            self.cardnum = 0
        else:
            self.cardnum +=1
        retembed = self.makeEmbed()
        embed = retembed[1]
        file = retembed[0]
        await interaction.response.edit_message(embed=embed,attachments=[file])
    
'''
@bot.command()
async def mycards(ctx):
    pass

@bot.command()
async def setdisplay(ctx):
    pass #thumbnail'''


#ping!
@bot.command()
async def ping(ctx):
    '''
    Makes sure bot is running
    '''
    await ctx.send('Pong!')


bot.run(TOKEN)


