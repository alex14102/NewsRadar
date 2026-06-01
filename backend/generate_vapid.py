#!/usr/bin/env python3
"""Generate VAPID keys for Web Push notifications. Run once and add to .env."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import base64


def generate_vapid_keys():
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()

    private_bytes = private_key.private_numbers().private_value.to_bytes(32, "big")
    private_b64 = base64.urlsafe_b64encode(private_bytes).rstrip(b"=").decode()

    public_numbers = public_key.public_key().public_numbers() if hasattr(public_key, 'public_key') else public_key.public_numbers()
    x = public_numbers.x.to_bytes(32, "big")
    y = public_numbers.y.to_bytes(32, "big")
    public_bytes = b"\x04" + x + y
    public_b64 = base64.urlsafe_b64encode(public_bytes).rstrip(b"=").decode()

    print("VAPID keys generated. Add these to your .env file:\n")
    print(f'VAPID_PUBLIC_KEY="{public_b64}"')
    print(f'VAPID_PRIVATE_KEY="{private_b64}"')
    print(f'VAPID_EMAIL="mailto:your@email.com"')


if __name__ == "__main__":
    generate_vapid_keys()
