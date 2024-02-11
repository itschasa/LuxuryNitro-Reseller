import discord
from discord import app_commands
from discord.ext import tasks
import time
import httpx
import asyncio
import base64
import re

import utils
from utils import config
import luxurynitro

__version__ = 'v1.2.1'

last_update_ping = int(time.time())

async def latest_version_check():
    try:
        async with httpx.AsyncClient() as client:
            github_data = await client.get("https://api.github.com/repos/ItsChasa/LuxuryNitro-Reseller/releases/latest")
        
        github_data_json = github_data.json()
        app_latest_ver = github_data_json['tag_name']
        app_latest_ver_link = github_data_json['html_url']
    except:
        app_latest_ver = __version__
        app_latest_ver_link = "null"

    return app_latest_ver_link, app_latest_ver

global_credits = 0
global_orders: dict[str, luxurynitro.Order] = {}

f = open('data/queue.txt', 'r')
queue_message_id = f.read()
f.close()
if queue_message_id == '': queue_message_id = None

f = open('data/vps.txt', 'r')
vps_message_id = f.read()
f.close()
if vps_message_id == '': vps_message_id = None

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

logs_channel = None

error_color = 0xe64e4e
error_symbol = '`🔴`'
success_color = 0x4dd156
success_symbol = '`🟢`'

api: luxurynitro.Client = None
api_user: luxurynitro.User = None

class log:
    @staticmethod
    async def error(message):
        timenow = int(time.time())
        return await logs_channel.send(f"<t:{timenow}:d> <t:{timenow}:t> `🔴` {message}", suppress_embeds=True)
    @staticmethod
    async def success(message):
        timenow = int(time.time())
        return await logs_channel.send(f"<t:{timenow}:d> <t:{timenow}:t> `🟢` {message}", suppress_embeds=True)
    @staticmethod
    async def warn(message):
        timenow = int(time.time())
        return await logs_channel.send(f"<t:{timenow}:d> <t:{timenow}:t> `🟡` {message}", suppress_embeds=True)
    @staticmethod
    async def info(message):
        timenow = int(time.time())
        return await logs_channel.send(f"<t:{timenow}:d> <t:{timenow}:t> `🔵` {message}", suppress_embeds=True)

async def resp_success(interaction: discord.Interaction, msg:str, hidden=True, followup=False):
    if followup:
        method = interaction.followup.send
    else:
        method = interaction.response.send_message
    await method(
        embed=discord.Embed(
            description=f'{success_symbol} {msg}',
            color=success_color
        ),
        ephemeral=hidden
    )

async def resp_error(interaction: discord.Interaction, msg:str, hidden=True, followup=False):
    if followup:
        method = interaction.followup.send
    else:
        method = interaction.response.send_message
    await method(
        embed=discord.Embed(
            description=f'{error_symbol} {msg}',
            color=error_color
        ),
        ephemeral=hidden
    )


@tree.command(description=utils.lang.cmd_credits_desc, name=utils.lang.cmd_credits)
@app_commands.describe(hidden=utils.lang.cmd_credits_arg_hidden, user=utils.lang.cmd_credits_arg_user)
async def credits(interaction: discord.Interaction, hidden: bool = False, user: discord.Member = None):
    credit_count = utils.get_credits(interaction.user.id if user is None else user.id)
    
    if user is not None and interaction.user.id not in config.discord_admins:
        await resp_error(interaction, utils.lang.no_admin)
    else:
        if user:
            await resp_success(interaction, utils.lang.process(utils.lang.cmd_credits_success_user, {'user': user.mention, 'total': credit_count}), hidden)
        else:
            await resp_success(interaction, utils.lang.process(utils.lang.cmd_credits_success, {'total': credit_count}), hidden)

