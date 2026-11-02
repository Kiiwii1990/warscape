"""Build labelled Blizzard-icon comparison sheets from the installed 3.3.5 client.

Usage: py addons/WarscapeHUD/tools/build_icon_review.py --client <game-dir> --out <folder>
Only local archived BLPs are read. This utility does not alter game or addon assets.
"""
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont
from client_assets import ClientAssets

CANDIDATES = {
    "settings": [
        "INV_Misc_Gear_01", "INV_Misc_Gear_02", "INV_Gizmo_02", "INV_Gizmo_04", "Trade_Engineering",
    ],
    "friends": [
        "INV_Misc_GroupLooking", "INV_Misc_GroupNeedMore", "Ability_Hunter_HuntingParty",
        "Spell_Nature_AstralRecalGroup",
    ],
    "quests": [
        "INV_Misc_Note_01", "INV_Misc_Note_03", "INV_Misc_Note_05", "INV_Scroll_02", "INV_Scroll_06",
    ],
    "equipment": [
        "INV_Chest_Cloth_08", "INV_Chest_Leather_01", "INV_Chest_Chain_04", "INV_Chest_Plate01",
        "INV_Shield_01",
    ],
    "attack-styles": [
        "Ability_Warrior_Bladestorm", "Ability_Warrior_SwordandBoard", "Ability_Warrior_WeaponMastery",
        "Ability_DualWield", "Ability_Rogue_DualWeild",
    ],
    "prayer": [
        "INV_Jewelry_Necklace_02", "INV_Jewelry_Necklace_21", "INV_Jewelry_Necklace_27",
        "INV_Jewelry_Talisman_08",
    ],
    "spellbook": [
        "INV_Misc_Book_01", "INV_Misc_Book_03", "INV_Misc_Book_07", "INV_Misc_Book_11", "INV_Misc_Book_14",
    ],
}


def build(client: Path, output: Path) -> None:
    assets = ClientAssets(client)
    output.mkdir(parents=True, exist_ok=True)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 12)
    title_font = ImageFont.truetype(str(font_path), 18)
    cell_width, height = 210, 245

    for category, names in CANDIDATES.items():
        sheet = Image.new("RGB", (len(names) * cell_width, height), (20, 21, 22))
        draw = ImageDraw.Draw(sheet)
        draw.text((14, 10), category.replace("-", " ").title() + " — Original Blizzard icon candidates", font=title_font,
                  fill=(245, 202, 73))
        for index, name in enumerate(names):
            x = index * cell_width
            draw.rounded_rectangle((x + 5, 38, x + cell_width - 5, height - 6), radius=7,
                                   fill=(31, 32, 33), outline=(130, 99, 47), width=1)
            path = f"Interface\\Icons\\{name}.blp"
            data, _archive = assets.get(path)
            icon = Image.open(BytesIO(data)).convert("RGBA")
            icon = icon.crop((4, 4, 60, 60))
            # Match the HUD: a 44-square cell with a 36-square icon, then show
            # a nearest-neighbour enlargement below for detail comparison.
            button = Image.new("RGBA", (44, 44), (16, 17, 18, 255))
            ImageDraw.Draw(button).rectangle((0, 0, 43, 43), outline=(182, 137, 57), width=2)
            button.alpha_composite(icon.resize((36, 36), Image.Resampling.NEAREST), (4, 4))
            center_x = x + cell_width // 2
            sheet.paste(button.convert("RGB"), (center_x - 22, 48))
            large = icon.resize((112, 112), Image.Resampling.NEAREST)
            sheet.paste(large.convert("RGB"), (center_x - 56, 99))
            base = name + ".blp"
            for line_index, line in enumerate(textwrap.wrap(base, width=25)[:2]):
                draw.text((x + 8, 215 + line_index * 14), line, font=font, fill=(232, 229, 218))
        sheet.save(output / f"{category}.png")


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--client", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    build(args.client, args.out)


if __name__ == "__main__":
    main()
