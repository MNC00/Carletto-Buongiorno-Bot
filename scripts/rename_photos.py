import os
import random


def generate_superhero_compliment() -> str:
    compliments = [
        "invincibile",
        "fortissimo",
        "velocissimo",
        "potentissimo",
        "imbattibile",
        "leggendario",
        "eroico",
        "straordinario",
        "incredibile",
        "mitico",
    ]
    return random.choice(compliments)


def rename_photos() -> None:
    photos_dir = os.path.join("data", "photos")

    if not os.path.exists(photos_dir):
        print(f"La cartella {photos_dir} non esiste.")
        return

    for index, filename in enumerate(os.listdir(photos_dir)):
        file_path = os.path.join(photos_dir, filename)
        if os.path.isfile(file_path):
            extension = os.path.splitext(filename)[1]
            new_name = f"carlo_{generate_superhero_compliment()}_{index + 1}{extension}"
            new_path = os.path.join(photos_dir, new_name)
            os.rename(file_path, new_path)
            print(f"Rinominato {filename} in {new_name}")


if __name__ == "__main__":
    rename_photos()