purchase_lock = asyncio.Lock()
@tree.command(description=utils.lang.cmd_purchase_desc, name=utils.lang.cmd_purchase)
@app_commands.describe(amount=utils.lang.cmd_purchase_arg_amount, token=utils.lang.cmd_purchase_arg_token, anonymous=utils.lang.cmd_purchase_arg_anonymous)
async def purchase(interaction: discord.Interaction, amount: int, token: str, anonymous: bool = False):
    global global_credits
    await interaction.response.defer(ephemeral=True)
    await purchase_lock.acquire()
    credit_count = utils.get_credits(interaction.user.id)
    if credit_count < amount:
        await resp_error(interaction, utils.lang.cmd_purchase_no_credits, followup=True)
    else:
        try:
            order = await api.create_order(amount, token, anonymous=anonymous, reason=f"RS: {interaction.user.id}")
        
        except luxurynitro.errors.APIError as exc:
            if "credits" in exc.message.lower():
                await resp_error(interaction, utils.lang.cmd_purchase_contact_owner, followup=True)
                
                await log.error(utils.lang.process(utils.lang.cmd_purchase_contact_owner_log, {
                    'user': interaction.user.mention,
                    'amount': amount,
                    'global_credits': global_credits
                }) + ''.join(f' <@{x}>' for x in config.discord_admins))
            
            else:
                await resp_error(interaction, utils.lang.process(utils.lang.general_error, {'error': exc.message}), followup=True)
        
        except luxurynitro.errors.RetryTimeout:
            await resp_error(interaction, utils.lang.retry_later_error, followup=True)
        
        else:
            db = utils.database.Connection()
            db.insert("credits", [interaction.user.id, f"-{amount}", f'Order #{order.id}', credit_count-amount])
            db.insert("orders", [order.id, interaction.user.id, str(base64.b64decode(bytes(token.split('.')[0] + '==', encoding='utf-8')), encoding='utf-8'), 1 if anonymous else 0, 0])
            db.close()

            await resp_success(interaction, utils.lang.process(utils.lang.cmd_purchase_success, {'order': order.id}), followup=True)
            
            global_credits -= amount
            
            await log.success(utils.lang.process(utils.lang.cmd_purchase_success_log, {
                'user': interaction.user.mention,
                'amount': amount,
                'order': order.id,
                'credit_before': credit_count,
                'credit_after': credit_count-amount,
                'global_credits': global_credits
            }))
    
    purchase_lock.release()

@tree.command(description=utils.lang.cmd_cancel_desc, name=utils.lang.cmd_cancel)
@app_commands.describe(order_id=utils.lang.cmd_cancel_arg_order_id)
async def cancel(interaction: discord.Interaction, order_id: int):
    global global_credits
    order_id = utils.clean_id(order_id)
    db = utils.database.Connection()
    res = db.query('orders', ['completed', 'discord_id'], {'api_id': order_id})
    if res is None:
        await resp_error(interaction, utils.lang.cmd_cancel_order_invalid)
    elif res[1] == 1:
        await resp_error(interaction, utils.lang.cmd_cancel_order_completed)
    elif res[2] != str(interaction.user.id) and interaction.user.id not in config.discord_admins:
        await resp_error(interaction, utils.lang.cmd_cancel_no_permission)
    else:
        await interaction.response.defer(ephemeral=True)
        try:
            refunded = await api.delete_order(order_id=order_id)
        
        except luxurynitro.errors.APIError as exc:
            await resp_error(interaction, utils.lang.process(utils.lang.general_error, {'error': exc.message}), followup=True)
            if "complete" in exc.message.lower():
                db.edit('orders', {'completed': 1}, {'api_id': order_id})
                
        except luxurynitro.errors.RetryTimeout:
            await resp_error(interaction, utils.lang.retry_later_error, followup=True)
        
        else:
            balance = utils.get_credits(res[2])
            db.insert('credits', [res[2], refunded, f'Order {order_id} cancelled.', balance+refunded])
            db.edit('orders', {'completed': 1}, {'api_id': order_id})
            
            await resp_success(interaction, utils.lang.process(utils.lang.cmd_cancel_success, {'order': order_id, 'amount': refunded}), followup=True)
            
            global_credits += refunded
            
            await log.success(utils.lang.process(utils.lang.cmd_cancel_success_log, {'user': interaction.user.mention, 'order': order_id, 'global_credits': global_credits}))
    
    db.close()

