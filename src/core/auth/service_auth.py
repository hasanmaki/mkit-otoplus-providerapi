"""auth transaction servicee."""

import hmac
from typing import Annotated

from fastapi import Depends, HTTPException

from core.auth.sch_transaction import TrxAuthPayload
from core.auth.srv_signature import OtomaxSignatureService
from src.config.settings import AppSettings
from src.deps import get_app_settings, get_client_ip


async def authenticate_request(
    payload: TrxAuthPayload,
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    ip_address: Annotated[str, Depends(get_client_ip)],
) -> TrxAuthPayload:
    """Fungsi dependen untuk mengotentikasi permintaan."""
    # Pengecekan pertama: memberID
    member = next((m for m in settings.members if m.memberid == payload.memberid), None)
    if not member:
        raise HTTPException(status_code=401, detail="Invalid member ID.")

    # Pengecekan kedua: keaktifan member
    if not member.is_active:
        raise HTTPException(status_code=401, detail="Member is inactive.")

    # Pengecekan ketiga: alamat IP
    client_ip = ip_address
    if client_ip not in member.ip_address:
        raise HTTPException(status_code=401, detail="IP address not allowed.")

    # Pengecekan terakhir: signature
    expected_signature = OtomaxSignatureService.generate_transaction_signature(
        memberid=member.memberid,
        product=payload.product,
        dest=payload.dest,
        refid=payload.refid,
        pin=member.pin,
        password=member.password,
    )

    if not hmac.compare_digest(payload.sign, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature.")

    return payload
