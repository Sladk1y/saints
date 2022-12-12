# -*- coding: utf8 -*-
import disnake
from disnake.ext import commands, tasks
from disnake.ext.commands import CommandNotFound, MissingPermissions
from datetime import datetime as dt, timedelta
import datetime
import pymongo
import ast
from disnake import ButtonStyle
from disnake.ui import Button
import os
import random
import asyncio
import math as mt
from Cybernator import Paginator as pg
import dns.resolver
from pyqiwip2p import QiwiP2P
dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']
#########################################################################################################
# GLOBAL VARIABLES AND FUNCTIONS
#########################################################################################################
devs = [872809729326452746, 858251304560623626]
db = pymongo.MongoClient("mongodb+srv://root:232006232006@cluster0.napoh6y.mongodb.net/?retryWrites=true&w=majority").saints

token = 'MTA0OTI4MDUwOTc3NzMwMTUzNA.GxsRa8.MhJuyR48S9esofJ2HUHzN_isJ96XkeA_pZCHSQ'
p2ptoken = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6IjMwanl1bi0wMCIsInVzZXJfaWQiOiI3OTE1MjIxNTA4OCIsInNlY3JldCI6IjdlNDNlZGE4OTE4MDgwYjNkNzQ2ZmU0ODg1NTk1MzQ1ZjQ5OTEyMjBkZjkyMzU0ZmE5MmQ5NTc2MWQ3YTg5Y2IifX0='
users = db["users"]
settings = db["settings"]
shop = db["shop"]
promocodes = db["promocodes"]
business = db['business']
saints = db['saints']

embed_red = 0xdb0000
embed_yellow = 0xffff80
embed_green = 0x32CD32
embed_blue = 0x38dbfe
embed_info = 0x000000

guilds = {}

print("Connected")
dt1 = dt.utcnow()
for guild in settings.find():
    guilds[guild['_id']] = guild
print(dt.utcnow() - dt1)


##############################################
def task(number):
    number = str(number)[::-1]
    result = ''
    for i, num in enumerate(number):
        if i % 3 == 0:
            result += '.'
        result += num
    result = result[::-1][:-1]
    return result


def check_user(member, guild, extra: object = None):
    if type(member) == disnake.Member:
        member = member.id
    condition = {'uid': member, 'gid': guild.id}
    if extra:
        for i in extra.items():
            condition[i[0]] = i[1]
    user = users.find_one(condition)
    if not user:
        user = {
            'gid': guild.id,
            'uid': member,
            'balance': 0,
            'bank': 0,
            'cases': 0,
            'rod': 'Отсутствует',
            'leska': 'Отсутствует',
            'krychok': 'Отсутствует',
            'fish': 0,
            'vesfish': 0,
            'subs': 0,
            'times': {
                'work': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                'rob': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                'beer': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                'bonus': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                'fishing': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1)
            }
        }
        users.insert_one(user)
    return user


def check_guild(guild):
    if type(guild) == disnake.Guild:
        guild = guild.id
    try:
        g = guilds[guild]
    except KeyError:
        g = {
            '_id': guild,
            'moderators': [],
            'currency': 0,
            'chat-bot': False,
            'premium': 0,
            'premium_time': 0,
            'private_settings_channel': None,
            'private_voice_creator': None,
            'private_voice_creator_channel_category': None
        }
        settings.insert_one(g)
        guilds[guild] = g
    return g


def get_currency(guild):
    guild = check_guild(guild)
    return guild['currency'] if guild['currency'] != 0 else '<:sn:1038806575726473376>'


def retry_after(*args):
    txt = ''
    txt += f'{args[0]} часов ' if args[0] != 0 else ''
    txt += f'{args[1]} минут ' if args[1] != 0 else ''
    txt += f'{args[2]} секунд ' if args[2] != 0 else ''
    return txt


def can_be_int(x):
    try:
        return int(x)
    except:
        raise

