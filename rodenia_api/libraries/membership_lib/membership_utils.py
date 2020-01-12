import stripe


def cancel_membership(customer_id):
    customer = stripe.Customer.retrieve(customer_id)

    if len(customer["subscriptions"]["data"]) == 0:
        return {"error": "No subscriptions found for user."}

    subscription = customer["subscriptions"]["data"][0]
    subscriptionId = subscription["id"]
    customer.subscriptions.retrieve(subscriptionId).delete()


def update_billing(customer_id, stripe_token):
    customer = stripe.Customer.retrieve(customer_id)

    if len(customer["sources"]["data"]) != 0:
        source = customer["sources"]["data"][0]
        source_id = source["id"]
        customer.sources.retrieve(source_id).delete()

    result = customer.sources.create(source=stripe_token)
    return result


# @TODO: Make this generic to support multi-subscription services.
def get_membership_data(customer_id):
    customer = stripe.Customer.retrieve(customer_id)

    if len(customer["sources"]["data"]) == 0:
        source = None
    else:
        source = customer["sources"]["data"][0]

    subscription = None
    if len(customer["subscriptions"]["data"]) == 0:
        print("whoops its empty!!!")
    else:
        subscription = customer["subscriptions"]["data"][0]

    return {
        "source": source,
        "subscription": subscription
    }


def update_subscription(subscription_id, subscription_item_id, plan):
    stripe.Subscription.modify(subscription_id,
                               cancel_at_period_end=False,
                               items=[{
                                   'id': subscription_item_id,
                                   'plan': plan,
                               }]
                               )
