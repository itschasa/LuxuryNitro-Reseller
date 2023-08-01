import httpx
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Union

import utils
from utils import config

request_method_map = {
    "sellix": "GET",
    "sellapp": "GET",
    'sellpass': 'GET'
}
request_url_map = {
    "sellix": "https://dev.sellix.io/v1/orders/{}",
    "sellapp": "https://sell.app/api/v1/invoices/{}",
    'sellpass': 'https://dev.sellpass.io/self/' + str(config.claiming.merchant) + '/invoices/{}'
}
request_auth_map = {
    "sellix": "Bearer {}",
    "sellapp": "Bearer {}",
    "sellpass": "Bearer {}"
}
request_store_map = {
    "sellix": "X-Sellix-Merchant",
    "sellapp": "X-Store"
}

@dataclass
class order_data:
    product_id: str
    order_time: int
    quantity: int
    paid: bool


def get_order(order_id, retry=0) -> tuple[bool, Union[str, order_data]]:
    headers = {
        'Authorization': request_auth_map[config.claiming.mode].format(config.claiming.api_key),
        "Accept": "application/json"
    }
    if config.claiming.merchant and config.claiming.mode != 'sellpass':
        headers[request_store_map[config.claiming.mode]] = config.claiming.merchant
    
    try:
        res = httpx.request(
            method=request_method_map[config.claiming.mode],
            url=request_url_map[config.claiming.mode].format(order_id),
            headers=headers,
            json=None
        )
    except:
        if retry > 2: return False, 'max_retries'
        time.sleep(1)
        return get_order(order_id, retry+1)
    else:
        if res.status_code == 429:
            if retry > 2: return False, 'max_retries'
            time.sleep(2.5)
            return get_order(order_id, retry+1)
        
        elif res.status_code in (401, 403):
            return False, 'unauthorized'
        
        elif res.status_code == 200:
            resjson = res.json()

            if config.claiming.mode == 'sellix':
                return True, order_data(
                    product_id=str(resjson['data']['order']['product_id']),
                    order_time=resjson['data']['order']['created_at'],
                    quantity=resjson['data']['order']['quantity'],
                    paid=resjson['data']['order']['status'] == 'COMPLETED'
                )
            
            elif config.claiming.mode == 'sellapp':                
                quantity = 0
                for product in resjson['data']['products']:
                    if str(product['id']) == config.claiming.product:
                        for variant in product['variants']:
                            quantity += variant['quantity']
                
                return True, order_data(
                    product_id=str(config.claiming.product) if quantity > 0 else '0',
                    order_time=int(
                        datetime.strptime(resjson['data']['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
                            .replace(tzinfo=timezone.utc)
                            .timestamp()
                    ),
                    quantity=quantity,
                    paid=resjson['data']['status']['status']['status'] == 'COMPLETED'
                )
            
            elif config.claiming.mode == 'sellpass':
                quantity = 0
                for product in resjson['data']['partInvoices']:
                    if str(product['product']['id']) == config.claiming.product:
                        quantity += product['quantity']
                
                return True, order_data(
                    product_id=str(config.claiming.product) if quantity > 0 else '0',
                    order_time=int(
                        datetime.strptime(resjson['data']['timeline'][0]['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                            .replace(tzinfo=timezone.utc)
                            .timestamp()
                    ),
                    quantity=quantity,
                    paid=resjson['data']['status']== 3
                )
            
            else:
                raise Exception
        
        else:
            return False, 'unknown'


async def confirm_order(order_id, discord_id):
    "Returns `tuple[bool, Union[str, order_data], int, str]`. str will be returned on False, order_data will be returned on True. int is the user's new balance (if it changed)."
    success, data = get_order(order_id)
    if success:
        if data.order_time > config.claiming.start_time:
            if data.product_id == config.claiming.product:
                if data.paid:
                    db = utils.database.Connection()
                    dup_check = db.query2('SELECT user FROM credits WHERE reason LIKE ?', [f'%{order_id}%'], True)
                    if dup_check is not None:
                        db.close()
                        return False, "claimed", -1, ""
                    else:
                        credit_count = utils.get_credits(discord_id)
                        total = credit_count + data.quantity
                        
                        db.insert('credits', [discord_id, data.quantity, f'{config.claiming.mode}: {order_id}', total])
                        db.close()

                        return True, data, total, utils.lang.process(utils.lang.cmd_claim_success_log, {
                            'user': f'<@{discord_id}>',
                            'quantity': data.quantity,
                            'credit_before': credit_count,
                            'credit_after': total,
                            'source': config.claiming.mode,
                            'order': order_id
                        })
                else:
                    return False, 'payment', -1, ""
            else:
                return False, 'product_id', -1, ""
        else:
            return False, 'start_time', -1, ""
    else:
        return False, data, -1, ""