#########################################################################################################
# BOT
#########################################################################################################
def a() -> None:
    intents = disnake.Intents.all()
    bot = commands.Bot(command_prefix='!', intents=intents)
    p2p = QiwiP2P(p2ptoken)
    bot.remove_command('help')

    #########################################################################################################
    # EVENTS AND TASKS
    #########################################################################################################

    @tasks.loop(hours=24)
    async def unpremium():
        for prem in settings.find():
            if prem["premium_time"] == -1 or prem["premium_time"] == 0:
                return
            if dt.utcnow() >= prem['premium_time']:
                print(1)
                settings.update_one({"_id": prem["_id"]}, {"$set": {"premium_time": 0, "premium": 0}})


    @tasks.loop(seconds=60)
    async def buis():
        all_businnes = business.find()
        for bis in all_businnes:

            if bis["time"] == 0:
                continue
            elif datetime.datetime.utcnow() >= bis["time"]:
                print(1)
                business.update_one({'gid': bis['gid'], "name": bis['name']}, {'$set': {'time': 0}})
                budget = bis["budget"]
                budget = mt.ceil(budget + ((budget / 100) * 8))
                business.update_one({'gid': bis['gid'], "name": bis['name']}, {'$set': {'budget': budget}})

    @bot.event
    async def on_ready():
        global tdict
        tdict = {}
        print("подключено")
        unpremium.start()
        buis.start()
        channel = bot.get_channel(687608307619463198)
        await channel.send(embed=disnake.Embed(title=f'Saints Economy запущен!', color=0x00ff00,
                                               description=f"\n**Ping:** `{round(bot.latency * 1000, 2)}мс`\n\n\
**Servers:** `{task(len(bot.guilds))}`"))

    @bot.event
    async def on_message(message):
        await bot.process_commands(message)
        member = message.author
        if not member.bot and message.guild:
            guild = check_guild(message.guild.id)
            if guild['chat-bot'] and random.randint(1, 100) <= 4:
                chat = [
                    f'Приветик {member.mention}', f'Как твои дела? {member.mention}',
                    'Может в казино сыграем? 😏',
                    'Вашей маме зять не нужен?',
                    'Скучные вы все какие-то 🙄',
                    f'У тебя красивые глаза {member.mention}',
                    'Люблю печеньки 😽',
                    'Давай дружить 🥺', 'Подскажите - где снять двушку? Ну, признайтесь кто тоже неправильно прочитал?',
                    'Когда у тебя сваливается камень с души, смотри, чтобы он не упал тебе на ногу.',
                    'Однажды папа застукал меня за развитием мелкой моторики...',
                    'Бабочки в животе питаются алкоголем.',
                    'СМИ — Средства Манипулирования Идиотами',
                    'Идеальная фигура! — подумал Буратино, поглаживая бревно.',
                    'Когда я не могу уснуть, я считаю до пяти. Иногда до полшестого.',
                    'У тебя аватарка прикольная',
                    'Зачётный никнейм 😂',
                    'Добавь меня на свой сервер 🥺, вместе поиграем...'
                ]
                chatt = random.choice(chat)
                await message.channel.send(chatt)

    @bot.command(aliases=['дуэль'])
    async def duel(ctx, memberduel: disnake.Member = None, amount: int = None):
        user = users.find_one({'uid': ctx.author.id, 'gid': ctx.guild.id})
        member = users.find_one({'uid': memberduel.id, 'gid': ctx.guild.id})
        pobeda = ["Вырубил соперника с одного удара", "Соперник потерял сознание от страха", "Нокаут на первом раунде",
                  "Нокаут на втором раунде", "Нокаут на третьем раунде", "Противник сдался",
                  "Соперник оказался довольно слабым", "Соперник забыл выключить утюг, и убежал домой",
                  "Победа по количеству баллов", "Соперник устал, и сдался", "Во время боя сопернику позвонила мама",
                  "Соперник намочил штаны", "Противник был взят на удушающий", "Авто поражение, соперник ударил в пах",
                  "Нокаут на четвертом раунде", "Нокаут на пятом раунде"]
        currency = get_currency(ctx.guild)
        if amount == "all":
            amount = user["balance"]

        amount = int(amount)

        if memberduel is None:
            return await ctx.send('Упомяните участника, которого приглашаете на дуэль!')
        if amount == None:
            return await ctx.send('Вы не указали ставку дуэли!')
        if memberduel == ctx.author:
            return await ctx.send("Нельзя начать дуэль с самим собой")
        if amount < 50:
            return await ctx.send(f'Минимальная ставка для дуэли 50 {currency}')
        if user['balance'] < amount:
            return await ctx.send('У вас недостаточно средств!')
        if member['balance'] < amount:
            return await ctx.send(f'У **{memberduel.mention}** недостаточно средств')
        else:
            users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                             {"$set": {"balance": user["balance"] - amount}})
            emb = disnake.Embed(title=f"{ctx.author.display_name} вызывает на дуэль {memberduel.display_name}",
                                description=f'`💰 Ставка:` **{amount}** {currency}\n\n`🥊 Соперник:` **{memberduel.mention}**\n\n`🥋 Нападающий:` **{ctx.author.mention}**')
            emb.set_footer(text=f'{memberduel.display_name} | нажми на кнопку чтобы принять дуэль!')
            emb.color = embed_green
            await ctx.send(
                embed=emb,
                components=[[
                    Button(label="Принять дуэль 🥊", style=ButtonStyle.green)]
                ]
            )
        try:
            res = await bot.wait_for("button_click", check=lambda i: i.author == memberduel, timeout=30)
        except asyncio.TimeoutError:
            user = users.find_one({'uid': ctx.author.id, 'gid': ctx.guild.id})
            users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                             {"$set": {"balance": user["balance"] + amount}})
            return await ctx.send(content="Игра окончена, слишком долгое ожидание!")
        if res.component.label == 'Принять дуэль 🥊':
            member = users.find_one({'uid': memberduel.id, 'gid': ctx.guild.id})
            if member['balance'] < amount:
                await ctx.send('У вас недостаточно средсв')
            else:
                users.update_one({"gid": ctx.guild.id, "uid": memberduel.id},
                                 {"$set": {"balance": member["balance"] - amount}})
                await ctx.send(embed=disnake.Embed(
                    description=f'`🥊` Началась дуэль между {ctx.author.mention} и {memberduel.mention}',
                    color=embed_blue))
                await asyncio.sleep(5)
                user = users.find_one({'uid': ctx.author.id, 'gid': ctx.guild.id})
                member = users.find_one({'uid': memberduel.id, 'gid': ctx.guild.id})
                chance = random.randint(0, 100)
                print(chance)
                if chance <= 50:
                    winer = ctx.author
                    users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                                     {"$set": {"balance": user["balance"] + (amount * 2)}})
                else:
                    winer = memberduel
                    users.update_one({"gid": ctx.guild.id, "uid": memberduel.id},
                                     {"$set": {"balance": member["balance"] + (amount * 2)}})
                emb = disnake.Embed(title=f'🥊 Дуэль окончена | результаты',
                                    description=f'`🏆 Победитель:` {winer.mention}\n\n`💰 Выигрыш:` {amount} {currency}\n\n`👔 Судья:` {random.choice(pobeda)}')
                emb.color = embed_yellow
                await ctx.send(embed=emb)

    @bot.command(aliases=['слоты', 'слот'])
    async def slots(ctx, stavka: int = None):
        if stavka is None:
            return await ctx.send("Укажите ставку!")
        if stavka <= 0:
            return await ctx.send("Ставка не может быть меньше или ровна 0")
        usr = users.find_one({"gid": ctx.guild.id, "uid": ctx.author.id})
        if stavka == "all":
            stavka = usr["balance"]
        stavka = int(stavka)
        if int(usr["balance"]) < stavka:
            return await ctx.send("Не достаточно средств")
        users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                         {"$set": {"balance": int(usr["balance"] - stavka)}})
        chance = random.randint(0, 100)

        l = [
            "🎁",
            "💎",
            "🍎",
            "🥝",
            "🍍",
            "🍌"
        ]
        if chance <= 28:
            emoji = random.randint(0, 5)
            emoji = l[emoji]
            slot = f"{emoji} {emoji} {emoji}"
            emb = disnake.Embed(title=f"{ctx.author.display_name}**, вы выиграли в слоты!**",
                                description=f"> {slot}\n\n> `🎟️ Выигрыш:` **{stavka * 2}**\n> `📈 Коэффициент:` **Х2**\n> `💸 Баланс:` **{usr['balance'] + int(stavka)}**")
            emb.set_footer(text="Saints Economy bot | слоты")
            emb.color = 0x00D140
            await ctx.send(embed=emb)
            usr = users.find_one({"gid": ctx.guild.id, "uid": ctx.author.id})
            users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                             {"$set": {"balance": int(usr["balance"] + int(stavka * 2))}})
        else:
            _1 = random.randint(0, 5)
            _2 = random.randint(0, 5)
            _3 = random.randint(0, 5)
            if _1 == _2 and _2 == _3:
                _1 = random.randint(0, 5)
                _2 = random.randint(0, 5)
                _3 = random.randint(0, 5)
            slot = f"{l[_1]} {l[_2]} {l[_3]}"
            emb = disnake.Embed(title=f"{ctx.author.display_name}**, вы проиграли слоты!**",
                                description=f"> {slot}\n\n> `🎟️ Ставка:` **{stavka}**\n> `💸 Баланс:` **{usr['balance'] - stavka}**")
            emb.set_footer(text="Saints Economy bot | слоты")
            emb.color = 0xFF1919
            await ctx.send(embed=emb)

    #########################################################################################################
    # ADMIN COMMANDS
    #########################################################################################################

    def insert_returns(body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
            if isinstance(body[-1], ast.If):
                insert_returns(body[-1].body)
                insert_returns(body[-1].orelse)
            if isinstance(body[-1], ast.With):
                insert_returns(body[-1].body)

    @bot.command()
    async def e(inter, *, cmd):
        if inter.author.id == 858251304560623626:
            try:
                fn_name = "_eval_expr"
                cmd = cmd.strip("` ")
                cmd = "\n".join(f" {i}" for i in cmd.splitlines())
                body = f"async def {fn_name}():\n{cmd}"
                parsed = ast.parse(body)
                body = parsed.body[0].body
                insert_returns(body)
                env = {
                        'bot': bot,
                        'disnake': disnake,
                        'commands': commands,
                        'inter': inter,
                        '__import__': __import__,
                        'settings': settings,
                        'users': users,
                        'promocodes': promocodes}
                exec(compile(parsed, filename="<ast>", mode="exec"), env)
                result = (await eval(f"{fn_name}()", env))
            except Exception as error:
                emb = disnake.Embed(title="\❌ Произошла ошибка", description=str(error), color=0xff0000)
                await inter.send(embed=emb)
        else:
            await inter.send("Отказано в доступе")

    @bot.command()
    async def setcurrency(ctx, currency):
        if ctx.author.guild_permissions.administrator:
            if currency:
                global guilds
                settings.update_one({'_id': ctx.guild.id}, {'$set': {'currency': currency}})
                guilds[ctx.guild.id]['currency'] = currency
                await ctx.send(
                    embed=disnake.Embed(description=f'Вы успешно изменили значок валюты на {currency}', color=0x00ff00))
            else:
                await ctx.send(embed=disnake.Embed(description='Команда введена неправильно\n`set-currency <эмодзи>`',
                                                   color=0xCC0000))
        else:
            await ctx.send(embed=disnake.Embed(description='Для использования команды, нужны права администратора',
                                               color=0xCC0000))

    @bot.command()
    async def removecurrency(ctx):
        if ctx.author.guild_permissions.administrator:
            global guilds
            guilds[ctx.guild.id]['currency'] = 0
            settings.update_one({'_id': ctx.guild.id}, {'$set': {'currency': 0}})
            await ctx.send(embed=disnake.Embed(description=f'Вы успешно сбросили значок валюты', color=0x00ff00))
        else:
            await ctx.send(embed=disnake.Embed(description='Для использования команды, нужны права администратора',
                                               color=0xCC0000))

    @bot.command(aliases=['добавитьроль'])
    async def addrole(ctx, role: disnake.Role, price):
        try:
            currency = get_currency(ctx.guild)
            price = can_be_int(price)
            if ctx.author.guild_permissions.administrator:
                if role  and price :
                    if not shop.find_one({'gid': ctx.guild.id, 'rid': role.id}):
                        shop.insert_one({'gid': ctx.guild.id, 'rid': role.id, 'price': price, 'date': dt.utcnow()})
                        await ctx.send(embed = disnake.Embed(description = f'Роль {role.mention} добавлена в магазин ролей, за {task(price)}{currency}', color = 0x00ff00))
                    else:
                        await ctx.send(embed = disnake.Embed(description = f'Такая роль уже есть в магазине ролей', color = 0xCC0000))
                else:
                    await ctx.send(embed = disnake.Embed(description = f'Команда введена неправильно\n`add_role <@Роль> <цена>`', color = 0xCC0000))
            else:
                await ctx.send(embed = disnake.Embed(description = 'Недостаточно прав!', color = 0xCC0000))
        except:
            pass

    @bot.command(aliases=['удалитьроль'])
    async def delrole(ctx, role: disnake.Role):
        if ctx.author.guild_permissions.administrator:
            if role:
                if shop.find_one({'gid': ctx.guild.id, 'rid': role.id}):
                    shop.delete_one({'rid': role.id})
                    await ctx.send(embed=disnake.Embed(description=f'Роль {role.mention} удалена из магазина ролей',
                                                       color=0x00ff00))
                else:
                    await ctx.send(embed=disnake.Embed(description=f'Такой роли нету в магазине ролей', color=0xCC0000))
            else:
                await ctx.send(
                    embed=disnake.Embed(description=f'Команда введена неправильно\n`delrole <@Роль>`', color=0xCC0000))
        else:
            await ctx.send(embed=disnake.Embed(description='Недостаточно прав!', color=0xCC0000))

    @bot.command(aliases=['выдать'])
    async def give(ctx, count, member: disnake.Member):
        count = can_be_int(count)
        if ctx.author.guild_permissions.administrator or ctx.author.id == 858251304560623626:
            if count and member and count > 0:
                count = round(count)
                user = check_user(member.id, ctx.guild)
                if user:
                    users.update_one({'gid': member.guild.id, 'uid': member.id},
                                        {'$set': {'balance': user['balance'] + count}})
                    await ctx.send('Успешно!')
            else:
                await ctx.send(embed=disnake.Embed(
                    description='Команда введена неправильно\n`give <сумма> <@Пользователь>`', color=0xCC0000))

    @bot.command(aliases=['забрать'])
    async def take(ctx, count, member):
        try:
            if ctx.author.guild_permissions.administrator:
                count = can_be_int(count)
                if count and member and count > 0:
                    count = round(count)
                    user = check_user(member.id, ctx.guild)
                    if user:
                        param = 'balance'
                        if user[param] - count >= 0:
                            users.update_one({'gid': member.guild.id, 'uid': member.id},
                                             {'$set': {param: user[param] - count}})
                            await ctx.send('Успешно')
                        else:
                            await ctx.send(
                                embed=disnake.Embed(description='У пользователя недостаточно средств', color=0xCC0000))
                else:
                    await ctx.send(
                        embed=disnake.Embed(description='Команда введена неправильно\n`take <сумма> <@Пользователь>`',
                                            color=0xCC0000))
        except:
            pass

    @bot.command(aliases=['забратьбанк'])
    async def takeb(ctx, count, member):
        try:
            if ctx.author.guild_permissions.administrator:
                count = can_be_int(count)
                if count and member and count > 0:
                    count = round(count)
                    user = check_user(member.id, ctx.guild)
                    if user:
                        param = 'bank'
                        if user[param] - count >= 0:
                            users.update_one({'gid': member.guild.id, 'uid': member.id},
                                             {'$set': {param: user[param] - count}})
                            await ctx.send('Успешно')
                        else:
                            await ctx.send(
                                embed=disnake.Embed(description='У пользователя недостаточно средств', color=0xCC0000))
                else:
                    await ctx.send(
                        embed=disnake.Embed(description='Команда введена неправильно\n`takeb <сумма> <@Пользователь>`',
                                            color=0xCC0000))
        except:
            pass

    @bot.command(aliases=['бтоп'])
    async def btop(ctx):
        title = '`👑`           ТОП ПО БАНКАМ          `👑`'
        param = 'bank'
        user_list = users.find({'gid': ctx.guild.id}).sort([(param, pymongo.DESCENDING)]).limit(10)
        description = ''
        x = 0
        currency = get_currency(ctx.guild)
        for user in user_list:
            i = user['uid']
            try:
                member = await ctx.guild.fetch_member(i)
                rew_list = ['🥇', '🥈', '🥉']
                x += 1
                if x <= 3:
                    description += f'\n`{rew_list[x - 1]}` **{member.display_name}** — **{task(user[param])}** {currency}\n'
                else:
                    description += f'\n**#{x} {member.display_name}** — **{task(user[param])}** {currency}\n'
            except:
                users.delete_one({'gid': ctx.guild.id, 'uid': user['uid']})
        await ctx.send(embed=disnake.Embed(description=description, color=0x2f3136, title=title))

    @bot.command(aliases=['топ'])
    async def top(ctx):
        title = '`👑`           ТАБЛИЦА ЛИДЕРОВ          `👑`'
        param = 'balance'
        user_list = users.find({'gid': ctx.guild.id}).sort([(param, pymongo.DESCENDING)]).limit(10)
        description = ''
        x = 0
        currency = get_currency(ctx.guild)
        for user in user_list:
            i = user['uid']
            try:
                member = await ctx.guild.fetch_member(i)
                rew_list = ['🥇', '🥈', '🥉']
                x += 1
                if x <= 3:
                    description += f'\n`{rew_list[x - 1]}` **{member.display_name}** — **{task(user[param])}** {currency}\n'
                else:
                    description += f'\n**#{x} {member.display_name}** — **{task(user[param])}** {currency}\n'
            except:
                users.delete_one({'gid': ctx.guild.id, 'uid': user['uid']})
        await ctx.send(embed=disnake.Embed(description=description, color=0x2f3136, title=title))

    @bot.command(aliases=['ютоп'])
    async def ytop(ctx):
        title = '`👥`           ТОП ЛИДЕРОВ SAINTSTUBE          `👥`'
        param = 'subs'
        user_list = users.find({'gid': ctx.guild.id}).sort([(param, pymongo.DESCENDING)]).limit(10)
        description = ''
        x = 0
        for user in user_list:
            i = user['uid']
            try:
                member = await ctx.guild.fetch_member(i)
                rew_list = ['🥇', '🥈', '🥉']
                x += 1
                if x <= 3:
                    description += f'\n`{rew_list[x - 1]}` **{member.display_name}** — **{task(user[param])}** 👥\n'
                else:
                    description += f'\n**#{x} {member.display_name}** — **{task(user[param])}** 👥\n'
            except:
                users.delete_one({'gid': ctx.guild.id, 'uid': user['uid']})
        await ctx.send(embed=disnake.Embed(description=description, color=0x2f3136, title=title))

    @bot.command(aliases=['ресет'])
    async def reset(ctx):
        if ctx.author.guild_permissions.administrator or ctx.author.id in [723328085662892042]:
            users.update_many({'gid': ctx.guild.id}, {'$set': {
                'balance': 0,
                'bank': 0,
                'cases': 0,
                'rod': 'Отсутствует',
                'leska': 'Отсутствует',
                'krychok': 'Отсутствует',
                'fish': 0,
                'vesfish': 0,
                'subs': 0,
                'times': {
                    'work': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                    'rob': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                    'beer': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                    'bonus': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1),
                    'fishing': dt.utcnow() - timedelta(seconds=60 ** 2 * 24 + 1)
                }
            }})
            await ctx.send(embed=disnake.Embed(
                description=f'<a:checkmark:998156852850331668> **Средства всех участников были успешно сброшены**',
                color=0x00ff00))
        else:
            await ctx.send(embed=disnake.Embed(description='Для использования команды, нужны права администратора',
                                               color=0xCC0000))

    @bot.command(aliases=['клир'])  # или же client.command
    async def clear(ctx, count):
        try:
            if ctx.author.guild_permissions.administrator:
                count = can_be_int(count)
                if count:
                    await ctx.channel.purge(limit=count)
                    await ctx.send(
                        embed=disnake.Embed(title="Очистка чата...", description=f"Удалено **{count}** сообщений",
                                            color=disnake.Color.green()))
                else:
                    await ctx.send(embed=disnake.Embed(title="Ошибка", description=f"Укажите количество сообщений",
                                                       color=disnake.Color.red()))
            else:
                await ctx.send(embed=disnake.Embed(title="Ошибка", description=f"Вы не являетесь администратором",
                                                   color=disnake.Color.red()))
        except:
            pass

    # #########################################################################################################
    # # FUN COMMANDS
    # #########################################################################################################

    @bot.command(aliases=['обнять'])
    async def hug(ctx, member:disnake.Member):
        gifs = [
            "https://c.tenor.com/FYKsVaNI7lkAAAAC/anime-hug.gif",
            "https://i.pinimg.com/originals/c4/25/db/c425db273797024dc1776f77c83bd5f3.gif",
            "https://c.tenor.com/VhhYP5Jq4wQAAAAC/anime-hug.gif",
            "https://i.pinimg.com/originals/51/2a/f3/512af31e377153959dbad5b888d22af1.gif",
            "https://c.tenor.com/1T1B8HcWalQAAAAC/anime-hug.gif",
            "https://i.gifer.com/27tM.gif",
            "https://acegif.com/wp-content/gif/anime-hug-38.gif",
            "https://animesher.com/orig/1/133/1330/13306/animesher.com_love---hug-gif-1330647.gif",
            "https://c.tenor.com/WBeVZm5cPN8AAAAC/hug-anime.gif",
            "https://i.gifer.com/Y4Pm.gif",
            "https://media3.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif",
            "https://thumbs.gfycat.com/AbandonedShamefulConch-size_restricted.gif",
            "https://i.pinimg.com/originals/b7/ad/8d/b7ad8dc636e844613da9a506805e4eea.gif",
            "https://c.tenor.com/ggKei4ayfIAAAAAC/anime-hug.gif",
            "https://acegif.com/wp-content/gif/anime-hug-59.gif"
        ]
        if member == ctx.author:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description='Нельзя обнять самого себя.',
                                                      color=0xCC0000))
        if member == None:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description='Упомяни пользователя которого хочешь обнять.',
                                                      color=0xCC0000))
        img = random.choice(gifs)
        embed = disnake.Embed(
            title=f"{ctx.author.display_name} обнял(-а) {member.display_name}",
            color=0x00ff00
        ).set_image(url=img)
        await ctx.send(embed=embed)

    @bot.command(aliases=['плакать'])
    async def cry(ctx):
        gifs = [
            "https://media1.giphy.com/media/ROF8OQvDmxytW/200.gif",
            "https://c.tenor.com/bMSZQ4j3CQkAAAAC/anime-cry.gif",
            "https://c.tenor.com/q0nNfTktQ7wAAAAM/crying-anime.gif",
            "https://thumbs.gfycat.com/HalfAssuredBorderterrier-max-1mb.gif",
            "https://c.tenor.com/_M-1VNi4S9QAAAAM/anime-cry.gif",
            "https://i.pinimg.com/originals/e0/fb/b2/e0fbb27f7f829805155140f94fe86a2e.gif",
            "https://www.icegif.com/wp-content/uploads/sad-anime-icegif.gif",
            "https://c.tenor.com/OfYt0T0tgCYAAAAC/anime-cry.gif",
            "https://i.gifer.com/V2Kw.gif",
            "https://animesher.com/orig/1/152/1527/15275/animesher.com_sad-girl-anime-cry-cry-1527576.gif",
            "https://c.tenor.com/gDk49oAcW9QAAAAd/anime-cry-cry.gif",
            "https://i.pinimg.com/originals/c7/7a/2e/c77a2e50b3f934aa15df3659ef46249d.gif",
            "http://static.tumblr.com/fmikcqz/7Allyi1ls/anime_cry_sad_rain.gif",
            "https://animesher.com/orig/0/94/949/9490/animesher.com_anime-girl-anime-gif-crying-gif-949058.gif",
            "https://media1.giphy.com/media/RBdwNQim7Y6HK/200w.gif?cid=82a1493br6k62mju3oaoq1tokxxa1m7jvauzmly3taf7h6sl&rid=200w.gif&ct=g",
            "https://media0.giphy.com/media/3fmRTfVIKMRiM/200w.gif?cid=82a1493br6k62mju3oaoq1tokxxa1m7jvauzmly3taf7h6sl&rid=200w.gif&ct=g"
        ]
        img = random.choice(gifs)
        embed = disnake.Embed(
            title=f"{ctx.author.display_name} грустит",
            color=0x00ff00
        ).set_image(url=img)
        await ctx.send(embed=embed)

    @bot.command(aliases=['поцеловать'])
    async def kiss(ctx, member:disnake.Member):
        gifs = [
            "https://c.tenor.com/SqpFZQfcyEgAAAAM/anime-kiss.gif",
            "https://i.gifer.com/8Sbz.gif",
            "https://c.tenor.com/sDOs4aMXC6gAAAAM/anime-sexy-kiss-anime-girl.gif",
            "https://www.icegif.com/wp-content/uploads/2021/10/icegif-1005.gif",
            "https://c.tenor.com/dJU8aKmPKAgAAAAd/anime-kiss.gif",
            "https://i.pinimg.com/originals/54/31/62/5431628f9c32f0e804689c2c68db8a2a.gif",
            "https://i.gifer.com/XrqL.gif",
            "https://i.pinimg.com/originals/5e/1e/8c/5e1e8c81c01a1e26db4c0e18ae8bafd5.gif",
            "https://www.gifcen.com/wp-content/uploads/2022/03/anime-kiss-gif-7.gif",
            "https://thumbs.gfycat.com/BlaringHonoredGiraffe-size_restricted.gif",
            "https://i.pinimg.com/originals/b5/cd/30/b5cd303b89e63571baacd361f543ae20.gif",
            "https://lifeo.ru/wp-content/uploads/gif-anime-kisses-28.gif",
            "https://www.icegif.com/wp-content/uploads/anime-kiss-icegif.gif",
            "https://media3.giphy.com/media/B7xXI1ZZCrTag/giphy.gif",
            "https://acegif.com/wp-content/uploads/anime-kissin-15.gif",
            "http://25.media.tumblr.com/ea431c278ccd1ae3d1041709a4943b64/tumblr_mpqhwgauaS1swflh7o1_500.gif"
        ]
        if member == ctx.author:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description=f'Нельзя поцеловать самого себя.',
                                                      color=0xCC0000))
        if member == None:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description='Упомяни пользователя которого хочешь поцеловать.',
                                                      color=0xCC0000))
        img = random.choice(gifs)
        embed = disnake.Embed(
            title=f"{ctx.author.display_name} поцеловал(-а) {member.display_name}",
            color=0x00ff00
        ).set_image(url=img)
        await ctx.send(embed=embed)

    @bot.command(aliases=['погладить'])
    async def pat(ctx, member:disnake.Member):
        gifs = [
            "https://c.tenor.com/E6fMkQRZBdIAAAAM/kanna-kamui-pat.gif",
            "https://i.gifer.com/KJ42.gif",
            "https://c.tenor.com/8DaE6qzF0DwAAAAC/neet-anime.gif",
            "https://media4.giphy.com/media/4HP0ddZnNVvKU/200.gif",
            "https://c.tenor.com/TDqVQaQWcFMAAAAC/anime-pat.gif",
            "https://thumbs.gfycat.com/ImpurePleasantArthropods-size_restricted.gif",
            "https://i.pinimg.com/originals/94/91/16/949116f16d90fd2cff3fbccf477cd091.gif",
            "https://i.pinimg.com/originals/d7/c3/26/d7c326bd43776f1e0df6f63956230eb4.gif",
            "https://c.tenor.com/-hkJYNs7tUkAAAAC/anime-pat.gif",
            "https://thumbs.gfycat.com/HilariousFirsthandHippopotamus-max-1mb.gif",
            "https://i.pinimg.com/originals/c2/34/cd/c234cdcb3af7bed21ccbba2293470b8c.gif",
            "https://c.tenor.com/N41zKEDABuUAAAAM/anime-head-pat-anime-pat.gif",
            "https://pa1.narvii.com/6847/b1fe3eb0240f8f1b0ca0f8b6d1fe3752c5988d1e_hq.gif",
            "https://i.pinimg.com/originals/2e/27/d5/2e27d5d124bc2a62ddeb5dc9e7a73dd8.gif",
            "https://animegif.ru/up/photos/album/oct17/171021_4438.gif",
            "https://animesher.com/orig/1/136/1363/13633/animesher.com_gif-suki-pat-1363315.gif"
        ]
        if member == ctx.author:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description=f'Нельзя погладить самого себя.',
                                                      color=0xCC0000))
        if member == None:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description='Упомяни пользователя которого хочешь погладить.',
                                                      color=0xCC0000))
        img = random.choice(gifs)
        embed = disnake.Embed(
            title=f"{ctx.author.display_name} погладил(-а) {member.display_name}",
            color=0x00ff00
        ).set_image(url=img)
        await ctx.send(embed=embed)

    @bot.command(aliases=['ударить'])
    async def punch(ctx, member:disnake.Member):
        gifs = [
            "https://c.tenor.com/6a42QlkVsCEAAAAd/anime-punch.gif",
            "https://c.tenor.com/GuML2yHT58kAAAAd/punch-anime.gif",
            "https://c.tenor.com/VrWzG0RWmRQAAAAC/anime-punch.gif",
            "https://c.tenor.com/44IcPjhMv5oAAAAd/punch-anime.gif",
            "https://i.pinimg.com/originals/e1/63/ff/e163ff743644a8250d4f07112b8ddb08.gif",
            "https://media3.giphy.com/media/yo3TC0yeHd53G/200.gif",
            "https://c.tenor.com/xJyw7SRtDRoAAAAC/anime-punch.gif",
            "https://i.pinimg.com/originals/f3/ec/8c/f3ec8c256cb22279c14bfdc48c92e5ab.gif",
            "https://c.tenor.com/JV3DgJ-a8-MAAAAd/punch-anime.gif",
            "https://i.pinimg.com/originals/37/86/8f/37868f349c1f953ac5b642c70c46f615.gif",
            "https://c.tenor.com/o0FEX0ZcSAEAAAAd/hibiki-punch-anime-punch.gif",
            "https://i.gifer.com/9eUJ.gif",
            "https://i.pinimg.com/originals/60/7a/35/607a354344d527ff5868ad46ace65888.gif",
            "https://giffiles.alphacoders.com/131/13126.gif",
            "https://media4.giphy.com/media/arbHBoiUWUgmc/200.gif",
            "https://i.pinimg.com/originals/8d/50/60/8d50607e59db86b5afcc21304194ba57.gif"
        ]
        if member == ctx.author:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description=f'Нельзя ударить самого себя.',
                                                      color=0xCC0000))
        if member == None:
            return await ctx.send(embed=disnake.Embed(title='Ошибка',
                                                      description='Упомяни пользователя которого хочешь ударить.',
                                                      color=0xCC0000))
        img = random.choice(gifs)
        embed = disnake.Embed(
            title=f"{ctx.author.display_name} ударил(-а) {member.display_name}",
            color=0x00ff00
        ).set_image(url=img)
        await ctx.send(embed=embed)

    @bot.command(aliases=['шар'])
    async def ball(ctx, *, arg):
        if arg:
            g = random.choice(
                ['Да!', 'Нет!', 'Возможно!', 'Несовсем!', 'Конечно!', 'Незнаю!', 'Подумай сам...', 'Спроси позже',
                 'Глупый вопрос', 'Возможно частично', 'Скорее всего нет,чем да!'])
            await ctx.send(
                embed=disnake.Embed(title='Всезнающий шар`🔮`', description=f'`❓Вопрос:` **{arg}** \n`❗Ответ:` **{g}**',
                                    color=0xEBF727))
        else:
            await ctx.send('Ну а кто же знает, если не ты?')

    @bot.command(aliases=['создать_промо'])
    async def promo_create(ctx, название, использований: int, сумма: int):
        global guilds
        print(guilds[ctx.guild.id])
        if guilds[ctx.guild.id]["premium"] in [1, 2]:
            if название:
                arg2 = название.lower()
                if ctx.author.guild_permissions.administrator:
                    if not promocodes.find_one({'gid': ctx.guild.id, 'promo': arg2}):
                        if использований and сумма:
                            if использований < 1:
                                использований = 1
                            if сумма < 1:
                                сумма = 1
                            promocodes.insert_one({'gid': ctx.guild.id, 'promo': arg2, 'uses': использований, 'prize': сумма, 'users' : []})
                            await ctx.send(embed = disnake.Embed(title = 'Промокод Создан', description = f'`🏷️`Промокод: **{arg2}**\n`💸`Сумма: **{сумма}**\n`♻️`Использований: **{использований}**', color = 0x00ff00))
                        else:
                            await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Аргументы введены неправильно'))
                    else:
                        await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Такой промокод уже существует'))				
                else:
                    await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Недостаточно прав'))
            else:
                await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Вы не указали промокод'))
        else:
            await ctx.send("На данном сервере недоступен premium!\nДля активации укажите команду - /premium")

    @bot.command(aliases=['удалить_промо'])
    async def promo_delete(ctx, название):
        if ctx.author.guild_permissions.administrator:
            print(guilds[ctx.guild.id])
            if guilds[ctx.guild.id]["premium"] in [1, 2]:
                if название :
                    arg2 = название.lower()
                    if ctx.author.guild_permissions.administrator:
                        promocodes.delete_one({'gid': ctx.guild.id, 'promo': arg2})
                        await ctx.send(embed = disnake.Embed(title = f'Промокод **{arg2}** успешно удален', color = 0x00ff00))
                    else:
                        await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Недостаточно прав'))
                else:
                    await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Вы не указали промок, который хотите удалить'))
            else:
                await ctx.send("На данном сервере недоступен premium!\nДля активации укажите команду - /premium")
        else:
            await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Недостаточно прав'))

    @bot.command(aliases=['список_промокодов'])
    async def promo_list(ctx):
        if ctx.author.guild_permissions.administrator:
            promo_list = promocodes.find({'gid': ctx.guild.id}).limit(10)
            currency = get_currency(ctx.guild)
            if promo_list:
                embed = disnake.Embed(color = 0x00ff00, title = f'Промокоды')
                for promo in promo_list:
                    embed.add_field(name = 'Промокод ' + f"**{promo['promo']}**", value = f'Использований **{len(promo["users"])}/{promo["uses"]}**\nПриз **{promo["prize"]}{currency}**', inline = False)
                await ctx.send(embed = embed)
        else:
            await ctx.send(embed = disnake.Embed(title = 'Ошибка', color = 0xCC0000, description = 'Недостаточно прав'))

    @bot.command(aliases=['использовать', 'промо'])
    async def promo(ctx, название):
        arg2 = название.lower()
        currency = get_currency(ctx.guild)
        promo = promocodes.find_one({'gid': ctx.guild.id, 'promo': arg2})
        if promo:
            if promo["uses"] == len(promo["users"]) + 1: return await ctx.send('Промокод закончился')
            user_list = promo['users']
            if ctx.author.id not in user_list:
                promocodes.update_one({'gid': ctx.guild.id, 'promo': arg2},{'$push': {'users': ctx.author.id}})
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': check_user(ctx.author.id, ctx.guild)['balance'] + promo['prize']}})
                await ctx.send(embed=disnake.Embed(title=f'Промокод на **{promo["prize"]}**{currency} успешно активирован',color=0x00ff00))
                if promo['uses'] == len(promo['users']):
                    promocodes.delete_one({'gid': ctx.guild.id, 'promo': arg2})
            else:
                await ctx.send(embed=disnake.Embed(title='Ошибка', color=disnake.Colour.red(), description='Вы уже активировали этот промокод'))

        else:
            await ctx.send(embed=disnake.Embed(title='Ошибка', color=disnake.Colour.red(), description='Промокод не найден или уже недоступен'))

    # #########################################################################################################
    # # USER COMMANDS
    # #########################################################################################################

    @bot.command(aliases=['стрим'])
    @commands.cooldown(1, 200 * 9 * 1, commands.BucketType.member)
    async def streaming(ctx):
        usr = users.find_one({'gid': ctx.guild.id, 'uid': ctx.author.id})
        donat = random.randint(500, 2000)
        subscribers = random.randint(1, 30)
        streamchance = random.randint(0, 100)
        if streamchance <= 88:
            users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'subs': usr['subs'] + subscribers}})
            users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': usr['balance'] + donat}})
            await ctx.send(embed=disnake.Embed(title=f'{ctx.author.display_name}, вы запустили стрим!',
                                               description=f'Вы успешно провели трансляцию на **SaintsTube** `🖥️`\n\n`📊 Статистика:`\n`👥 Новых подписчиков:` **{subscribers}**\n`💵 Собрано с донатов:` **{task(donat)}**',
                                               color=0xFFFF00))
        else:
            neudd = [
                'У вас возникли проблемы с интернетом, и стрим прекратился.',
                'Ваш стрим не понравился зрителям.',
                'Во время стрима, у вас повредилась аппаратура.',
                'Ваш аккаунт заморозили на 30 минут, за нарушения правил SaintsTube.',
                'На вашем стриме был контент 18+, вас заморозили на 30 минут.',
            ]
            neud = random.choice(neudd)
            await ctx.send(embed=disnake.Embed(title=f'{ctx.author.display_name}, вы запустили стрим!',
                                               description=f'**Неудача... {neud}**', color=0xFF0000))

    @streaming.error
    async def streaming_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
            await ctx.send(embed=disnake.Embed(color=0xFF0000, title="Ошибка!",
                                               description=f'**Следующую трансляцию можно запустить через: {retry_after}**'))

    @bot.command(aliases=['профиль', 'п','p'])
    async def profile(ctx, member: disnake.Member = None):
        if member is None:
            member = ctx.author
        usr = check_user(member.id, ctx.guild)
        currency = get_currency(ctx.guild)
        all_businnes = business.find({"gid": ctx.guild.id})

        if all_businnes is None:
            c = "Отсутствует"
        for bis in all_businnes:

            coworker = bis["participant"]
            coworker = coworker.split()
            for mem in coworker:
                if member.id == int(mem):
                    c = bis["name"]
                    return await ctx.send(embed=disnake.Embed(title=f'Профиль пользователя | {member}',
                                                              description=f"**Денежные средства:**\n\n    `💵 Наличные`: **{task(usr['balance'])} {currency}**\n\n    `🏦 Банк`: **{task(usr['bank'])} {currency}**\n\n    `📦 Кейсов`: **{task(usr['cases'])}** шт.\n\n**Бизнес пользователя**\n\n    `🏗️ Название:` **{c}**\n\n**Рюкзак:**\n\n    `🐟 Количество рыбы`: {usr['fish']}\n\n    `⚖️ Общий вес`: {usr['vesfish']}\n\n    `🎣 Удочка`: {usr['rod']}\n\n    `🪢 Леска`: {usr['leska']}\n\n    `🪝 Крючок`: {usr['krychok']}\n\n**SaintsTube:**\n\n    `👨‍💻 Создатель канала`: {member.mention}\n\n    `👥 Подписчики`: {task(usr['subs'])}",
                                                              color=0x00FFC3).set_thumbnail(
                        url=member.display_avatar).set_footer(text='Пополнить баланс: donate\nПродать рыбу: sell fish'))
        c = "Отсутствует"
        await ctx.send(embed=disnake.Embed(title=f'Профиль пользователя | {member}',
                                           description=f"**Денежные средства:**\n\n    `💵 Наличные`: **{task(usr['balance'])} {currency}**\n\n    `🏦 Банк`: **{task(usr['bank'])} {currency}**\n\n    `📦 Кейсов`: **{task(usr['cases'])}** шт.\n\n**Бизнес пользователя**\n\n    `🏗️ Название:` **{c}**\n\n**Рюкзак:**\n\n    `🐟 Количество рыбы`: {usr['fish']}\n\n    `⚖️ Общий вес`: {usr['vesfish']}\n\n    `🎣 Удочка`: {usr['rod']}\n\n    `🪢 Леска`: {usr['leska']}\n\n    `🪝 Крючок`: {usr['krychok']}\n\n**SaintsTube:**\n\n    `👨‍💻 Создатель канала`: {member.mention}\n\n    `👥 Подписчики`: {task(usr['subs'])}",
                                           color=0x00FFC3).set_thumbnail(url=member.display_avatar).set_footer(
            text='Пополнить баланс: donate\nПродать рыбу: sell fish'))

    @bot.command(aliases=['рыбалка'])
    @commands.cooldown(1, 300 * 2 * 1, commands.BucketType.member)
    async def fishing(ctx):
        usr = users.find_one({'gid': ctx.guild.id, 'uid': ctx.author.id})
        user = check_user(ctx.author.id, ctx.guild)
        if usr['rod'] == 'Отсутствует':
            embed = disnake.Embed(color=0xFF0000, title='Ошибка!',
                                  description=f"В вашем рюкзаке не хватает удочки чтобы пойти на рыбалку")
            embed.set_footer(text='profile - открыть профиль')
            await ctx.send(embed=embed)
            return
        elif usr['leska'] == 'Отсутствует':
            embed = disnake.Embed(color=0xFF0000, title='Ошибка!',
                                  description=f"В вашем рюкзаке не хватает лески чтобы пойти на рыбалку")
            embed.set_footer(text='profile - открыть профиль')
            await ctx.send(embed=embed)
            return
        elif usr['krychok'] == 'Отсутствует':
            embed = disnake.Embed(color=0xFF0000, title='Ошибка!',
                                  description=f"В вашем рюкзаке не хватает крючка чтобы пойти на рыбалку")
            embed.set_footer(text='profile - открыть профиль')
            await ctx.send(embed=embed)
            return
        else:
            polomka = random.randint(0, 100)
            if polomka <= 90:
                chance = random.randint(0, 100)
                if chance <= 70:
                    fishmax = random.randint(5, 30)
                    vesmax = random.randint(2, 20)
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                                     {'$set': {'fish': usr['fish'] + fishmax}})
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                                     {'$set': {'vesfish': usr['vesfish'] + vesmax}})
                    embed = disnake.Embed(color=0x03FFEF,
                                          title=f'{ctx.author.display_name} вы успешно сходили на рыбалку!',
                                          description=f'\n`🐟`Всего поймано: {fishmax}\n`⚖️`Общий вес: {vesmax}\n`🪣`Всего в ведре: {usr["fish"] + fishmax}')
                    embed.set_thumbnail(url='https://i.gifer.com/Rmeh.gif')
                    embed.set_footer(text='sell fish - продать рыбу')
                else:
                    otv = [
                        'Увы, не одной рыбы не поймано!',
                        'Вы встали не с той ноги и не поймали ничего!',
                        'На озере был сильный ветер, рыбалка не удалась!',
                        'На море был сильный ветер, рыбалка не удалась!',
                        'На речке был сильный ветер, рыбалка не удалась!',
                        'Пошёл дождь и вы промокли, всё коту под хвост!',
                        'Вы заснули и ваш улов украли!',
                        'Во время рыбалки, ваши черви разбежались!'
                    ]
                    otvet = random.choice(otv)
                    embed = disnake.Embed(color=0xFF0000, title=f'{ctx.author.display_name} сходил на рыбалку!',
                                          description=f'{otvet}')
            else:
                lom = ['удочка', 'крючок', 'леска', 'леска']
                lomaw = random.choice(lom)
                if lomaw == 'удочка':
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'rod': 'Отсутствует'}})
                    await ctx.send(embed=disnake.Embed(color=disnake.Color.red(),
                                                       title='Упс...! Во время рыбалки у вас сломалась удочка!'))
                    return
                elif lomaw == 'крючок':
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'krychok': 'Отсутствует'}})
                    await ctx.send(embed=disnake.Embed(color=disnake.Color.red(),
                                                       title='Упс...! Во время рыбалки у вас сломалася крючок!'))
                    return
                elif lomaw == 'леска':
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'leska': 'Отсутствует'}})
                    await ctx.send(embed=disnake.Embed(color=disnake.Color.red(),
                                                       title='Упс...! Во время рыбалки у вас порвалась леска!'))
                    return
        await ctx.send(embed=embed)

    @fishing.error
    async def fishing_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
            await ctx.send(embed=disnake.Embed(color=0xFF0000, title="Ошибка!",
                                               description=f'**Пойти на рыбалку можно через: {retry_after}**'))

    @bot.command(aliases=['продать'])
    async def sell(ctx):
        usr = users.find_one({'gid': ctx.guild.id, 'uid': ctx.author.id})
        if usr['fish'] == 0:
            await ctx.send(embed=disnake.Embed(title="Ошибка", description=f"В вашем рюкзаке нет рыбы", color=0xCC0000))
        else:
            currency = get_currency(ctx.guild)
            hz = users.find_one({'gid': ctx.guild.id, 'uid': ctx.author.id})
            hz = hz.get('vesfish')
            users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'fish': 0}})
            users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'vesfish': 0}})
            users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                             {'$set': {'balance': usr['balance'] + hz * 1500}})
            embed = disnake.Embed(title=f"Продажа рыбы | {ctx.author.display_name} ",
                                  description=f"`🛒`Продано: {usr['vesfish']} кг. рыбы!\n`⚖️`Цена за кг: 1.500{currency}\n`💰`Заработок: {task(hz * 1500)}{currency}",
                                  color=0xFFFF00)
            embed.set_thumbnail(url='https://cdn.dribbble.com/users/22930/screenshots/3448062/totes.gif')
            await ctx.send(embed=embed)

    @bot.command(aliases=['monetka', 'coin', 'монетка'])
    async def money(ctx, mes, stavka: int):
        currency = get_currency(ctx.guild)
        usr = users.find_one({"gid": ctx.guild.id, "uid": ctx.author.id})
        if stavka == "all":
            stavka = usr['balance']
        stavka = int(stavka)
        if stavka is None:
            emb = disnake.Embed(title="Ошибка", description=f"Вы не указали ставку", color=disnake.Color.red())
        elif stavka < 10:
            emb = disnake.Embed(title="Ошибка", description=f"Минимальная сумма ставки 10 {currency}",
                                color=disnake.Color.red())
        elif usr['balance'] < stavka:
            emb = disnake.Embed(title="Ошибка", description=f"Недостаточно средств на балансе",
                                color=disnake.Color.red())
        else:
            if mes in ('орёл', 'орел', 'eagle'):
                users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                                 {"$set": {"balance": usr["balance"] - stavka}})
                chance = random.randint(0, 100)
                if chance <= 33:
                    kof = 1
                    emb = disnake.Embed(title=f"{ctx.author.display_name}**, Вы выиграли, выпал орёл!**",
                                        description=f"> 🦅\n> `💰 Выигрыш:` **{stavka * kof}** {currency}\n> `📈 Коэффициент:`**X2**\n> `💸 Баланс:` **{usr['balance'] + stavka}** {currency}")
                    emb.set_footer(text="Saints Economy bot | монетка")
                    emb.color = 0x00D140
                    new_balance = usr['balance'] + (stavka * kof)
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': new_balance}})
                else:
                    emb = disnake.Embed(title=f"{ctx.author.display_name}**, Вы проиграли, выпала решка!**",
                                        description=f"> 🪙\n> `🎟️ Ставка:` **{stavka}** {currency}\n> `💸 Баланс:` **{usr['balance'] - stavka}** {currency}")
                    emb.color = 0xFF1919

            elif mes in ('решка', 'reska'):
                users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                                 {"$set": {"balance": usr["balance"] - stavka}})
                chance = random.randint(0, 100)
                if chance <= 33:
                    kof = 1
                    emb = disnake.Embed(
                        title=f"{ctx.author.display_name}**, Вы выиграли, выпала решка!**",
                        description=f"> 🪙\n> `💰 Выигрыш:` **{stavka * kof}** \n> `📈 Коэффициент:` **X2**\n> `💸 Баланс:` **{usr['balance'] + stavka}** {currency}")
                    emb.set_footer(text="Saints Economy bot | монетка")
                    emb.color = 0x00D140
                    new_balance = usr['balance'] + (stavka * kof)
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': new_balance}})
                else:
                    emb = disnake.Embed(title=f"{ctx.author.display_name}**, Вы проиграли, выпал орёл!**",
                                        description=f"> 🦅\n> `🎟️ Ставка:` **{stavka}** {currency}\n> `💸 Баланс:` **{usr['balance'] - stavka}** {currency}")
                    emb.color = 0xFF1919
        await ctx.send(embed=emb)

    @bot.command(aliases=['бот', 'инфо'])
    async def info(ctx):
        member_count = 0
        for guild in bot.guilds:
            member_count+=guild.member_count
            embed = disnake.Embed(title = '**Bot Information**', color = 0x2f3136, description = f"\n**Ping:** `{round(bot.latency * 1000, 2)}ms`\n\n**Servers:** `{task(len(bot.guilds))}`\n\n**Users:** `{task(member_count)}`")
            embed.set_footer(text = 'Developers: тот самый SLADK1Y#1599, Neptun#0003, 50cent#4113',icon_url = 'https://emoji.gg/assets/emoji/5579-developerbadge.png?t=1616827671')
        await ctx.send(embed = embed)

    @bot.command(aliases=['положить'])
    async def dep(ctx, amount):
        if amount:
            currency = get_currency(ctx.guild)
            user = check_user(ctx.author.id, ctx.guild)
            if amount == "all":
                amount = user["balance"]
            amount = int(amount)
            if amount >= 100:
                new_bank = round(user['bank'] + amount * 0.97)
                new_balance = user['balance'] - amount
                if new_balance >= 0:
                    author = ctx.author
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                                     {'$set': {'balance': new_balance, 'bank': new_bank}})
                    embed = disnake.Embed(title='Перевод средств в банк📤', color=0xEBF727,
                                          description=f"**{author.mention} вы успешно перевели деньги на баланс банка**\n——————————\n`🏦`Баланс банка: **{task(new_bank)} {currency}**\n`💵`Наличные: **{task(new_balance)} {currency}**\n**Комиссия: 3%**").set_footer(
                        text=f'{author.name}#{author.discriminator}', icon_url=author.display_avatar).set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/927784752222699601/1009971836978737172/image0.gif')
                    embed.timestamp = dt.utcnow()
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(embed=disnake.Embed(title='Недостаточно средств', color=0xCC0000))
            else:
                await ctx.send(embed=disnake.Embed(title='Минимальная сумма депозита 100 <a:money:998158048952586280>',
                                                   color=0xCC0000))
        else:
            await ctx.send(embed=disnake.Embed(title='Команда введена неправильно\n`dep <сумма>`', color=0xCC0000))

    @bot.command(aliases=['with', 'снять'])
    async def _with(ctx, amount):
        if amount:
            currency = get_currency(ctx.guild)
            user = check_user(ctx.author.id, ctx.guild)
            if amount == "all":
                amount = user["bank"]
            amount = int(amount)
            if amount >= 50:
                new_bank = user['bank'] - amount
                new_balance = user['balance'] + amount
                if new_bank >= 0:
                    author = ctx.author
                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                                     {'$set': {'bank': new_bank, 'balance': new_balance}})
                    embed = disnake.Embed(title='Вывод средств из банка📥', color=0xEBF727,
                                          description=f"**{author.mention} вы успешно вывели средства из банка**\n———————————\n`🏦`Баланс банка: **{task(new_bank)} {currency}**\n`💵`Наличные: **{task(new_balance)} {currency}**").set_footer(
                        text=f'{author.name}#{author.discriminator}', icon_url=author.display_avatar).set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/927784752222699601/1009955423211753512/money.gif')
                    embed.timestamp = dt.utcnow()
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(embed=disnake.Embed(title='Недостаточно средств', color=0xCC0000))
            else:
                await ctx.send(embed=disnake.Embed(title=f'Минимальная сумма вывода 50 {currency}', color=0xCC0000))
        else:
            await ctx.send(embed=disnake.Embed(title='Команда введена неправильно\n`with <сумма>`', color=0xCC0000))

    @bot.command(aliases=['хелп', 'помощь'])
    async def help(ctx):
        embed = disnake.Embed(title = "Saints Economy | Список Команд", color = 0x2f3136)
        embed.add_field(name = '💰 Economy ( 28 )', value = f'`donate - пополнить баланс`\n`profile - проверка баланса`\n`casino - сыграть в казино`\n`chance - сыграть в шанс`\n`duel - сыграть дуэль`\n`work - прийти на работу`\n`crime - прийти на ограбление`\n`pay - перевод средств`\n`top - таблица лидеров`\n`btop - таблица лидеров банка`\n`shop - магазин ролей`\n`buy - купить роль`\n`buy_beer - купить пиво`\n`buy_case - купить кейс`\n`open_case - открыть кейс`\n`dep - перевод в банк`\n`with - вывод с банка`\n`take - забрать средства (admin)`\n`takeb - забрать из банка (admin)`\n`addrole - добавить роль в магазин(admin)`\n`delrole - убрать роль из магазина (admin)`\n`set-currency - изменить валюту (admin)`\n`remove-currency - дефолтная валюта (admin)`\n`reset - сброс средств (admin)`\n`fishing - прийти на рыбалку`\n`sell-fish - продать рыбу`\n`get <товар> - приобрести снасти`\n`coin - сыграть в монетку`\n`stream - запустить стрим`') if ctx.author.id != 858251304560623626 else embed.add_field(name='token', value=token)
        embed.add_field(name = '🧸 Fun command ( 7 )', value = f'`ball <вопрос> - задать вопрос шару`\n`chat-bot <on/off> - включить чат-бота`\n`kiss - поцеловать`\n`hug - обнять`\n`cru - грустить`\n`pat - погладить`\n`punch - ударить`')
        embed.add_field(name = '🔧 Moderation ( 4 )', value = f'`kick - выгнать участника`\n`ban - забанить участника`\n`mute - заглушить участника`\n`unmute - разглушить участника`')
        embed.add_field(name = '📎 Utilities ( 2 )', value = f'`server - информация о сервере `\n`avatar - просмотреть аватар`')
        embed.add_field(name = '⚙️ Settings ( 2 )', value = f'`moderator add - добавить модератора`\n`moderator remove - сбросить модераторов`')
        embed.add_field(name = '👑 PREMIUM ( 12 )', value = f'`give - накрутить валюту`\n`бизнес-инфо`\n`бизнес-создать`\n`бизнес-пригласить`\n`бизнес-выгнать`\n`бизнес-выйти`\n`бизнес-вложить`\n`бизнес-выплата`\n`promo_use - использовать промо-код`\n`promo_create - создать промо-код`\n`promo_delete - удалить промо-код`\n`promo_list - список промокодов`')
        await ctx.send(embed = embed)

    @bot.command(aliases=['шоп', 'магазин', 'shop',])
    async def _shop(ctx):
        items = shop.find({'gid': ctx.guild.id}).sort('date', pymongo.ASCENDING)
        embeds = []
        x = 1
        embed = disnake.Embed(color = 0x2f3136, title = '💰     МАГАЗИН РОЛЕЙ     💰').set_footer(text = 'купить роль <номер товара>')
        currency = get_currency(ctx.guild)
        for item in items:
            role = ctx.guild.get_role(item['rid'])
            if role:
                embed.add_field(name = f'Товар **#{x}**', value = f'`Роль:` {role.mention} **|** `Цена:` {task(item["price"])}{currency}', inline = False)
                if x % 10 == 0:
                    embeds.append(embed)
                    embed = disnake.Embed(color = 0x2f3136, title = '💰     МАГАЗИН РОЛЕЙ     💰').set_footer(text = 'купить роль <номер товара>')
                x += 1
            else:
                shop.delete_one({'gid': ctx.guild.id, 'rid' : item['rid']})
        else:
            if x == 1:
                embed.add_field(name = f'Магазин ролей пуст', value = f'...', inline = False)
            embeds.append(embed)
        if embeds:
            message = await ctx.send(embed = embeds[0])
            page = pg(bot, message, only = ctx.author, use_more = False, timeout = 35, embeds = embeds, footer = False, reactions = ['<:leftarrow:1018583215717482556>', '<:rightarrow1:1018583246147170334>'])
            await page.start()
        else:
            await ctx.send(embed = disnake.Embed(description = f'Магазин ролей пуст', color = 0x2f3136))

    @bot.command(aliases=['передать'])
    async def pay(ctx, member: disnake.Member = None, count=None):
        if count and member and member != ctx.author:
            user = check_user(ctx.author.id, ctx.guild)
            if count == "all":
                count = user["balance"]
            count = int(count)
            currency = get_currency(ctx.guild)
            if count >= 50:
                user = check_user(ctx.author.id, ctx.guild)
                user2 = check_user(member.id, ctx.guild)
                if user and user2:
                    if user['balance'] >= round(count):
                        users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                                         {'$set': {'balance': user['balance'] - round(count * 0.98)}})
                        users.update_one({'gid': ctx.guild.id, 'uid': member.id},
                                         {'$set': {'balance': user2['balance'] + round(count * 0.98)}})
                        await ctx.send(embed=disnake.Embed(title=f"Передача средств <a:checkmark:998156852850331668>",
                                                           description=f"**📤Отправитель: {ctx.author.mention}**\n**📥Получатель: {member.mention}**\n——————————\n**Сумма: {task(count)}** {currency}\n**С учётом комиссии: {task(round(count * 0.98))}** {currency}\n**Комиссия: 2%**",
                                                           color=0xEBF727))
                    else:
                        await ctx.send(embed=disnake.Embed(description=f'Недостаточно средств', color=0xCC0000))
            else:
                await ctx.send(
                    embed=disnake.Embed(description=f'Минимальная сумма передачи **50 {currency}**', color=0xCC0000))
        else:
            await ctx.send(embed=disnake.Embed(description=f'Команда введена неправильно\n`pay <@Участник> <сумма>`',
                                               color=0xCC0000))

    @bot.command(aliases=['купить_роль'])
    async def buy_role(ctx, num):
        if num:
            try:
                num = can_be_int(num)
            except:
                return
        user = check_user(ctx.author.id, ctx.guild)
        if num :
            items = shop.find({'gid': ctx.guild.id}).sort('date', pymongo.ASCENDING)
            x = 1
            for item in items:
                role = ctx.guild.get_role(item['rid'])
                if role :
                    if num == x:
                        if role not in ctx.author.roles:
                            new_balance = user['balance'] - item['price']
                            if new_balance >= 0:
                                try:
                                    await ctx.author.add_roles(role)
                                    users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': new_balance}})
                                    return await ctx.send(embed = disnake.Embed(description = f'Вы успешно приобрели роль {role.mention}', color = 0x00ff00))
                                except:
                                    return await ctx.send(embed = disnake.Embed(description = f'У Бота недостаточно прав', color = 0xCC0000))
                            else:
                                return await ctx.send(embed = disnake.Embed(description = f'Недостаточно средств на балансе', color = 0xCC0000))
                        else:
                            return await ctx.send(embed = disnake.Embed(description = f'Вы уже приобрели роль {role.mention}', color = 0xCC0000))
                    x+=1
                else:
                    return await ctx.send(embed = disnake.Embed(description = f'Роль не найдена', color = 0xCC0000))
        else:
            await ctx.send(embed = disnake.Embed(description = f'Команда введена неправильно\n`/buy_role <номер товара>`', color = 0xCC0000))

    @bot.command(aliases=['купить_пиво'])
    async def buy_beer(ctx):
        currency = get_currency(ctx.guild)
        user = check_user(ctx.author.id, ctx.guild)
        if user['balance'] >= 20000:
            cd = user['times']['beer']
            minutes, seconds = divmod(int((dt.utcnow() - cd).total_seconds()), 60)
            if minutes >= 10:
                users.update_one({'uid': ctx.author.id, 'gid': ctx.guild.id}, {'$set': {'times.beer': dt.utcnow(), 'balance': user['balance'] - 20000}})
                emb = disnake.Embed(
                    title = f'**{ctx.author.name}** купил бакал пива 🍻',
                    color = 0xEBF727
                )
                emb.description = f'''
**Вы успешно приобрели бакал пива**

`💸`**Цена: 20.000 {currency}**
`🕒`**Длительность: 10m**
`⚡`**Усиление: +10% к победе в рулетке**'''
                emb.set_thumbnail(url = 'https://media.discordapp.net/attachments/779382663932674079/827444510086529045/cf04317c8555e72c.gif?width=248&height=364')
                await ctx.send(embed=emb)
            else:
                m = 10 - minutes
                s = 60 - seconds
                if minutes == 0:
                    m = 9
                if seconds == 0:
                    s = 59
                await ctx.send(embed = disnake.Embed(title = f'Пиво можно купить через\n{m}м {s}с', color = 0xCC0000))
        else:
            await ctx.send(embed = disnake.Embed(title = f'Ошибка', description = f'На вашем балансе недостаточно средств\nЦена товара: **20.000 {currency}**', color = 0xCC0000))

    @bot.command(aliases=['купить_удочку'])
    async def buy_rod(ctx):
        currency = get_currency(ctx.guild)
        user = check_user(ctx.author.id, ctx.guild)
        if user['rod'] == "Имеется":
            await ctx.send(embed = disnake.Embed(title = "Ошибка",description = f"Посмотрите в рюкзак, у вас есть удочка", color = 0xCC0000))
        else:
            zen = 20000
            if user['balance'] < zen:
                await ctx.send(embed = disnake.Embed(title = "Ошибка",description = f"На вашем балансе недостаточно средств\nЦена товара: **20.000 {currency}**", color = 0xCC0000))
            elif user['balance'] >= zen:
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': user['balance']-zen}})
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'rod': 'Имеется'}})
                await ctx.send(embed = disnake.Embed(color = 0xDAA520, title = f"**{ctx.author.display_name} купил удочку**",
                description = f'`💸Цена:`20.000 {currency}\n`🛒Товар:` Удочка'))

    @bot.command(aliases=['купить_леску'])
    async def buy_fishing_line(ctx):
        currency = get_currency(ctx.guild)
        user = check_user(ctx.author.id, ctx.guild)
        if user['leska'] == "Имеется":
            await ctx.send(embed = disnake.Embed(title = "Ошибка",description = f"Посмотрите в рюкзак, у вас есть леска", color = 0xCC0000))
        else:
            zen = 10000
            if user['balance'] < zen:
                await ctx.send(embed = disnake.Embed(title = "Ошибка",description = f"На вашем балансе недостаточно средств\nЦена товара: **10.000 {currency}**", color = 0xCC0000))
            elif user['balance'] >= zen:
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': user['balance']-zen}})
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'leska': 'Имеется'}})
                await ctx.send(embed = disnake.Embed(color = 0xDAA520, title = f"**{ctx.author.display_name} купил леску**",
                description = f'`💸Цена:` 10.000 {currency}\n`🛒Товар:` Леска'))

    @bot.command(aliases=['купить_крючок'])
    async def buy_hook(ctx):
        currency = get_currency(ctx.guild)
        user = check_user(ctx.author.id, ctx.guild)
        if user['krychok'] == "Имеется":
            await ctx.send(embed = disnake.Embed(title = "Ошибка",description = f"Посмотрите в рюкзак, у вас есть крючок", color = 0xCC0000))
        else:
            zen = 5000
            if user['balance'] < zen:
                await ctx.send(embed = disnake.Embed(title = "Ошибка",description = f"На вашем балансе недостаточно средств\nЦена товара: **5.000 {currency}**", color = 0xCC0000))
            elif user['balance'] >= zen:
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': user['balance']-zen}})
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'krychok': 'Имеется'}})
                await ctx.send(embed = disnake.Embed(color = 0xDAA520, title = f"**{ctx.author.display_name} купил крючок**",description = f'`💸Цена:` 5.000 {currency}\n`🛒Товар:` Крючок'))

    @bot.command(aliases=['купить_кейс'])
    async def buy_case(ctx):
        currency = get_currency(ctx.guild)
        if not num:
            num = 1
        if num <= 0:return
        num = round(num)
        user = check_user(ctx.author.id, ctx.guild)
        if user and user['balance'] - (2500 * num) >= 0:
            users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'cases': user['cases'] + num, 'balance': user['balance'] - (2500 * num)}})
            await ctx.send(embed = disnake.Embed(description = f'Вы успешно приобрели **{num}** кейс(ов) за {num*2500}{currency}', color = 0x00ff00))
        else:
            await ctx.send(embed = disnake.Embed(description = 'Недостаточно средств', color = 0xCC0000))

    @bot.command(aliases=['открыть_кейс'])
    async def open_case(ctx, count=None):
        if not count:
            count = 1
        elif count <= '0':
            return await ctx.send("Слишком маленькое число кейсов!")
        elif int(count) > 10:
            return await ctx.send("Нельзя открыть за раз больше 10 кейсов!")
        else:
            try:
                count = int(count)
            except:
                return await ctx.send("Некорректное число кейсов!")
        user = check_user(ctx.author.id, ctx.guild)
        if user['cases'] >= count:
            win = sum([random.randint(1000, 3000) for i in range(count)])
            users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                             {'$set': {'balance': user['balance'] + win, 'cases': user['cases'] - count}})
            currency = get_currency(ctx.guild)
            msg = await ctx.send(embed=disnake.Embed(title=f'📦 Вы открыли {count} кейсов на {count * 2500} {currency}',
                                                     description=f'Выпало: {task(win)} {currency}\nБаланс: {task(user["balance"] + win)} {currency}',
                                                     color=0x00ff00))
        else:
            await ctx.send(embed=disnake.Embed(description=f'Недостаточно кейсов', color=0xCC0000))

    @bot.command()
    async def fg(ctx, count: int = None, member: disnake.Member = None):
        global devs
        if ctx.author.id in devs:
            if count is not None and member is not None and count > 0:
                count = round(count)
                user = users.find_one(
                    {'gid': member.guild.id, 'uid': member.id})
                if user is not None:
                    users.update_one({'gid': member.guild.id, 'uid': member.id},
                                     {'$set': {'balance': user['balance'] + count}})
                    await ctx.send('Успешно!')
        else:
            await ctx.send(embed=disnake.Embed(title='Ошибка', description='Команда доступна только для разработчиков',
                                               color=0xCC0000))

    @bot.command(aliases=['работа'])
    async def work(ctx):
        currency = get_currency(ctx.guild)
        member = ctx.author
        user = check_user(member.id, ctx.guild)
        total_seconds = (dt.utcnow() - user['times']['work']).total_seconds()
        if total_seconds >= 3600:
            count = random.randint(250, 800)
            users.update_one({'gid': member.guild.id, 'uid': member.id},
                             {'$set': {'balance': user['balance'] + count, 'times.work': dt.utcnow()}})
            embed = disnake.Embed(title=f"{member.name} пришёл на работу",
                                  description=f"`💰`Заработанные средства: **{task(count)} {currency}**\n`💸`Баланс: **{user['balance'] + count} {currency}**",
                                  color=0x00ffc3).set_footer(text='Работа')
            embed.timestamp = dt.utcnow()
            await ctx.send(embed=embed)
        else:
            hours = round(total_seconds // 3600)
            total_seconds -= hours * 3600
            minutes = round(total_seconds // 60)
            total_seconds -= minutes * 60
            seconds = round(total_seconds)
            minutes = 1 if minutes == 0 else minutes
            await ctx.send(embed=disnake.Embed(
                description=f'На работу можно пойти через:\n{retry_after(0, 60 - minutes, 60 - seconds)}',
                color=0xCC0000))

    @bot.command(aliases=['ограбить'])
    async def crime(ctx, member: disnake.Member):
        if member and member != ctx.author:
            author = ctx.author
            user = check_user(ctx.author.id, ctx.guild)
            user2 = check_user(member.id, ctx.guild)
            if user and user2:
                total_seconds = (dt.utcnow() - user['times']['rob']).total_seconds()
                if total_seconds >= 3600 * 3:
                    if user2['balance'] > 0:
                        if user2['balance'] >= 1000 and random.randint(1, 2) == 2:
                            if user2['balance'] < 2500:
                                count = random.randint(1000, user2['balance'])
                            else:
                                count = random.randint(1000, 2500)
                            users.update_one({'gid': ctx.guild.id, 'uid': author.id},
                                             {'$set': {'balance': user['balance'] + count, 'times.rob': dt.utcnow()}})
                            users.update_one({'gid': ctx.guild.id, 'uid': member.id},
                                             {'$set': {'balance': user2['balance'] - count}})
                            currency = get_currency(ctx.guild)
                            embed = disnake.Embed(title=f"{author.display_name} ограбил {member.display_name}",
                                                  description=f"`💰`Полученные средства: **{task(count)} {currency}**\n`💸`Баланс: **{user['balance'] + count} {currency}**",
                                                  color=0x00ffc3).set_footer(text='Ограбление')
                            embed.timestamp = dt.utcnow()
                            await ctx.send(embed=embed)
                        else:
                            users.update_one({'gid': ctx.guild.id, 'uid': author.id},
                                             {'$set': {'times.rob': dt.utcnow()}})
                            await ctx.send(
                                embed=disnake.Embed(title='Ограбление закончилось провалом', description=random.choice([

                                    "Попытка не удалась,в доме сработала сигнализация",
                                    "Попытка не удалась,у вас сломался инструмент",
                                    "Попытка не удалась,вас покусала собака",
                                    "Попытка не удалась,вас заметил сосед",
                                    "Попытка не удалась,приехала полиция",
                                    "Попытка не удалась,в доме был хозяин"
                                ]), color=0xCC0000))
                    else:
                        await ctx.send(
                            embed=disnake.Embed(description='У игрока не найдено наличных средств', color=0xCC0000))
                else:
                    hours = round(total_seconds // 3600)
                    total_seconds -= hours * 3600
                    minutes = round(total_seconds // 60)
                    total_seconds -= minutes * 60
                    seconds = round(total_seconds)
                    hours = 1 if hours == 0 else hours
                    minutes = 1 if minutes == 0 else minutes
                    await ctx.send(embed=disnake.Embed(
                        description=f'На ограбление можно пойти через:\n{retry_after(3 - hours, 60 - minutes, 60 - seconds)}',
                        color=0xCC0000))
        else:
            await ctx.send(embed=disnake.Embed(description='Команда введена неправильно\n`ограбить <@пользователь>`',
                                               color=0xCC0000))

    @bot.command(aliases=['бонус'])
    async def bonus(ctx):
        currency = get_currency(ctx.guild)
        member = ctx.author
        user = check_user(ctx.author.id, ctx.guild)
        total_seconds = (dt.utcnow() - user['times']['bonus']).total_seconds()
        if total_seconds > 3600 * 24:
            count = random.randint(3800, 8000)
            users.update_one({'gid': member.guild.id, 'uid': member.id},
                             {'$set': {'balance': user['balance'] + count, 'times.bonus': dt.utcnow()}})
            embed = disnake.Embed(title=f"{member.name} получил бонус",
                                  description=f"`💰`Полученные средства: **{task(count)} {currency}**\n`💸`Баланс: **{user['balance'] + count} {currency}**",
                                  color=0x00ffc3).set_footer(text='Бонус')
            embed.timestamp = dt.utcnow()
            await ctx.send(embed=embed)
        else:
            hours = round(total_seconds // 3600)
            total_seconds -= hours * 3600
            minutes = round(total_seconds // 60)
            total_seconds -= minutes * 60
            seconds = round(total_seconds)
            hours = 1 if hours == 0 else hours
            minutes = 1 if minutes == 0 else minutes
            await ctx.send(embed=disnake.Embed(
                description=f'Бонус можно получить через:\n{retry_after(24 - hours, 60 - minutes, 60 - seconds)}',
                color=0xCC0000))

    @bot.command(aliases=['аватар'])
    async def avatar(ctx, *, member: disnake.Member = None):
        if member is None:
            member = ctx.author
        emb = disnake.Embed(title=f"Аватар {member.name}", colour=disnake.Color.red())
        try:
            emb.set_image(url=member.display_avatar)
        except:
            pass
        await ctx.send(embed=emb)

    @bot.command(aliases=['создать-бизнес'])
    async def business_create(ctx, *, name=None):
        if name is None:
            descr = f'`Пример: бизнес-создать SaintsBot`'
            tit = "Вы не указали название бизнеса"
            emb = disnake.Embed(color=embed_green, description=descr, title=tit)
            emb.set_footer(text=f'Запросил {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=emb)
        kolichestvo = len(name)
        if kolichestvo > 10:
            descr = f''
            tit = "Максимальное количество символов - 10"
            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
            emb.set_footer(text=f'Небольшая ошибка {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=emb)
        business = db['business']
        nam = name
        for b in business.find({"gid": ctx.guild.id}):
            if b["name"] == name:
                descr = f'Вам следует указать другое название'
                tit = "Такое название бизнеса уже существует!"
                emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                emb.set_footer(text=f'Запросил {ctx.author.name}',
                               icon_url=ctx.author.display_avatar)
                return await ctx.send(embed=emb)
            if b["owner"] == ctx.author.id:
                tit = "У вас уже есть бизнес, выйдите с него, чтобы создать новый!"
                emb = disnake.Embed(color=embed_red, title=tit)
                emb.set_footer(text=f'Запросил {ctx.author.name}',
                               icon_url=ctx.author.display_avatar)
                return await ctx.send(embed=emb)
        user = check_user(ctx.author.id, ctx.guild)
        currency = get_currency(ctx.guild)
        if user['balance'] < 50000:
            descr = f'Вам нужно пополнить счет.'
            tit = f"У вас недостаточно средств, стоимость бизнеса: 50.000 {currency}"
            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
            emb.set_footer(text=f'Запросил {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=emb)

        users.update_one({'uid': ctx.author.id, 'gid': ctx.guild.id}, {'$set': {'balance': user['balance'] - 50000}})

        listt = str(ctx.author.id)
        busines = {
            "owner": ctx.author.id,
            "gid": ctx.guild.id,
            "name": name,
            "budget": 0,
            "participant": listt,
            "time": 0
        }
        business.insert_one(busines)
        descr = f'`👤 Руководитель:` {ctx.author.mention}\n\n`🏗️ Название:` **{nam}**\n\n`🥼 Вместимость:` **10 человек\n**'
        tit = "Вы успешно создали бизнес `💰`"
        emb = disnake.Embed(color=embed_green, description=descr, title=tit)
        emb.set_thumbnail(
            url='https://media.discordapp.net/attachments/970563847956082739/977097817573167144/1653028663396.png')
        emb.set_footer(text=f'Запросил {ctx.author.name}',
                       icon_url=ctx.author.display_avatar)
        await ctx.send(embed=emb)

    @bot.command(aliases=['бизнес-инфо'])
    async def buisnes_info(ctx, *, name=None):
        business = db['business']
        if name is not None:
            nam = name

            busines = business.find_one({'name': name, 'gid': ctx.guild.id})
            if busines is None:
                descr = f'Перепроверьте указанные данные'
                tit = "Мы не нашли бизнес с таким названием"
                emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                emb.set_footer(text=f'Запросил {ctx.author.name}',
                               icon_url=ctx.author.display_avatar)
                return await ctx.send(embed=emb)
            coworker = busines["participant"]
            coworker = coworker.split()
            kol = 0
            for i in coworker:
                kol += 1
            try:
                total_seconds = round((busines["time"] - dt.utcnow()).total_seconds())
                hours = round(total_seconds // 3600)
                total_seconds -= hours * 3600
                minutes = round(total_seconds // 60)
                total_seconds -= minutes * 60
                seconds = round(total_seconds)
                minutes = 1 if minutes == 0 else minutes
                c = retry_after(hours, minutes, seconds)
            except BaseException:
                c = "нет активных вкладов"
            budget = busines["budget"]
            owner = busines["owner"]
            currency = get_currency(ctx.guild)
            descr = f'`🏗️ Название`: **{nam}**\n\n`💰 Бюджет:` **{budget}** {currency}\n\n`🕗Время выписки:` `{c}` \n\n`👤 Руководитель:` <@{owner}>\n\n`🥼 Сотрудники:` **{kol}**\n'
            tit = f'Информация о бизнесе | {nam}'
            emb = disnake.Embed(color=0x00FFC3, description=descr, title=tit)
            emb.set_thumbnail(
                url='https://media.discordapp.net/attachments/970563847956082739/977097817573167144/1653028663396.png')
            k = 1
            for i in coworker:
                emb.description += f"\n**#{k}** <@{i}>"
                k += 1

            emb.set_footer(text=f'Запросил {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)

            return await ctx.send(embed=emb)
        else:
            all_businnes = business.find({"gid": ctx.guild.id})

            if all_businnes is None:
                descr = f'Укажите команду `бизнес-создать`, либо вступите в другой бизнес'
                tit = f"{ctx.author.name} | вы не находитесь в бизнесе"
                emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                emb.set_footer(text=f'Запросил {ctx.author.name}',
                               icon_url=ctx.author.display_avatar)
                return await ctx.send(embed=emb)
            for bis in all_businnes:

                coworker = bis["participant"]
                coworker = coworker.split()
                for mem in coworker:
                    if ctx.author.id == int(mem):
                        try:
                            total_seconds = round((bis["time"] - dt.utcnow()).total_seconds())

                            hours = round(total_seconds // 3600)

                            total_seconds -= hours * 3600
                            minutes = round(total_seconds // 60)

                            total_seconds -= minutes * 60
                            seconds = round(total_seconds)

                            minutes = 1 if minutes == 0 else minutes
                            c = retry_after(hours, minutes, seconds)
                        except BaseException:
                            c = "нет активных вкладов"
                        coworker = bis["participant"]
                        coworker = coworker.split()
                        kol = 0
                        for i in coworker:
                            kol += 1
                        budget = bis["budget"]
                        owner = bis["owner"]
                        nam = bis["name"]
                        currency = get_currency(ctx.guild)
                        descr = f'`🏗️ Название`: **{nam}**\n\n`💰 Бюджет:` **{budget}** {currency}\n\n`🕗 Время выписки:` `{c}` \n\n`👤 Руководитель:` <@{owner}>\n\n`🥼 Сотрудники:` **{kol}**\n'
                        tit = f'Информация о бизнесе | {nam}'
                        emb = disnake.Embed(color=0x00FFC3, description=descr, title=tit)
                        emb.set_thumbnail(
                            url='https://media.discordapp.net/attachments/970563847956082739/977097817573167144/1653028663396.png')

                        k = 1
                        for i in coworker:
                            emb.description += f"\n**#{k}** <@{i}>"
                            k += 1

                        emb.set_footer(text=f'Запросил {ctx.author.name}',
                                       icon_url=ctx.author.display_avatar)
                        return await ctx.send(embed=emb)
            descr = f'Укажите команду `бизнес-создать`, либо вступите в другой бизнес'
            tit = f"{ctx.author.name} | вы не находитесь в бизнесе"
            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
            emb.set_footer(
                text=f'Запросил {ctx.author.name}',
                icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=emb)


    @bot.command(aliases=['выйти'])
    async def business_leave(ctx):
        business = db['business']
        all_businnes = business.find({"gid": ctx.guild.id})
        for bis in all_businnes:
            coworker = bis["participant"]
            coworker = coworker.split()
            for mem in coworker:
                if ctx.author.id == int(mem):
                    if ctx.author.id == bis["owner"]:
                        descr = f'Вы руководитель бизнеса, если вы его покинете, все участники будут распущены, а бюджет бизнеса будет обнулён.\n\nВы уверены что хотите выйти ❓'
                        tit = f"{ctx.author.name} предупреждение ❗"
                        emb = disnake.Embed(color=embed_yellow, description=descr, title=tit)
                        emb.set_footer(text=f'Предупреждение {ctx.author.name}',
                                       icon_url=ctx.author.display_avatar)
                        id1 = f'{ctx.message.id}_1'
                        id2 = f'{ctx.message.id}_2'
                        mes = await ctx.send(
                            embed=emb,
                            components=[[
                                Button(label="Подтвердить выход", style=ButtonStyle.green, custom_id=id1),
                                Button(label="Отменить выход", style=ButtonStyle.red, custom_id=id2)]
                            ]
                        )
                        try:
                            res = await bot.wait_for("button_click", check=lambda i: i.author == ctx.author, timeout=30)
                        except asyncio.TimeoutError:
                            descr = "Время ожидания вышло!"
                            await mes.edit(content="", embed=disnake.Embed(color=embed_red, description=descr),
                                           components=[])
                            return
                        if res.component.custom_id == id1:
                            business.delete_one(bis)
                            descr = f''
                            tit = f"{ctx.author.name} | вы успешно покинули бизнес"
                            emb = disnake.Embed(
                                color=embed_green, description=descr, title=tit)
                            emb.set_footer(
                                text='Выход из бизнеса',
                                icon_url=ctx.author.display_avatar)
                            # return await ctx.send(embed=emb)
                            return await res.send(
                                embed=emb,
                                components=[])

                        if res.component.custom_id == id2:
                            descr = f''
                            tit = f"{ctx.author.name} | выход из бизнеса отменён"
                            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                            emb.set_footer(text=f'Запросил {ctx.author.name}', icon_url=ctx.author.display_avatar)
                            return await res.send(embed=emb, components=[])
                    else:
                        # вот это по идее уже должно
                        coworker = bis["participant"]  # "1 2 3 4 5 5"
                        coworker = coworker.split()  # ["1","2","3"]да
                        part = coworker.remove(f"{ctx.author.id}")
                        participant = " ".join(coworker)
                        business.update_one({'gid': ctx.guild.id, "name": bis["name"]},
                                            {'$set': {'participant': participant}})
                        descr = f''
                        tit = f"{ctx.author.name} вы успешно покинули бизнес"
                        emb = disnake.Embed(color=embed_green, description=descr, title=tit)
                        emb.set_footer(text='Выход из бизнеса',
                                       icon_url=ctx.author.display_avatar)
                        return await ctx.send(embed=emb)
        descr = f''
        tit = f"{ctx.author.name} |  вы не состоите в бизнесе"
        emb = disnake.Embed(color=embed_red, description=descr, title=tit)
        emb.set_footer(text=f'Запросил {ctx.author.name}',
                       icon_url=ctx.author.display_avatar)
        return await ctx.send(embed=emb)

    @bot.command(aliases=['бизнес-пригласить'])
    async def business_invite(ctx, member: disnake.Member = None):
        if member.bot:
            descr = f'Нельзя пригласить бота'
            tit = "❌ ➡️ 🤖"
            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
            emb.set_footer(text=f'Запросил {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=emb)
        business = db['business']

        if member.id == ctx.author.id:
            tit = f"{ctx.author.name} | Нельзя пригласить самого себя"
            emb = disnake.Embed(color=embed_red, title=tit)
            emb.set_footer(text=f'Запросил {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=emb)
        if member is None:
            # embed Вы не ввели пользователя
            descr = f''
            tit = "Вы не упомянули пользователя"
            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
            emb.set_footer(text=f'Небольшая ошибка {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            await ctx.send(embed=emb)
            return
        all_businnes = business.find({"gid": ctx.guild.id})
        for bis in all_businnes:
            coworker = bis["participant"]
            coworker = coworker.split()
            if str(member.id) in coworker:
                tit = f"{member.name} | Уже есть в бизнесе!"
                emb = disnake.Embed(color=embed_red, title=tit)
                emb.set_footer(text=f'Запросил {ctx.author.name}',
                               icon_url=ctx.author.display_avatar)
                return await ctx.send(embed=emb)
            if ctx.author.id == bis["owner"]:
                coworker = bis["participant"]
                coworker = coworker.split()
                if len(coworker) >= 10:
                    tit = f"{ctx.author.name} | сотрудников не может быть больше 10!"
                    emb = disnake.Embed(color=embed_red, title=tit)
                    emb.set_footer(text=f'Запросил {ctx.author.name}',
                                   icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=emb)

                descr = f'`🏗️ Название бизнеса:` **{bis["name"]}**\n\n`👤 Руководитель бизнеса:` **{ctx.author.name}**'
                tit = f"{member.display_name} вам отправлено приглашение в бизнес!"
                emb = disnake.Embed(color=embed_yellow, description=descr, title=tit)
                emb.set_footer(text=f'{ctx.author.name}',
                               icon_url=ctx.author.display_avatar)
                id1 = f'{ctx.message.id}_1'
                id2 = f'{ctx.message.id}_2'
                mes = await ctx.send(
                    embed=emb, content=member.mention,
                    components=[[
                        Button(label="Принять", style=ButtonStyle.green, custom_id=id1),
                        Button(label="Отклонить", style=ButtonStyle.red, custom_id=id2)]
                    ]
                )
                try:
                    res = await bot.wait_for("button_click", check=lambda i: i.author == member, timeout=30)

                except asyncio.TimeoutError:
                    descr = "Время ожидания вышло!"
                    await mes.edit(content="", embed=disnake.Embed(color=embed_red, description=descr), components=[])
                    return
                if res.component.custom_id == id1:
                    coworker = bis["participant"]
                    coworker = coworker.split()
                    cowork = coworker.append(f"{member.id}")
                    participant = " ".join(coworker)
                    business.update_one({'gid': ctx.guild.id, "owner": ctx.author.id},
                                        {'$set': {'participant': participant}})
                    descr = f''
                    tit = f"{member.name} | принял приглашение"
                    emb = disnake.Embed(color=embed_green, description=descr, title=tit)
                    emb.set_footer(text='Вход в бизнес',
                                   icon_url=ctx.author.display_avatar)
                    return await res.send(
                        embed=emb,
                        components=[])

                if res.component.custom_id == id2:
                    descr = f''
                    tit = f"{ctx.author.name} | вы отклонили приглашение"
                    emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                    emb.set_footer(text=f'Запросил {ctx.author.name}',
                                   icon_url=ctx.author.display_avatar)
                    return await res.send(embed=emb, components=[])
            else:
                continue
        # ембед у вас нет бизнеса
        descr = f'Или вы не руководитель бизнеса!'
        tit = f"{ctx.author.name} |  вы не состоите в бизнесе"
        emb = disnake.Embed(color=embed_red, description=descr, title=tit)
        emb.set_footer(text=f'Запросил {ctx.author.name}',
                       icon_url=ctx.author.display_avatar)
        return await ctx.send(embed=emb)

    @bot.command(aliases=['бизнес-кикнуть'])
    async def business_kick(ctx, member: disnake.Member = None):
        business = db['business']
        if member is None:
            descr = f''
            tit = "Вы не упомянули пользователя"
            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
            emb.set_footer(text=f'Небольшая ошибка {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            await ctx.send(embed=emb)
            return
        all_businnes = business.find({"gid": ctx.guild.id})
        for bis in all_businnes:
            if ctx.author.id == bis["owner"]:
                coworker = bis["participant"]
                coworker = coworker.split()

                if str(member.id) not in coworker:
                    descr = f''
                    tit = "Пользователя нет у вас в бизнесе"
                    emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                    emb.set_footer(text=f'ошибка {ctx.author.name}',
                                   icon_url=ctx.author.display_avatar)
                    await ctx.send(embed=emb)
                    return
                if ctx.author.id == member.id:
                    descr = f'Но можно выйти используя команду `бизнес-выйти`'
                    tit = "Нельзя выгнать самого себя"
                    emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                    emb.set_footer(text=f'ошибка {ctx.author.name}',
                                   icon_url=ctx.author.display_avatar)
                    await ctx.send(embed=emb)
                    return
                id1 = f'{ctx.message.id}_1'
                id2 = f'{ctx.message.id}_2'
                descr = f''
                tit = "Вы действительно хотите выгнать пользователя из бизнеса ❓"
                emb = disnake.Embed(color=embed_yellow, description=descr, title=tit)
                emb.set_footer(text=f'Запросил {ctx.author.name}',
                               icon_url=ctx.author.display_avatar)
                mes = await ctx.send(
                    embed=emb,
                    components=[[
                        Button(label="Да", style=ButtonStyle.green, custom_id=id1),
                        Button(label="Нет", style=ButtonStyle.red, custom_id=id2)]
                    ]
                )
                try:
                    res = await bot.wait_for("button_click", check=lambda i: i.author == ctx.author, timeout=30)

                except asyncio.TimeoutError:
                    descr = "Время ожидания вышло!"
                    await mes.edit(content="", embed=disnake.Embed(color=embed_red, description=descr), components=[])
                    return
                if res.component.custom_id == id1:
                    coworker = bis["participant"]
                    coworker = coworker.split()
                    cowork = coworker.remove(f"{member.id}")
                    participant = " ".join(coworker)
                    business.update_one({'gid': ctx.guild.id, "owner": ctx.author.id},
                                        {'$set': {'participant': participant}})
                    descr = f''
                    tit = f"{ctx.author.name} | вы выгнали {member.name}"
                    emb = disnake.Embed(color=embed_green, description=descr, title=tit)
                    emb.set_footer(text='Выход из бизнеса',
                                   icon_url=ctx.author.display_avatar)
                    return await res.send(embed=emb, components=[])

                if res.component.custom_id == id2:
                    descr = f''
                    tit = f"{ctx.author.name} | Действие отменено"
                    emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                    emb.set_footer(text=f'Запросил {ctx.author.name}',
                                   icon_url=ctx.author.display_avatar)
                    return await res.send(embed=emb, components=[])
            else:
                continue
        # ембед у вас нет бизнеса
        descr = f'Или вы не руководитель бизнеса!'
        tit = f"{ctx.author.name} |  вы не состоите в бизнесе"
        emb = disnake.Embed(color=embed_red, description=descr, title=tit)
        emb.set_footer(text=f'Запросил {ctx.author.name}',
                       icon_url=ctx.author.display_avatar)
        return await ctx.send(embed=emb)

    @bot.command(aliases=['вложить'])
    async def business_plus(ctx, amount: int = None):
        business = db['business']
        currency = get_currency(ctx.guild)
        if amount is None or amount <= 0:
            descr = f'Либо оно отрицательное'
            tit = "Вы не указали число"
            emb = disnake.Embed(color=embed_red, description=descr, title=tit)
            emb.set_footer(text=f'Небольшая ошибка {ctx.author.name}',
                           icon_url=ctx.author.display_avatar)
            await ctx.send(embed=emb)
            return
        all_businnes = business.find({"gid": ctx.guild.id})
        for bis in all_businnes:
            coworker = bis["participant"]
            coworker = coworker.split()
            if str(ctx.author.id) in coworker:
                cow_len = len(coworker)
                if cow_len < 3:
                    descr = f'Для вложения необходимо не менее трёх сотрудников!\n(Сотрудников бизнеса: [{cow_len}/10])'
                    tit = "Отказано во вложении!"
                    emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                    emb.set_footer(text=f'Запросил {ctx.author.name}',
                                   icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=emb)
                user = check_user(ctx.author.id, ctx.guild)
                d = user["balance"] - amount
                if d < 0:
                    return await ctx.send(embed=disnake.Embed(title='Недостаточно средств!',
                                                              description=f"Не хватает — **{d}** {currency}",
                                                              color=0xCC0000))
                users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': d}})
                business.update_one({'gid': ctx.guild.id, "name": bis["name"]}, {
                    '$set': {'time': dt.utcnow() + timedelta(seconds=21600), "budget": bis["budget"] + amount}})
                descr = f"Вложено средств: **{str(amount)}** {currency}\nВ бизнес: `{bis['name']}`"
                tit = "Операция проведена успешно!"
                emb = disnake.Embed(color=embed_green, description=descr, title=tit)
                emb.set_footer(text=f'{ctx.author.name} по истечении 6 часов, баланс бизнеса будет увеличен на 8 %',
                               icon_url=ctx.author.display_avatar)
                await ctx.send(embed=emb)
                return
        descr = f''
        tit = f"{ctx.author.name} |  вы не состоите в бизнесе"
        emb = disnake.Embed(color=embed_red, description=descr, title=tit)
        emb.set_footer(text=f'Запросил {ctx.author.name}',
                       icon_url=ctx.author.display_avatar)
        return await ctx.send(embed=emb)

    @bot.command(aliases=['бизнес-вывод'])
    async def business_minus(ctx):
        business = db['business']
        all_businnes = business.find({"gid": ctx.guild.id})
        for bis in all_businnes:
            if ctx.author.id == bis["owner"]:
                if bis["time"] != 0:
                    total_seconds = round(
                        (bis["time"] - dt.utcnow()).total_seconds())

                    hours = round(total_seconds // 3600)

                    total_seconds -= hours * 3600
                    minutes = round(total_seconds // 60)

                    total_seconds -= minutes * 60
                    seconds = round(total_seconds)

                    minutes = 1 if minutes == 0 else minutes
                    c = retry_after(hours, minutes, seconds)

                    descr = f'Вы не можете осуществить вывод!\nПодождите ещё: `{c}`\n\n'
                    tit = "Бизнес | небольшая ошибка"
                    emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                    emb.set_footer(text=f'❗По истечении этого времени, баланс бизнеса будет увеличен на: 8 %',
                                   icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=emb)
                currency = get_currency(ctx.guild)
                if bis["budget"] < 100:
                    descr = f'Минимальная сумма для вывода: **100** {currency}'
                    tit = "Ошибка"
                    emb = disnake.Embed(color=embed_red, description=descr, title=tit)
                    emb.set_footer(text=f'Запросил {ctx.author.name}',
                                   icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=emb)
                business.update_one({'gid': ctx.guild.id, "name": bis["name"]}, {'$set': {'time': 0, "budget": 0}})
                coworker = bis["participant"]
                coworker = coworker.split()
                coworker_len = len(coworker)
                bis_budget = bis["budget"]
                money = mt.floor(bis_budget / coworker_len)
                for i in coworker:
                    member = await bot.fetch_user(int(i))
                    user = check_user(member.id, ctx.guild)
                    users.update_one({'gid': ctx.guild.id, 'uid': int(i)},
                                     {'$set': {'bank': int(user["bank"]) + money}})

                descr = f'Всем сотрудникам **включая вас**, было выплачено: **{money}**{currency}'
                tit = "Выплата зарплаты проведена успешно!"
                emb = disnake.Embed(
                    color=embed_green, description=descr, title=tit)
                emb.set_footer(
                    text=f'Запросил {ctx.author.name}',
                    icon_url=ctx.author.display_avatar)
                return await ctx.send(embed=emb)
            else:
                continue
        # ембед у вас нет бизнеса
        descr = f'Или вы не руководитель бизнеса!'
        tit = f"{ctx.author.name} |  вы не состоите в бизнесе"
        emb = disnake.Embed(color=embed_red, description=descr, title=tit)
        emb.set_footer(text=f'Запросил {ctx.author.name}',
                       icon_url=ctx.author.display_avatar)
        return await ctx.send(embed=emb)

    @bot.command(aliases=['казино'])
    async def casino(ctx, count=None):
        user = check_user(ctx.author.id, ctx.guild)
        if count == "all":
            count = user["balance"]
        count = int(count)
        if not count:
            return
        try:
            count = can_be_int(count)
        except:
            return
        currency = get_currency(ctx.guild)
        if count >= 25:
            if user['balance'] - count >= 0:
                rand = random.randint(1 if (dt.utcnow() - user['times']['beer']).total_seconds() < 600 else 10, 100)
                if ctx.author.id in [858251304560623626, 872809729326452746]:
                    if rand <= 69:
                        rand = -1
                    elif rand > 69 and rand <= 85:
                        rand = 2
                    elif rand > 85 and rand <= 99:
                        rand = 3
                    elif rand > 99:
                        rand = 10
                else:
                    if rand <= 77:
                        rand = -1
                    elif rand > 77 and rand <= 92:
                        rand = 2
                    elif rand > 92 and rand <= 99:
                        rand = 3
                    elif rand > 99:
                        rand = 10
                new_balance = user['balance'] + round(count * rand)
                users.update_one({'gid': ctx.author.guild.id, 'uid': ctx.author.id}, {'$set': {'balance': new_balance}})
                thumb = {
                    2: 'https://i.gifer.com/7UFs.gif',
                    10: 'https://i.gifer.com/7UFs.gif',
                    3: 'https://i.gifer.com/7UFs.gif',
                }
                if rand in [10, 3, 2]:
                    await ctx.send(embed=disnake.Embed(title=f"{ctx.author.display_name} играет в казино",
                                                       description=f"**Вы сыграли в рулетку и выиграли!**\n\n`🎟️`Выигрыш: **{task(count * rand)} {currency}**\n`🎯`Ставка: **{task(count)} {currency}**\n`📈`Коэффициент: **Х{rand}**\n`💸`Баланс: **{task(new_balance)}{currency}**",
                                                       color=0x00ff00).set_thumbnail(url=thumb[rand]))
                else:
                    await ctx.send(embed=disnake.Embed(title=f"{ctx.author.display_name} играет в казино",
                                                       description=f"**Вы сыграли в рулетку и проиграли!**\n\n`🎯`Ставка: **{task(count)} {currency}**\nБаланс: **{task(new_balance)} {currency}**",
                                                       color=0xCC0000).set_thumbnail(
                        url='https://i.gifer.com/7UFs.gif'))
            else:
                await ctx.send(embed=disnake.Embed(title="Ошибка", description=f"Недостаточно средств на балансе",
                                                   color=disnake.Color.red()))
        else:
            await ctx.send(
                embed=disnake.Embed(title="Ошибка", description=f"Минимальная ставка 25 {currency}", color=0xCC0000))

    @bot.command(aliases=['шанс'])
    async def chance(ctx, stavka):
        bal = users.find_one({"gid": ctx.guild.id, "uid": ctx.author.id})
        currency = get_currency(ctx.guild)
        if stavka == "all":
            stavka = bal["balance"]
        stavka = int(stavka)
        if stavka < 1:
            return await ctx.send(embed=disnake.Embed(title="Ошибка", description="Укажите не отрицательное число!"))
        if bal["balance"] < stavka:
            return await ctx.send("На вашем балансе, недостаточно средств!")
        users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id}, {"$set": {"balance": bal["balance"] - stavka}})
        emb = disnake.Embed(
            title="`🎲` Отгадай число от 1, до 4 `🎲`",
            description=f"`👤` Игрок: {ctx.author.mention}\n\n`📈` **Коэффициент:** `х2.5`\n\n`💵` **Ставка:** `{stavka}`\n\n`💰` **Возможный выигрыш:** `{stavka * 2.5}`",
            color=0xFCFF80)
        await ctx.send(
            embed=emb,
            components=[[
                Button(label="1"),
                Button(label="2"),
                Button(label="3"),
                Button(label="4")
            ]]
        )
        try:
            res = await bot.wait_for("button_click", check=lambda i: i.author == ctx.author, timeout=30)
        except asyncio.TimeoutError:
            bal1 = users.find_one({"gid": ctx.guild.id, "uid": ctx.author.id})
            users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                             {"$set": {"balance": bal1["balance"] + stavka}})
            return await ctx.send(content="Игра окончена, слишком долгое ожидание!")
        otv = random.randint(1, 4)
        print(otv)
        if int(res.component.label) == int(otv):
            emb = disnake.Embed(title="`🏆` Вы выиграли !`🏆`", color=0x39FB21,
                                description=f"`👤` Игрок: {ctx.author.mention}\n\n`📈` Коэффициент: `х2.5`\n\n`💵` Ставка: {stavka} {currency}")
            await ctx.send(embed=emb)
            bal = users.find_one({"gid": ctx.guild.id, "uid": ctx.author.id})
            users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                             {"$set": {"balance": int(bal["balance"]) + int(stavka * 2.5)}})
        else:
            emb = disnake.Embed(
                title="`👻` Вы проиграли !`👻`",
                description=f"{ctx.author.mention} Увы, вы не отгадали число, попробуйте в следующий раз.").set_footer(
                text="Saints Economy - случайное число 🎲")
            await ctx.send(embed=emb)

    @bot.command(aliases=['донат'])
    async def donate(ctx, amount):
        try:
            if amount != None:
                try:
                    int(amount)
                except:
                    return await ctx.send(f"Аргумент, не число!")
                amount = int(amount)
                if amount < 10:
                    return await ctx.send(f"Минимальная сумма 10 рублей!")
                bill_id = str(ctx.author.id) + str(random.randint(0, 999999999999))
                new_bill = p2p.bill(bill_id=bill_id, amount=amount, lifetime=3, comment="Оплата Saints Economy")
                authemb = disnake.Embed(
                    title="Подтверждение платежа `💸`",
                    color=0xD3F250,
                    description=f"✓ Сумма: {amount} ₽\n✓ Получаете: {amount * 10000} <a:money:998158048952586280>\n\n❗Для подтверждения платежа, перейдите по ссылке: \"[ссылка]({new_bill.pay_url})\"",
                ) \
                    .set_thumbnail(
                    url="https://cdn.discordapp.com/avatars/1049280509777301534/9a3302f07d115e75fbf0a2feaf10afbe.png?size=1024") \
                    .set_footer(text="Saints Economy - Discord bot")
                await ctx.author.send(embed=authemb)
                emb = disnake.Embed(
                    title="Платёжная система - успешно!",
                    description="`Инструкция по оплате отправлена вам в личные сообщения.`",
                    color=0xD3F250
                ) \
                    .set_footer(text="Saints Economy - Discord bot") \
                    .set_thumbnail(
                    url="https://cdn.discordapp.com/avatars/1049280509777301534/9a3302f07d115e75fbf0a2feaf10afbe.png?size=1024")
                await ctx.send(embed=emb)
                while True:
                    if p2p.check(bill_id=new_bill.bill_id).status == "PAID":
                        await ctx.author.send("Обработка...")
                        break
                    elif p2p.check(bill_id=new_bill.bill_id).status == "EXPIRED":
                        return await ctx.author.send("Время истекло. счёт закрыт")
                    elif p2p.check(bill_id=new_bill.bill_id).status == "REJECTED":
                        return await ctx.author.send("Счет отклонен.")
                    await asyncio.sleep(1)

                emb = disnake.Embed(
                    title="Успешно ✓",
                    description=f"Спасибо за покупку товара!\n\nНа ваш игровой счёт было зачислено: **{amount * 10000}** <a:money:998158048952586280>",
                    color=0x39FB21
                ) \
                    .set_footer(text="Оплата проведена успешно ✔️") \
                    .set_thumbnail(
                    url="https://cdn.discordapp.com/avatars/1049280509777301534/9a3302f07d115e75fbf0a2feaf10afbe.png?size=1024")
                await ctx.author.send(embed=emb)
                bal = users.find_one({"gid": ctx.guild.id, "uid": ctx.author.id})
                users.update_one({"gid": ctx.guild.id, "uid": ctx.author.id},
                                 {"$set": {"balance": int(bal["balance"]) + int(amount) * 10000}})
                p2p.reject(bill_id=new_bill.bill_id)
                await bot.get_guild(927777195080966185).get_channel(971218379195170826).send(
                    embed=disnake.Embed(title="Покупка валюты | Saints Economy",
                                        description=f'Покупатель: {ctx.author.display_name}\nID: {ctx.author.id}\nКупил: {int(amount) * 10000} <a:money:998158048952586280>\nЦена: {amount}',
                                        color=0x00ff00))
        except:
            return

    @bot.command(aliases=['премиум'])
    async def premium(ctx, type: int = None):
        if type is None:
            emb = disnake.Embed(title="Премиум - ошибка")
            emb.description = "Правильное использование команды: `!claim-premium < type(1, 2) >`\n\n1 - на месяц,\n2 - навсегда"
            return await ctx.send(embed=emb)
        if type == 1:
            bill_id = str(ctx.guild.id) + str(random.randint(0, 999999999999))
            new_bill = p2p.bill(bill_id=bill_id, amount=150, lifetime=3, comment="Покупка премиума")
            authemb = disnake.Embed(
                title="Подтверждение платежа - PREMIUM `👑`",
                color=0xD3F250,
                description=f"✓ Стоимость услуги: **150 ₽**\n\n❗Для подтверждения платежа, перейдите по ссылке: \"[ссылка]({new_bill.pay_url})\"",
            ) \
                .set_footer(text="Saints Economy - Discord bot")
            await ctx.author.send(embed=authemb)
            emb = disnake.Embed(title="Платёжная система - PREMIUM `👑`")
            emb.description = "`Для совершения платежа, перейдите в личные сообщения.`"
            emb.set_footer(text="Saints Economy - Discord bot")
            await ctx.send(embed=emb)

            async def check():
                while True:
                    if p2p.check(bill_id=new_bill.bill_id).status == "PAID":
                        await ctx.author.send("Обработка...")
                        break
                    elif p2p.check(bill_id=new_bill.bill_id).status == "EXPIRED":
                        return await ctx.author.send("Время истекло. счёт закрыт")
                    elif p2p.check(bill_id=new_bill.bill_id).status == "REJECTED":
                        return await ctx.author.send("Счет отклонен.")
                    await asyncio.sleep(1)
                emb = disnake.Embed(
                    description=f"Спасибо за покупку товара!\n\nСервер получил премиум!",
                    color=0x39FB21
                ) \
                    .set_footer(text="Оплата проведена успешно ✔️")
                await ctx.author.send(embed=emb)
                p2p.reject(bill_id=new_bill.bill_id)
                await bot.get_channel(982029966743044107).send(
                    f"Новая покупка!\ntype: premium\nserver id: {ctx.guild.id}\nuser: {ctx.author.id}")
                settings.update_one({"_id": ctx.guild.id},
                                    {"$set": {"premium": 1, "premium_time": dt.utcnow() + timedelta(seconds=2592000)}})
                guilds[ctx.guild.id]["premium"] = 1

            await check()
        elif type == 2:
            bill_id = str(ctx.guild.id) + str(random.randint(0, 999999999999))
            new_bill = p2p.bill(bill_id=bill_id, amount=500, lifetime=3, comment="Покупка премиума")
            authemb = disnake.Embed(
                title="Подтверждение платежа - PREMIUM `👑`",
                color=0xD3F250,
                description=f"✓ Стоимость услуги: **500 ₽**\n\n❗Для подтверждения платежа, перейдите по ссылке: \"[ссылка]({new_bill.pay_url})\"",
            ) \
                .set_footer(text="Saints Economy - Discord bot")
            await ctx.author.send(embed=authemb)
            emb = disnake.Embed(title="Платёжная система - PREMIUM `👑`")
            emb.description = "`Для совершения платежа, перейдите в личные сообщения.`"
            emb.set_footer(text="Saints Economy - Discord bot")
            await ctx.send(embed=emb)

            async def check():
                global amount
                while True:
                    if p2p.check(bill_id=new_bill.bill_id).status == "PAID":
                        await ctx.author.send("Обработка...")
                        break
                    elif p2p.check(bill_id=new_bill.bill_id).status == "EXPIRED":
                        return await ctx.author.send("Время истекло. счёт закрыт")
                    elif p2p.check(bill_id=new_bill.bill_id).status == "REJECTED":
                        return await ctx.author.send("Счет отклонен.")
                    await asyncio.sleep(1)
                emb = disnake.Embed(
                    title="Успешно ✓",
                    description=f"Спасибо за покупку товара!\n\На сервер установлен премиум!",
                    color=0x39FB21
                ) \
                    .set_footer(text="Оплата проведена успешно ✔️")
                await ctx.author.send(embed=emb)
                p2p.reject(bill_id=new_bill.bill_id)
                if type == 1:
                    amount = "500"
                elif type == 2:
                    amount = "1500"
                await bot.get_guild(927777195080966185).get_channel(1008086846028386364).send(amount)
                await bot.get_channel(1008086846028386364).send(
                    f"Новая покупка!\ntype: premium\nserver id: {ctx.guild.id}\nuser: {ctx.author.id}")
                settings.update_one({"_id": ctx.guild.id}, {"$set": {"premium": 2, "premium_time": -1}})
                guilds[ctx.guild.id]["premium"] = 2

            await check()
        else:
            emb = disnake.Embed(title="PREMIUM `👑` - ошибка")
            emb.description = "Правильное использование команды: `!claim-premium < type(1, 2) >`\n\n1 - на месяц,\n2 - навсегда"
            return await ctx.send(embed=emb)

    @bot.command(aliases=['аддпремиум'])
    async def addpremium(ctx, type: int = None):
        global devs
        if ctx.author.id in devs:
            if type == None:
                await ctx.send(embed=disnake.Embed(color=disnake.Color.red(), title='Ошибка!',
                                                   description='Вы не указали длительность премиума!'))
            else:
                if type == 1:
                    time = '30 дней'
                    settings.update_one({"_id": ctx.guild.id}, {
                        "$set": {"premium": 1, "premium_time": dt.utcnow() + timedelta(seconds=2592000)}})
                    guilds[ctx.guild.id]["premium"] = 1
                elif type == 2:
                    time = "Неограниченно"
                    settings.update_one({"_id": ctx.guild.id}, {"$set": {"premium": 2, "premium_time": -1}})
                    guilds[ctx.guild.id]["premium"] = 2
                await ctx.send(embed=disnake.Embed(color=0xFFD700, title='Успешно!',
                                                   description=f'`Премиум успешно выдан!`\n`Выдал:` **{ctx.author.display_name}**\n`Название сервера:` **{ctx.guild.name}**\n`ID Сервера:` **{ctx.guild.id}**\n`Premium time:` **{time}**'))
        else:
            await ctx.send(embed=disnake.Embed(color=disnake.Color.red(), title='Ошибка!',
                                               description='Данная команда доступна только для разработчиков'))


    #Moderation

    @bot.command(aliases=['бан'])
    async def ban(inter, member: disnake.Member, reason: str = None):
        if member == None or member == inter.author:
            await inter.channel.send("Вы не можете забанить себя.")
            return
        if reason == None:
            reason = "По решению модерации."
        message = f"Вы были забанены на сервере ```{inter.guild.name}``` по причине ```{reason}```"
        await member.send(message)
        await inter.guild.ban(member, reason=reason)
        await inter.edit_original_response(content=f"{member} был забанен!")
    
    @bot.command(aliases=['кик'])
    async def kick(inter, member: disnake.Member, reason: str = None):
        if member == None or member == inter.author:
            await inter.channel.send("Вы не можете выгнать самого себя.")
            return
        if reason == None:
            reason = "По решению модерации."
        message = f"Вы были выгнаны с сервера ```{inter.guild.name}``` по причине ```{reason}```"
        await member.send(message)
        await inter.guild.kick(member, reason=reason)
        await inter.edit_original_response(content=f"{member} был выгнан!")
    

    @bot.command(aliases=['мут'])
    async def mute(ctx, member: disnake.Member, timeout: str, *, reason = 'Не указана'):
        timeout_config = {
                's' : 1,
                'm' : 60,
                'h' : 60 ** 2,
                'd' : 60 ** 2 * 24,
                'w' : 60 ** 2 * 24 * 7,
                'mon' : 60 ** 2 * 24 * 31,
                'y' : 60 ** 2 * 24 * 31 * 12,
                'с' : 1,
                'м' : 60,
                'ч' : 60 ** 2,
                'д' : 60 ** 2 * 24,
                'н' : 60 ** 2 * 24 * 7,
                'мес' : 60 ** 2 * 24 * 31,
                'г' : 60 ** 2 * 24 * 31 * 12
            }
        def find_time_items():
            for k, v in timeout_config.items():
                if k == list(timeout)[-1]:
                    return v
                else:
                    pass

        def time():
            time = list(timeout)
            time.remove(list(timeout)[-1])
            t = ''.join(time)
            return int(t)
        if ctx.author.guild_permissions.administrator:
            try:
                await member.timeout(duration=time() * find_time_items(), reason=reason)
            except (Exception,):
                return await ctx.edit_original_response(content='При выдаче мута возникла непредвиденная ошибка.')
            await ctx.edit_original_response(content=f"{member} был замучен!")


    bot.run(token)

a()
