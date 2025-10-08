def format_otomax_dict(data: dict) -> str:
    parts = []
    for key, value in data.items():
        if isinstance(value, dict):
            # Untuk objek bersarang (nested dict), kita panggil fungsi ini lagi (rekursif)
            # dan membungkus hasilnya dalam kurung kurawal {}
            formatted_value = "{" + format_otomax_dict(value) + "}"
            parts.append(f"{key}={formatted_value}")
        elif isinstance(value, bool):
            # Konversi boolean ke string "true" atau "false"
            parts.append(f"{key}={str(value).lower()}")
        else:
            # Untuk nilai sederhana, langsung format tanpa tanda kutip
            # Gunakan str(value) untuk menangani angka
            parts.append(f"{key}={value!s}")

    # Gabungkan semua bagian dengan delimiter '&'
    return "&".join(parts)
    # hapus spasi berlebih


# Data input adalah raw_response Anda
raw_response = {
    "status_code": 200,
    "url": "10.0.0.3",
    "debug": False,
    "meta": {
        "status_code": 200,
        "elapsed_time_s": 0.817751,
        "content_type": "application/json; charset=utf-8",
        "response_type": "DICT",
        "description": "ok",
    },
    "parse": "SUCCESS",
    "cleaned_data": {
        "ngrs": {
            "1000": "0",
            "10000": "0",
            "15000": "0",
            "20000": "0",
            "25000": "0",
            "50000": "0",
            "100000": "0",
            "BULK": "0",
        },
        "linkaja": "3230",
        "finpay": "0",
    },
    "description": "Data berhasil di-parse",
}

# Lakukan transformasi
otomax_friendly_response_final = format_otomax_dict(raw_response)

print(otomax_friendly_response_final)
