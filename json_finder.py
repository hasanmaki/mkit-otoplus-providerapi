import argparse
import json
from pathlib import Path


# === Load JSON ===
def load_json_file(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File tidak ditemukan: {path}")
    except json.JSONDecodeError:
        print(f"❌ File {path} tidak valid JSON.")
    except Exception as e:
        print(f"❌ Error tidak terduga: {e}")
    return None


# === Recursive Finders ===
def deep_find(data, target_key: str, depth: int = 0, max_depth: int = 0):
    """Cari key pertama yang cocok (case-insensitive) dalam nested dict/list."""
    max_depth = max(depth, max_depth)

    if isinstance(data, dict):
        for k, v in data.items():
            if target_key.lower() in k.lower():
                return {k: v}, k, max_depth
            result, found_key, max_depth = deep_find(
                v, target_key, depth + 1, max_depth
            )
            if result is not None:
                return result, found_key, max_depth

    elif isinstance(data, list):
        for item in data:
            result, found_key, max_depth = deep_find(
                item, target_key, depth + 1, max_depth
            )
            if result is not None:
                return result, found_key, max_depth

    return None, None, max_depth


def deep_find_all(data, target_key: str):
    """Cari semua key yang cocok dalam nested dict/list."""
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            if target_key.lower() in k.lower():
                results.append({k: v})
            results.extend(deep_find_all(v, target_key))
    elif isinstance(data, list):
        for item in data:
            results.extend(deep_find_all(item, target_key))
    return results


def deep_find_any(data, *candidate_keys: str):
    """Coba cari salah satu dari beberapa key kandidat."""
    for key in candidate_keys:
        result, found_key, depth = deep_find(data, key)
        if result:
            return result, found_key, depth
    return None, None, 0


# === CLI ===
def main():
    parser = argparse.ArgumentParser(
        description="🔍 Deep key finder untuk nested JSON file (debug API)."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path ke file JSON target (misal: profile_response.json)",
    )
    parser.add_argument("--key", help="Cari satu key (case-insensitive).")
    parser.add_argument("--all", help="Cari semua key yang mengandung teks tertentu.")
    parser.add_argument(
        "--any",
        nargs="+",
        help="Cari salah satu dari beberapa kandidat key (misal: --any rewardSummary summary_profile).",
    )
    parser.add_argument(
        "--limit", type=int, default=3, help="Batas hasil yang ditampilkan (default=3)."
    )

    args = parser.parse_args()

    path = Path(args.file)
    data = load_json_file(path)
    if not data:
        return

    print(f"📂 File: {path.absolute()}")
    print("=" * 80)

    if args.key:
        print(f"🔍 MODE: deep_find('{args.key}')")
        result, key_found, depth = deep_find(data, args.key)
        if result:
            print(f"✅ Ketemu key: '{key_found}' di depth: {depth}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("⚠️ Tidak ditemukan.")

    elif args.all:
        print(f"🔎 MODE: deep_find_all('{args.all}')")
        all_results = deep_find_all(data, args.all)
        print(f"Total match ditemukan: {len(all_results)}")
        for idx, res in enumerate(all_results[: args.limit], 1):
            print(f"\n📍 Match #{idx}:")
            print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.any:
        print(f"🧠 MODE: deep_find_any({', '.join(args.any)})")
        result, key_found, depth = deep_find_any(data, *args.any)
        if result:
            print(f"✅ Ketemu key: '{key_found}' di depth: {depth}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("⚠️ Tidak ada key yang cocok ditemukan.")

    else:
        print("❌ Harus pilih salah satu mode: --key, --all, atau --any")


if __name__ == "__main__":
    main()
