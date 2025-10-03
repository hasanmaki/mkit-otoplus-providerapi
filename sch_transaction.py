"""schemas untuk transaksi di digipos."""

from pydantic import BaseModel, Field


class TrxBaseConfig(BaseModel):
    """Base config for digipos transaksi."""

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "validate_by_alias": True,
        "extra": "forbid",
    }


class TrxAuthPayload(TrxBaseConfig):
    """Generic request schema for digipos transaksi."""

    memberid: str = Field(description="Member ID User yang di daftarkan di settings.")
    product: str = Field(
        description="Kode produk yang di inginkan.",
    )
    dest: str = Field(
        pattern=r"^\d+$", description="tujuan transaksi/ nomor handphone or voucher."
    )
    refid: str = Field(description="Reference ID unik untuk transaksi. dari otomax")
    sign: str = Field(description="Signature untuk autentikasi")
