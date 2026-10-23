from pathlib import Path

def surah_index_to_filename(x: int | str) -> str:
    """Convert number to surah filename."""
    x = int(x)
    if 100 <= x <= 114:
        return f"{x}.mp3"
    elif 0 < x < 10:
        return f"00{x}.mp3"
    elif 10 <= x < 100:
        return f"0{x}.mp3"
    else:
        raise ValueError(f"{x} isn't valid surah index.")

def filename_resolve(filename: str) -> list[str | int]:
    """Get surah index, reciter code, and moshaf type from filename."""
    parts = filename[6:-4].split("@@")
    return [parts[-1], parts[0].split("/")[-1], parts[1]]