claim_lock = asyncio.Lock()
@tree.command(description=utils.lang.cmd_claim_desc, name=utils.lang.cmd_claim)
@app_commands.describe(order_id=utils.lang.cmd_claim_arg_order_id)
async def claim(interaction: discord.Interaction, order_id: str):
    await interaction.response.defer(ephemeral=True)
    await claim_lock.acquire()
    success, reason, balance, logstr = await utils.buy_api.confirm_order(order_id, interaction.user.id)
    claim_lock.release()
    if success:
        await resp_success(interaction, utils.lang.process(utils.lang.cmd_claim_success, {'total': balance}), followup=True)
        await log.success(logstr)
    else:
        reason_map = {
            'max_retries': utils.lang.retry_later_error,
            'unauthorized': utils.lang.unauthorized_error,
            'claimed': utils.lang.cmd_claim_order_already_claimed,
            'product_id': utils.lang.cmd_claim_invalid_product_id,
            'start_time': utils.lang.cmd_claim_order_before_time,
            'unknown': utils.lang.cmd_claim_no_order_exists,
            'payment': utils.lang.cmd_claim_order_incomplete
        }
        await resp_error(interaction, reason_map[reason], followup=True)

@tree.command(description=utils.lang.cmd_award_desc, name=utils.lang.cmd_award)
@app_commands.describe(user=utils.lang.cmd_award_arg_user, amount=utils.lang.cmd_award_arg_amount, reason=utils.lang.cmd_award_arg_reason)
async def award(interaction: discord.Interaction, user: discord.Member, amount: int, reason: str):
    if interaction.user.id not in config.discord_admins:
        await resp_error(interaction, utils.lang.no_admin)
    else:
        credit_count = utils.get_credits(user.id)
        new_balance = credit_count+amount
        db = utils.database.Connection()
        db.insert('credits', [user.id, amount, reason, new_balance])
        db.close()
        await resp_success(interaction, utils.lang.process(utils.lang.cmd_award_success, {'user': user.mention, 'credits': new_balance}))

async def get_orders_description(user_id, all_orders, page=1):
    db = utils.database.Connection()
    results = db.query('orders', ['api_id', 'user', 'discord_id', 'anonymous', 'completed'], {} if all_orders else {'user': user_id}, False)[::-1]
    refunded_orders = []
    invalid_orders = []
    user_cancelled_orders = []
    admin_cancelled_orders = []

    try:
        credits_history = await api.get_credits()
    except Exception:
        return '', f'0/{len(results)}'
    else:
        credits_history = credits_history.history

    for credit_change in credits_history:
        # If a credit change was because of a basic refund, ignore it.
        if "basics" in credit_change.reason.lower():
            continue
        
        order_id: list[str] = re.findall(r"#[0-9]{4,}", credit_change.reason) # Order IDs are currently 4 digits long, however they could be longer in the future.
        if len(order_id) == 1:
            raw_order_id = order_id[0].replace("#", '')
            
            if credit_change.change > 0:

                if "token was invalid" in credit_change.reason.lower():
                    invalid_orders.append(raw_order_id)
                
                elif "cancelled by user" in credit_change.reason.lower():
                    user_cancelled_orders.append(raw_order_id)

                else:
                    # Refunded for another reason other than Token Invalid and Cancelled by User.
                    refunded_orders.append(raw_order_id)
            
            elif credit_change.change == 0:
                # In rare cases, an order can be cancelled, without refund, by an admin (most commonly after chargebacks).
                admin_cancelled_orders.append(raw_order_id)
                
    try:
        data = utils.split_list(results)[page-1]
        description = ''
        for order in data:
            if order[1] not in description:
                
                if order[1] in refunded_orders:
                    # "Refunded" does not mean refunded to the user, but to the reseller, so "Cancelled" should be a more appropriate response.
                    status = utils.lang.cmd_orders_refunded
                
                elif order[1] in invalid_orders:
                    status = utils.lang.cmd_orders_token_invalidated

                elif order[1] in user_cancelled_orders:
                    status = utils.lang.cmd_orders_user_cancelled
                
                elif order[1] in admin_cancelled_orders:
                    status = utils.lang.cmd_orders_admin_cancelled

                elif global_orders[order[1]].status.completed:
                    status = utils.lang.cmd_orders_completed
                
                else:
                    status = utils.lang.cmd_orders_in_queue

                description += f"`#{order[1]}` | " + utils.lang.process(utils.lang.cmd_orders_success_data, {
                    'received': global_orders[order[1]].received,
                    'quantity': global_orders[order[1]].quantity,
                    'user': f'<@{order[2]}>',
                    'anonymous': utils.lang.bool_true if order[4] == 1 else utils.lang.bool_false,
                    'status': '**' + status + '**'
                }) + "\n"

    except Exception:
        db.close()
        return '', f'0/{len(results)}'
    else:
        db.close()
        return description, f'{len(data)}/{len(results)}'

