import stripe
import os
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

if not STRIPE_SECRET_KEY:
    raise Exception("STRIPE_SECRET_KEY not found in .env")

stripe.api_key = STRIPE_SECRET_KEY


def create_checkout_session(user_id: int):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",

            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": "Pro Plan",
                    },
                    "unit_amount": 49900,  
                    "recurring": {
                        "interval": "month"
                    },
                },
                "quantity": 1,
            }],

            
            success_url="http://127.0.0.1:8000/payment-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/payment-cancel",

            
            metadata={
                "user_id": str(user_id)
            },
            client_reference_id=str(user_id)
        )

        return session.url

    except Exception as e:
        print(" Stripe Error:", str(e))
        raise Exception("Stripe session creation failed")