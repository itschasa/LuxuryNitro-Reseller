from . import http_client
from . import classes
from . import errors

import re

class Client():
    def __init__(self, api_key: str, base_url='https://dash.luxurynitro.com/api/v1', *args) -> None:
        self.api_key = api_key
        self._base_url = base_url
        
        self.client = http_client.HTTP(
            api_key=api_key,
            base_url=base_url,
            *args
        )

        self._public_user = None
        
    async def get_user(self) -> classes.User:
        "Fetches the user's data. Returns `User`."
        res = await self.client.get('/users/@me')
        resjson = res.json()
        
        self._public_user = classes.PublicUser(
            display_name = resjson['display_name'],
            id = resjson['id']
        )
        
        return classes.User(
            username = resjson['username'],
            display_name = resjson['display_name'],
            email = resjson['email'],
            id = resjson['id'],
            credits = resjson['credits'],
            orders = [
                classes.Order(
                    eta = classes.ETA(
                        next_gift = order['eta'].get('next'),
                        completed = order['eta'].get('completed'),
                    ),
                    claimed = [
                        classes.Claim(
                            instance = claim['instance'],
                            snipe_time = claim.get('snipe_time'),
                            timestamp = claim['time'],
                            nitro_type = classes.Nitro(
                                _type = claim['type']
                            ),
                            user = self._public_user,
                            order_id = order['id']
                        ) for claim in order['claimed']
                    ],
                    id = order['id'],
                    quantity = order['quantity'],
                    received = order['received'],
                    status = classes.Status(
                        _type = order['status'],
                        status_text = order['status_text']
                    ),
                    timestamp = order['time'],
                    user = self._public_user
                ) for order in resjson['orders']
            ],
            stats = classes.Stats(
                alts = resjson['stats']['alts'],
                boost_chance = resjson['stats']['boost_percent'],
                servers = resjson['stats']['servers'],
                support_time = resjson['stats']['support_time'],
                total_claims = resjson['stats']['total_claims'],
            ),
            tickets = [
                classes.Ticket(
                    timestamp = ticket['creation_time'],
                    id = ticket['id'],
                    opened = ticket['open'],
                    seen = ticket['seen']
                ) for ticket in resjson['tickets']
            ]
        )
    
    async def get_vps_stats(self) -> list[classes.VPS]:
        "Fetches the vps stats. Returns list of `VPS`."

        res = await self.client.get('/vps-stats')
        resjson = res.json()

        data = sorted(resjson, key = lambda x: x['instance_id'])

        return [
            classes.VPS(
                alts = instance['alts'],
                instance_id = instance["instance_id"],
                last_seen = instance["last_seen"],
                servers = instance["servers"]
            ) for instance in data

        ]

    async def get_queue(self) -> classes.Queue:
        "Fetches the global queue. Returns `Queue`."
        res = await self.client.get('/queue')
        resjson = res.json()

        return classes.Queue(
            eta = classes.ETA(
                next_gift = resjson['eta_per_gift'],
                completed = resjson['queue_cleared']
            ),
            length = resjson['queue_quantity'],
            queue = [
                classes.Order(
                    eta = classes.ETA(
                        next_gift = order['eta'].get('next'),
                        completed = order['eta'].get('completed'),
                    ),
                    claimed = [],
                    id = order['id'],
                    quantity = order['quantity'],
                    received = order['received'],
                    status = classes.Status(
                        _type = order['status']
                    ),
                    user = classes.PublicUser(
                        display_name = order['user']['display_name'],
                        id = order['user']['id'],
                    )
                ) for order in resjson['queue']
            ],
            recent = [
                classes.Claim(
                    timestamp = claim['time'],
                    snipe_time = claim.get('snipe_time'),
                    nitro_type = classes.Nitro(
                        _type = claim['type']
                    ),
                    user = classes.PublicUser(
                        display_name = claim['user']['display_name'],
                        id = claim['user']['id']
                    ),
                    order_id = claim['order']
                ) for claim in resjson['recent']
            ]
        )
    
    async def get_credits(self) -> classes.Credits:
        "Fetches the user's credits, and credit history. Returns `Credits`."
        res = await self.client.get('/users/@me/credits')
        resjson = res.json()

        return classes.Credits(
            total = resjson['total'],
            history = [
                classes.CreditChange(
                    change = int(change['change']),
                    closing_balance = change['closing_balance'],
                    id = change['id'],
                    reason = change['reason'],
                    timestamp = change['time']
                ) for change in resjson['history']
            ]
        )
    
    async def get_tickets(self) -> list[classes.Ticket]:
        "Fetches all of the user's tickets. Returns a list of `Ticket`."
        res = await self.client.get('/users/@me/tickets')
        resjson = res.json()

        return [
            classes.Ticket(
                timestamp = ticket['creation_time'],
                id = ticket['id'],
                opened = ticket['open'],
                seen = ticket['seen']
            ) for ticket in resjson
        ]
    
    async def get_orders(self) -> list[classes.Order]:
        "Fetches all of the user's orders. Returns a list of `Order`."
        res = await self.client.get('/users/@me/orders')
        resjson = res.json()

        return [
            classes.Order(
                eta = classes.ETA(
                    next_gift = order['eta'].get('next'),
                    completed = order['eta'].get('completed'),
                ),
                claimed = [
                    classes.Claim(
                        instance = claim['instance'],
                        timestamp = claim['time'],
                        nitro_type = classes.Nitro(
                            _type = claim['type']
                        ),
                        user = self._public_user,
                        order_id = order['id']
                    ) for claim in order['claimed']
                ],
                id = order['id'],
                quantity = order['quantity'],
                received = order['received'],
                status = classes.Status(
                    _type = order['status'],
                    status_text = order['status_text']
                ),
                timestamp = order['time'],
                user = self._public_user
            ) for order in resjson
        ]
    
    async def create_order(self, quantity:int, token:str, anonymous:bool=False, reason:str='') -> classes.Order:
        """Create a new order, and return the `Order`.
        
        ### Arguments:
        - `quantity`: int, Amount of nitros to be sniped.
        - `token`: str, Discord User Token to claim the nitro on. Needs to be phone verified.
        - `anonymous`: bool, If true, the user will not be pinged for webhook notifications.
        - `reason`: str, Shown in credit history, used for future reference.
        """
        res = await self.client.post('/users/@me/orders',
            json = {
                'quantity': quantity,
                'token': token,
                'anonymous': anonymous,
                'reason': reason
            }
        )
        order_id = res.json()['order']

        for order in await self.get_orders():
            if order.id == order_id:
                return order
        
        return None

    async def delete_order(self, order:classes.Order=None, order_id:str=None) -> int:
        """Delete the order provided, and return the amount refunded.
        
        Either `order` or `order_id` has to be given. If both are given, `order` takes priority.
        
        If neither are provided, `errors.ValidationError` will be raised."""

        if order is None and order_id is None:
            raise errors.ValidationError("one argument has to be not None")
        
        res = await self.client.delete(f'/users/@me/orders/{order.id if order is not None else order_id}')
        
        return int(res.json()['refund_amount'])

    async def set_hit_webhook(self, webhook:str, message:str, emoji_map:dict={}) -> None:
        """Set the Discord Webhook that should be fired when a nitro is sniped.

        `errors.ValidationError` will be raised if any arguments are invalid.

        ### Arguments:
        - `webhook`: string, Discord Webhook URL.
        - `message`: string, Formatted string, using [] for variables.
          - Available Variables: [emoji] [nitro] [user] [order] [claimed] [quantity] [time]
          - [emoji] is replaced with the appropriate emoji from `emoji_map`
        - `emoji_map`: dict, Keys need to contain all types (boost, basic, classic), and value should be the appropiate emoji for it.
          - Example: `{"boost": "<:nitro_boost:1093986192346849310>", "basic": "<:nitro_basic:1093984571839758417>", "classic": "<:nitro_classic:1129332873728634970>"}`"""
        
        matches = re.findall("^.*(discord|discordapp)\.com\/api\/webhooks\/([0-9]+)\/([a-zA-Z0-9_-]+)$", webhook, re.RegexFlag.IGNORECASE)
        if len(matches) != 1:
            raise errors.ValidationError("webhook invalid (only include one webhook url)")
        
        webhook_id, webhook_key = matches[0][1], matches[0][2]
        
        if '[emoji]' in message and not emoji_map:
            raise errors.ValidationError("emoji variable used, but no emoji_map provided")
        
        if not emoji_map:
            available_keys = ['boost', 'classic', 'basic']
            emoji_re = re.compile('<(a|):[A-Za-z_-]+:[0-9]+>')
            for key, value in emoji_map.items():
                if key not in available_keys:
                    raise errors.ValidationError("invalid emoji_map (invalid key, or duplicate key)")
                
                if not emoji_re.findall(value):
                    raise errors.ValidationError(f"invalid emoji in {value}")
                
                available_keys.remove(key)
            
            if available_keys:
                raise errors.ValidationError(f"missing emojis: {', '.join(x for x in available_keys)}")
        

        await self.client.post('/users/@me/webhook',
            json = {
                'webhook': {
                    'id': webhook_id,
                    'key': webhook_key
                },
                'message': message,
                'emojis': emoji_map
            }
        )