@tree.command(description=utils.lang.cmd_orders_desc, name=utils.lang.cmd_orders)
@app_commands.describe(page=utils.lang.cmd_orders_arg_page , all_orders=utils.lang.cmd_orders_arg_all_orders)
async def orders(interaction: discord.Interaction, page: int = 1, all_orders: bool=False):
    if all_orders and interaction.user.id not in config.discord_admins:
        await resp_error(interaction, utils.lang.no_admin)
    else:
        desc, total = await get_orders_description(interaction.user.id, all_orders, page)
        await resp_success(interaction, utils.lang.process(utils.lang.cmd_orders_success, {'total': total}) + '\n\n' + desc)
        
@tree.command(description=utils.lang.cmd_buy_desc, name=utils.lang.cmd_buy)
@app_commands.describe()
async def buy(interaction: discord.Interaction):
    await resp_success(interaction, f"[{config.purchase_link}]({config.purchase_link})")

@tree.command(description=utils.lang.cmd_token_desc, name=utils.lang.cmd_token)
@app_commands.describe()
async def token(interaction: discord.Interaction):
    await resp_success(interaction, f"[{utils.lang.cmd_token_success}]({utils.config.qr_code_link})")


@client.event
async def on_ready():
    global logs_channel
    logs_channel = client.get_channel(config.logs_channel)
    
    await tree.sync()
    await queueEmbedLoop.start()
    await vpsEmbedLoop.start()

@tasks.loop(seconds=30)
async def vpsEmbedLoop():
    global vps_message_id, last_update_ping
    await client.wait_until_ready()
    try:
        vps_stats = await api.get_vps_stats()
    except luxurynitro.errors.APIError as exc:
        await log.warn(f"{utils.lang.embed_fetch_error} {exc.message}")
    except luxurynitro.errors.RetryTimeout as exc:
        await log.warn(f"{utils.lang.embed_fetch_error} {exc.message}" + "\n- ".join(f"`{e}`" for e in exc.errors))
    else:
        vps_stats_sorted = sorted(vps_stats, key=lambda x: x.instance_id)

        extensions = '\n'.join(
            [
                f'{config.vps_webhook.emojis["working"]} ``Instance {stats.instance_id}`` - ``{stats.servers} Guilds / {stats.alts} alts``'
                for stats in
                vps_stats_sorted])

        embed = discord.Embed(
            title = f"{utils.lang.process(utils.lang.vps_title)}",
            description = "If there are instances offline, it might takes longer to snipe.\n\n>>> " + extensions,
            color = config.vps_webhook.color
        ).set_footer(
            text=utils.lang.vps_footer_text,
            icon_url=config.vps_webhook.footer_icon
        )


        if vps_message_id:
            try:
                async with httpx.AsyncClient() as rclient:
                    res = await rclient.patch(config.vps_webhook.url + f'/messages/{vps_message_id}',
                                              json={'embeds': [embed.to_dict()]})
                    if res.status_code != 200:
                        vps_message_id = None
            except:
                pass

        if not vps_message_id:
            try:
                async with httpx.AsyncClient() as rclient:
                    res = await rclient.post(config.vps_webhook.url + '?wait=true',
                                             json={'embeds': [embed.to_dict()]})
            except:
                pass
            else:
                vps_message_id = str(res.json()['id'])
                f = open('data/vps.txt', 'w')
                f.write(vps_message_id)
                f.close()
                
