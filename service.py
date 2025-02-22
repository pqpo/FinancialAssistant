from pathlib import Path
import pandas as pd


def read_csv(file_str: Path):
    try:
        return pd.read_csv(file_str)
    except Exception as e:
        print(f"read csv failed: {file_str}, {e}")


def load_news(date_str: str, category: str):
    if category == 'all':
        data_path = Path.cwd() / "data" / date_str
    else:
        data_path = Path.cwd() / "data" / date_str / f"{category}.csv"
    print(f'load data {data_path}')
    if not data_path.exists():
        return None
    result = []
    if data_path.is_dir():
        for file in data_path.glob("**/*.csv"):
            item = read_csv(file)
            if item is not None:
                result.append(item)
    else:
        item = read_csv(data_path)
        if item is not None:
            result.append(item)
    return result
