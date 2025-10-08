import json
from pathlib import Path

path = Path(__file__).parent / "experiments/product_response.json"
try:
    with open(path) as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: The file {path} was not found.")
except json.JSONDecodeError:
    print(f"Error: The file {path} contains invalid JSON.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


def deep_find(
    data: dict | list, target_keys: list[str], depth: int = 0, max_depth: int = 0
):
    """Cari key secara rekursif dalam nested dict/list."""
    max_depth = max(depth, max_depth)  # Track maximum depth

    if isinstance(data, dict):
        for k, v in data.items():
            for target_key in target_keys:
                if target_key.lower() in k.lower():
                    return {k: v}, max_depth  # return subdict yang match
            result, max_depth = deep_find(v, target_keys, depth + 1, max_depth)
            if result is not None:
                return result, max_depth
    elif isinstance(data, list):
        for item in data:
            result, max_depth = deep_find(item, target_keys, depth + 1, max_depth)
            if result is not None:
                return result, max_depth
    return None, max_depth


def main():
    target_keys_input = input("Masukkan key yang ingin dicari (pisahkan dengan koma): ")
    target_keys = [key.strip() for key in target_keys_input.split(",")]
    result, max_depth = deep_find(data, target_keys)
    if result:
        print("Hasil pencarian:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Maximum recursion depth: {max_depth}")
    else:
        print("Key tidak ditemukan.")


if __name__ == "__main__":
    main()