@tasks.loop(seconds = 30)
async def queueEmbedLoop():
    global queue_message_id, global_credits, global_orders, last_update_ping
    await client.wait_until_ready()
    try:
        user = await api.get_user()
        queue = await api.get_queue()
    except luxurynitro.errors.APIError as exc:
        await log.warn(f"{utils.lang.embed_fetch_error} {exc.message}")
    except luxurynitro.errors.RetryTimeout as exc:
        await log.warn(f"{utils.lang.embed_fetch_error} {exc.message}" + "\n- ".join(f"`{e}`" for e in exc.errors))
    else:
        current_time = int(time.time())
        download_url, version_name = await latest_version_check()
        if version_name != __version__ and last_update_ping + 86400 < current_time:
            await log.warn(utils.lang.process(utils.lang.new_update_available_log, {
                "version": version_name,
                "current_version": __version__,
                "download_url": download_url
            }) + ''.join(f' <@{x}>' for x in config.discord_admins))
            last_update_ping = current_time
        
        db = utils.database.Connection()
        global_credits = user.credits
        orders = user.orders
        largest_gift_count_length = 0

        queue_ids = []
        for order in queue.queue:
            queue_ids.append(order.id)

        order_to_queue: dict[str, int] = {}

        for order in orders:
            if not order.status.completed:
                if len(str(order.quantity) + str(order.received)) > largest_gift_count_length:
                    largest_gift_count_length = len(str(order.quantity) + str(order.received))
                
                if order.status.in_queue:  
                    order_to_queue[order.id] = int(order.status.status_text.split('/')[0].replace('(', ''))
                else: # has to be on status=1 (claiming)
                    order_to_queue[order.id] = 0
            
            global_orders[order.id] = order
        
        orders = sorted(orders, key=lambda order: order_to_queue.get(order.id, 9999))

        description = ""
        queue_total = 0
        
        for order in orders:
            if not order.status.completed:
                result = db.query("orders", ["anonymous", "discord_id"], {"api_id": order.id})
                if result is not None:
                    if result[1] == 1:
                        display_name = utils.lang.anonymous_upper
                    else:
                        display_name = f"<@{result[2]}>"
                else:
                    display_name = utils.lang.anonymous_upper
                description += f"\n{config.queue_webhook.emojis['claiming'] if order.status.claiming else config.queue_webhook.emojis['in_queue']}    ` {order.received}/{order.quantity}{''.join(' ' for _ in range(largest_gift_count_length - len(str(order.quantity) + str(order.received))))} {utils.lang.queue_gifts} ` {display_name}{' `'+ utils.convertHMS(order.eta.next_gift) + '`' if config.queue_webhook.show_eta else ''}"
                queue_total += order.quantity - order.received
            else:
                db.edit('orders', {'completed': 1}, {'api_id': order.id})

        embed = discord.Embed(
            title = f"{config.queue_webhook.title_emoji}  {utils.lang.process(utils.lang.queue_title, {'name':api_user.display_name})}",
            description = "🎁    `" + utils.lang.process(utils.lang.queue_length, {'length': queue_total}) + "`\n" + description,
            color = config.queue_webhook.color
        ).set_footer(
            text = utils.lang.queue_footer_text,
            icon_url = config.queue_webhook.footer_icon
        )

        if queue_message_id:
            try:
                async with httpx.AsyncClient() as rclient:
                    res = await rclient.patch(config.queue_webhook.url+f'/messages/{queue_message_id}', json={'embeds': [embed.to_dict()]})
                    if res.status_code != 200:
                        queue_message_id = None
            except:
                pass
        
        if not queue_message_id:
            try:
                async with httpx.AsyncClient() as rclient:
                    res = await rclient.post(config.queue_webhook.url + '?wait=true', json={'embeds': [embed.to_dict()]})
            except:
                pass
            else:
                queue_message_id = str(res.json()['id'])
                f = open('data/queue.txt', 'w')
                f.write(queue_message_id)
                f.close()
        
        db.close()

async def startup():
    global api, api_user, global_credits
    print("Coded with <3 by chasa | https://github.com/itschasa/LuxuryNitro-Reseller")
    print("If you have any issues, create an issue using the link above. :D")
    
    download_url, version_name = await latest_version_check()
    if version_name != __version__:
        print("\n-------------------")
        print("!!! You are using an outdated version! Update with the link below!")
        print(download_url)
        print(f"You're using {__version__}, latest version is {version_name}")
        print("-------------------")
        exit()
    
    print("\nConnecting to LuxuryNitro API...")
    api = luxurynitro.Client(config.api_key)
    try: api_user = await api.get_user()
    except luxurynitro.errors.APIError as exc:
        print(f"Error connecting to LuxuryNitro API ({api._base_url}): {exc.message}")
        if exc.response.status_code == 401:
            print("It seems like your LuxuryNitro API key is invalid. You can get a new one at https://luxurynitro.com/settings")
            print("Make sure to paste the full key, including the 'api_' part.")
        exit()
    global_credits = api_user.credits
    
    print("Setting hit webhook...")
    await api.set_hit_webhook(config.hit_webhook.url, config.hit_webhook.message, config.hit_webhook.emojis)

    print("Logging into Discord...")
    discord.utils.setup_logging(root=False)
    await client.start(config.discord_token, reconnect=True)

asyncio.run(startup())
