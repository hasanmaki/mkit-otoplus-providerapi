import re

from pydantic import BaseModel, Field

from src.core.sch_response import ApiResponseGeneric


# InfoData harus punya 'to' dan 'paket' (list of ProductData)
class InfoData(BaseModel):
    to: str
    paket: list["ProductData"]


class ProductData(BaseModel):
    productid: str | int = Field(..., alias="productId")
    productname: str = Field(..., alias="productName")
    quota: str = Field(..., alias="quota")
    total: str | int = Field(..., alias="total_")

    @property
    def cleaned_productname(self) -> str:
        """Pembersihan nama produk."""
        val = str(self.productname).strip()
        val = re.sub(r"\s+", " ", val)
        val = re.sub(r"\bInternet\b", "Inet", val, flags=re.IGNORECASE)
        # val = re.sub(r"\bPaket\b", "", val, flags=re.IGNORECASE)
        val = re.sub(r"\s+", " ", val)
        return val.strip()

    @property
    def cleaned_quota(self) -> str:
        """Optimasi quota.

        - trim
        - hilangkan spasi ganda
        - setelah koma satu spasi
        - ganti 'Days' jadi 'D', 'GB', 'MB', 'Internet', 'Nasional', dll
        - bersihkan spasi/koma berlebih
        - hapus prefix seperti 'DATA Video/' pada setiap segmen
        """
        val = str(self.quota).strip()
        segmen = []
        for seg in val.split(","):
            s = re.sub(r"\s+", " ", seg.strip())
            # hapus prefix sebelum '/' jika ada
            if "/" in s:
                s = s.split("/", 1)[-1].strip()
            segmen.append(s) if s else None
        val = ",".join(segmen)
        # DAYS OPTIMIZATION
        val = re.sub(r"\b(\d+)\s+Days\b", r"\1D", val, flags=re.IGNORECASE)
        # GB/MB OPTIMIZATION
        val = re.sub(r"\b(\d+(?:\.\d+)?)\s+GB\b", r"\1GB", val, flags=re.IGNORECASE)
        val = re.sub(r"\b(\d+)\s+MB\b", r"\1MB", val, flags=re.IGNORECASE)
        # COMMON WORD REPLACEMENTS
        val = re.sub(r"\bInternet\b", "Net", val, flags=re.IGNORECASE)
        val = re.sub(r"\bNasional\b", "Nas", val, flags=re.IGNORECASE)
        val = re.sub(r"\bVidio\b", "Vid", val, flags=re.IGNORECASE)
        val = re.sub(r"\bVideo\b", "Vid", val, flags=re.IGNORECASE)
        val = re.sub(r"\bPrime\b", "", val, flags=re.IGNORECASE)

        # CLEANUP EXTRA SPACES AND COMMAS
        val = re.sub(r"\s+", " ", val)
        val = re.sub(r",\s*,", ",", val)
        val = re.sub(r"^\s*,\s*", "", val)
        val = re.sub(r"\s*,\s*$", "", val)
        return val.strip()


class ProductListResponse(ApiResponseGeneric[InfoData]):
    """response model for product list."""

    data: InfoData

    def to_text(self) -> str:
        """Convert the response to text with header info and product list (single line, no newline)."""
        produk_lines = []
        for product in self.data.paket:
            line = f"{product.productid}({product.cleaned_productname}|{product.cleaned_quota})-{product.total}"
            produk_lines.append(line)
        produk_text = "#".join(produk_lines)
        # Hitung content_length dari hasil text
        header = (
            f"status_code={self.status_code}"
            f"&content_length={len(produk_text)}"
            f"&meta={self.meta}"
            f"&to={self.data.to}"
            f"&paket=#"
        )
        return header + produk_text
