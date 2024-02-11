import yaml

f = open('lang.yml', 'r')
_lang = dict(yaml.safe_load(f))
f.close()

no_admin = _lang.get('no_admin', "You aren't an admin!")
general_error = _lang.get('general_error', "Error: {error}")
retry_later_error = _lang.get('retry_later_error', "Please try again later.")
unauthorized_error = _lang.get('unauthorized_error', "API Unauthorized. Please contact the owner!")
bool_true = _lang.get('bool_true', "true")
bool_false = _lang.get('bool_false', "false")
anonymous = _lang.get('anonymous', "anonymous")
anonymous_upper = _lang.get('anonymous_upper', "Anonymous")
embed_fetch_error = _lang.get('embed_fetch_error', "Failed to get orders for queue embed:")
new_update_available_log = _lang.get('new_update_available_log', "New Update Available: ({version}) (you are on {current_version}). Download: {download_url}")

cmd_claim = _lang.get('cmd_claim', "claim")
cmd_claim_desc = _lang.get('cmd_claim_desc', "Claim credits with a product ID.")
cmd_claim_arg_order_id = _lang.get('cmd_claim_arg_order_id', "Your Order/Invoice ID.")
cmd_claim_order_incomplete = _lang.get('cmd_claim_order_incomplete', "This order hasn't been paid for.")
cmd_claim_no_order_exists = _lang.get('cmd_claim_no_order_exists', "Couldn't find an order with that ID.")
cmd_claim_invalid_product_id = _lang.get('cmd_claim_invalid_product_id', "This order isn't for nitro snipes.")
cmd_claim_order_before_time = _lang.get('cmd_claim_order_before_time', "This order was made before the migration. Contact the owner.")
cmd_claim_order_already_claimed = _lang.get('cmd_claim_order_already_claimed', "This order has already been claimed.")
cmd_claim_success = _lang.get('cmd_claim_success', "Claimed! You now have {total} credits.")
cmd_claim_success_log = _lang.get('cmd_claim_success_log', "{user} claimed {quantity} credits ({credit_before} -> {credit_after}) from {source}: `{order}`")

cmd_credits = _lang.get('cmd_credits', "credits")
cmd_credits_desc = _lang.get('cmd_credits_desc', "Shows how many credits you have.")
cmd_credits_arg_hidden = _lang.get('cmd_credits_arg_hidden', "If true, only show how many credits you have to yourself.")
cmd_credits_arg_user = _lang.get('cmd_credits_arg_user', "(Admin Only) Show number of credits a user has.")
cmd_credits_success = _lang.get('cmd_credits_success', "You have {total} credits!")
cmd_credits_success_user = _lang.get('cmd_credits_success_user', "{user} has {total} credits!")

cmd_purchase = _lang.get('cmd_purchase', "purchase")
cmd_purchase_desc = _lang.get('cmd_purchase_desc', "Create an order.")
cmd_purchase_arg_amount = _lang.get('cmd_purchase_arg_amount', "How many nitro snipes.")
cmd_purchase_arg_token = _lang.get('cmd_purchase_arg_token', "Your Discord Token.")
cmd_purchase_arg_anonymous = _lang.get('cmd_purchase_arg_anonymous', "If true, your name will be hidden in the queue.")
cmd_purchase_no_credits = _lang.get('cmd_purchase_no_credits', "You don't have enough credits!")
cmd_purchase_contact_owner = _lang.get('cmd_purchase_contact_owner', "Please contact the owner! (An alert has been sent in the logs channel.)")
cmd_purchase_contact_owner_log = _lang.get('cmd_purchase_contact_owner_log', "{user} tried to purchase {amount} snipes, but you don't have enough balance! ({global_credits} left)")
cmd_purchase_success = _lang.get('cmd_purchase_success', "You've been added to the queue! (Order {order})")
cmd_purchase_success_log = _lang.get('cmd_purchase_success_log', "{user} added {amount} snipes to queue. (Order {order}) (Credits: {credit_before} -> {credit_after}) (Your account has {global_credits} credits left.)")

cmd_cancel = _lang.get('cmd_cancel', "cancel")
cmd_cancel_desc = _lang.get('cmd_cancel_desc', "Remove your order from the queue.")
cmd_cancel_arg_order_id = _lang.get('cmd_cancel_arg_order_id', "Your Order ID.")
cmd_cancel_order_invalid = _lang.get('cmd_cancel_order_invalid', "Can't find an order with that ID.")
cmd_cancel_order_completed = _lang.get('cmd_cancel_order_completed', "This order has already been completed.")
cmd_cancel_no_permission = _lang.get('cmd_cancel_no_permission', "You didn't create this order.")
cmd_cancel_success = _lang.get('cmd_cancel_success', "Order {order} cancelled, refunded {amount} credits.")
cmd_cancel_success_log = _lang.get('cmd_cancel_success_log', "{user} removed their order ({order}) from the queue. (Your account has {global_credits} credits left.)")

cmd_award = _lang.get('cmd_award', "award")
cmd_award_desc = _lang.get('cmd_award_desc', "(Admin Only) Give/take credits to/from a user.")
cmd_award_arg_user = _lang.get('cmd_award_arg_user', "Recipient of credits.")
cmd_award_arg_amount = _lang.get('cmd_award_arg_amount', "Number of credits to give/take. (use a negative to take)")
cmd_award_arg_reason = _lang.get('cmd_award_arg_reason', "Reason for doing this.")
cmd_award_success = _lang.get('cmd_award_success', "{user} now has {credits} credits.")

cmd_orders = _lang.get('cmd_orders', "orders")
cmd_orders_desc = _lang.get('cmd_orders_desc', "Lists all of your orders.")
cmd_orders_arg_page = _lang.get('cmd_orders_arg_page', "What page to view.")
cmd_orders_arg_all_orders = _lang.get('cmd_orders_arg_all_orders', "(Admins Only) Lists all orders.")
cmd_orders_success = _lang.get('cmd_orders_success', "Fetched {total} orders.")
cmd_orders_success_data = _lang.get('cmd_orders_success_data', "Gifts: {received}/{quantity} | User: {user} | Anonymous: {anonymous} | Status: {status}")
cmd_orders_completed = _lang.get('cmd_orders_completed', "Completed")
cmd_orders_refunded = _lang.get('cmd_orders_refunded', "Failed")
cmd_orders_user_cancelled = _lang.get('cmd_orders_user_cancelled', "Cancelled")
cmd_orders_admin_cancelled = _lang.get('cmd_orders_admin_cancelled', "Failed")
cmd_orders_in_queue = _lang.get('cmd_orders_in_queue', "In Queue")
cmd_orders_token_invalidated = _lang.get('cmd_orders_token_invalidated', "Token Invalid")

cmd_buy = _lang.get('cmd_buy', "buy")
cmd_buy_desc = _lang.get('cmd_buy_desc', "Find out how to buy!")

cmd_token = _lang.get('cmd_token', "token")
cmd_token_desc = _lang.get('cmd_token_desc', "Get your Discord Token via QR Code.")
cmd_token_success = _lang.get('cmd_token_success', "Click here to view the QR code.")

queue_footer_text = _lang.get('queue_footer_text', "Updates every 30 seconds")
queue_gifts = _lang.get('queue_gifts', "Gifts")
queue_title = _lang.get('queue_title', "{name} Queue")
queue_length = _lang.get('queue_length', "Queue Length: {length}")

vps_footer_text = _lang.get('vps_footer_text', "Updates every 30 seconds")
vps_title = _lang.get('vps_title', "Sniper Instsances")

def process(lang_str:str, args:dict={}) -> str:
    return lang_str.format(**args)
