"""OtomaX signature service."""

import base64
import hashlib
import hmac


class OtomaxSignatureService:
    """Service untuk generate dan verifikasi signature OtomaX API."""

    @staticmethod
    def generate_transaction_signature(
        memberid: str, product: str, dest: str, refid: str, pin: str, password: str
    ) -> str:
        """Generate OtomaX transaction signature.

        Algorithm:
            1. Build raw string: OtomaX|MEMBERID|PRODUCT|dest|refid|pin|password
               - memberid dan product diubah ke UPPERCASE
               - Field lain tetap original case
            2. SHA1 hash
            3. Base64 encode
            4. Hapus padding '='
            5. Replace '+' -> '-' dan '/' -> '_' (URL-safe)
        """
        # Build raw string
        raw = f"OtomaX|{memberid.upper()}|{product.upper()}|{dest}|{refid}|{pin}|{password}"

        # Generate SHA1 digest
        sha1_digest = hashlib.sha1(raw.encode()).digest()

        # Base64 encode dan URL-safe
        signature = base64.b64encode(sha1_digest).decode().rstrip("=")
        signature = signature.replace("+", "-").replace("/", "_")

        return signature

    @staticmethod
    def verify_signature(expected_data: dict, received_signature: str) -> bool:
        """Verifikasi signature secara timing-attack safe."""
        expected_signature = OtomaxSignatureService.generate_transaction_signature(
            **expected_data
        )
        return hmac.compare_digest(str(received_signature), str(expected_signature))
