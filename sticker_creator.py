from PIL import Image, ImageDraw, ImageFont
import os
import re

# --- Configuration ---
BASE_IMAGE_PATH = "LargeSquare.png"
INDIVIDUAL_STICKER_OUTPUT_DIR = "tornado_stickers_v3"
FINAL_SHEET_FILENAME = "sticker_sheet.png"
FONT_PATH = "gunplay rg.otf"
FONT_PATH_FALLBACK = "arial.ttf"

TEXT_COLOR = "#E0E0E0"

EF_COLORS = {
    "EFU": "#B0B0B0", "EF0": "#B0B0B0", "EF1": "#B0B0B0",
    "EF2": "#FFFF00", "EF3": "#FFA500", "EF4": "#FF0000",
    "EF5": "#FF00FF",
}
DEFAULT_FUNNEL_COLOR = "#808080"

DATE_FONT_SIZE = 95
LOCATION_FONT_SIZE = 85
EF_RATING_FONT_SIZE = 130

# Sheet Layout Configuration
STICKERS_PER_ROW_FOR_SHEET = 13
PADDING_BETWEEN_STICKERS_X = 15 # Horizontal space between stickers
PADDING_BETWEEN_STICKERS_Y = 15 # Vertical space between stickers
MARGIN_AROUND_SHEET_X = 30      # Left/Right margin for the entire sheet
MARGIN_AROUND_SHEET_Y = 30      # Top/Bottom margin for the entire sheet
SHEET_BACKGROUND_COLOR = (0, 0, 0) # Black

if not os.path.exists(INDIVIDUAL_STICKER_OUTPUT_DIR):
    os.makedirs(INDIVIDUAL_STICKER_OUTPUT_DIR)

# --- Helper Functions (mostly unchanged) ---
def parse_sticker_line(line):
    parts = line.split(" - ")
    if len(parts) == 3:
        date = parts[0].strip()
        location = parts[1].strip()
        ef_rating_str = parts[2].strip()
        return date, location, ef_rating_str
    return None, None, None

def get_ef_category_color(ef_rating_str):
    ef_rating_str_upper = ef_rating_str.upper()
    if "EF5" in ef_rating_str_upper: cat = "EF5"
    elif "EF4" in ef_rating_str_upper: cat = "EF4"
    elif "EF3" in ef_rating_str_upper: cat = "EF3"
    elif "EF2" in ef_rating_str_upper: cat = "EF2"
    elif "EF1" in ef_rating_str_upper and "EF0-EF1" not in ef_rating_str_upper : cat = "EF1"
    elif "EF0-EF1" in ef_rating_str_upper: cat = "EF0"
    elif "EF0" in ef_rating_str_upper: cat = "EF0"
    elif "EFU" in ef_rating_str_upper: cat = "EFU"
    else:
        match = re.search(r'EF(\d)', ef_rating_str_upper)
        if match:
            cat = f"EF{match.group(1)}"
            if cat not in EF_COLORS: return DEFAULT_FUNNEL_COLOR
        else: return DEFAULT_FUNNEL_COLOR
    return EF_COLORS.get(cat, DEFAULT_FUNNEL_COLOR)

def recolor_graphic(base_image, new_color_hex):
    img = base_image.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    img_data = img.load(); mask_data = mask.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img_data[x, y]
            if a > 0 and (r > 15 or g > 15 or b > 15): mask_data[x, y] = 255
    colored_layer = Image.new("RGBA", img.size, new_color_hex)
    final_image = Image.new("RGBA", img.size, (0,0,0,255)); final_image.paste(colored_layer, (0,0), mask)
    return final_image.convert("RGB")

def draw_text_with_wrapping(draw, text, position_xy_center, base_font_path, initial_font_size, max_width, fill, line_spacing_factor=1.15):
    x_center, y_block_center = position_xy_center
    words = text.split();
    if not words: return
    current_font_size = initial_font_size
    font_to_use = None
    while current_font_size > 10:
        font_to_use = ImageFont.truetype(base_font_path, current_font_size)
        lines = []; current_line_text = words[0]
        for word in words[1:]:
            if draw.textlength(current_line_text + " " + word, font=font_to_use) <= max_width:
                current_line_text += " " + word
            else: lines.append(current_line_text); current_line_text = word
        lines.append(current_line_text)
        if len(lines) == 1 and draw.textlength(lines[0], font=font_to_use) > max_width:
            current_font_size -= 3
            if current_font_size < 10: current_font_size = 10
            continue
        break
    font = ImageFont.truetype(base_font_path, current_font_size)
    final_lines = []; current_line_text = words[0]
    for word in words[1:]:
        if draw.textlength(current_line_text + " " + word, font=font) <= max_width: current_line_text += " " + word
        else: final_lines.append(current_line_text); current_line_text = word
    final_lines.append(current_line_text)
    ascent, descent = font.getmetrics(); font_line_box_height = ascent + descent
    spaced_line_height = font_line_box_height * line_spacing_factor
    total_block_height = (len(final_lines) - 1) * spaced_line_height + font_line_box_height
    current_y_top_of_line = y_block_center - (total_block_height / 2)
    for line_text in final_lines:
        line_w = draw.textlength(line_text, font=font)
        draw.text((x_center - (line_w / 2), current_y_top_of_line), line_text, font=font, fill=fill)
        current_y_top_of_line += spaced_line_height

# --- Sticker Data ---
sticker_data_input = """
05.18.13 - YOUNG, TEXAS - EF0-EF1
05.19.13 - WELSTON/LUTHER, OKLAHOMA - EF3
05.19.13 - EDMOND, OKLAHOMA - EF3
05.27.13 - CORA, KANSAS - EF3
05.31.13 - EL RENO, OKLAHOMA - EF5
06.26.13 - HAWK SPRINGS, WYOMING - EF1
12.22.13 - RUSTON, LOUISIANA - EF3
04.13.14 - VELMA, OKLAHOMA - EF0
04.28.14 - BAZEMORE, ALABAMA - EF1
04.28.14 - LITTLE SANDY CREEK, ALABAMA - EF1
05.11.14 - FAIRFIELD/SUTTON, NEBRASKA - EF3
05.11.14 - EXETER/GOEHNER, NEBRASKA - EF3
06.16.14 - PILGER, NEBRASKA - EF4
06.17.14 - COLERIDGE, NEBRASKA - EF3
06.18.14 - ALPENA, SOUTH DAKOTA - EF4
07.23.14 - CONSUL, SASKATCHEWAN - EF2
04.24.15 - SYLAN GROVE, OKLAHOMA - EF1
05.07.15 - SW DENTON, TEXAS - EF1
05.10.15 - SW BRANDON, TEXAS - EF3
05.19.15 - RYAN, OKLAHOMA - EF0
06.04.15 - SIMLA, COLORADO - EF1
07.21.15 - NW BISON, SOUTH DAKOTA - EF3
07.28.15 - NEAR PIERSON, MANITOBA - EF2
01.22.18 - CANTON, TEXAS - EF0
03.02.18 - BUXTON-FARGO, NORTH DAKOTA - EF0
03.19.18 - RUSSELLVILLE, ALABAMA - EF1
03.21.18 - RUSSELLVILLE, ALABAMA - EF1
05.01.18 - TESCOTT, KANSAS - EF3
05.01.18 - BENNINGTON, KANSAS - EF3
05.02.18 - TESCOTT, KANSAS - EF1
03.23.19 - SANDLOT, ARKANSAS - EF3
05.17.19 - MCCOOK, NEBRASKA - EF2
05.28.19 - LAWRENCE, KANSAS - EF4
05.28.19 - LAWRENCE, WYOMING - EF4
04.07.23 - LINNEUS, MISSOURI - EF2
04.19.23 - COLE, OKLAHOMA - EF3
05.12.23 - SPALDING, NEBRASKA - EF1
06.14.23 - NEWTON, GEORGIA - EF1
06.15.23 - SE LOCO, OKLAHOMA - EF2
06.17.23 - NEWTON, GEORGIA - EF1
04.16.24 - SALEM, IOWA - EF2
04.26.24 - COUNCIL BLUFFS, IOWA - EF1
04.26.24 - WATERLOO, NEBRASKA - EF4
04.26.24 - LINCOLN (HAVELOCK), NEBRASKA - EF3
05.19.24 - CUSTER CITY, OKLAHOMA - EF1
05.25.24 - WINDTHORST, TEXAS - EF1
11.02.24 - HOBBS, NEW MEXICO - EFU
11.02.24 - LEXINGTON, OKLAHOMA - EF0
11.04.24 - IDABEL (HOLLY CREEK), OKLAHOMA - EF1
03.14.25 - JONESBORO, ARKANSAS - EF0
03.14.25 - BAKERSFIELD, MISSOURI - EF3
"""
sticker_data_input_lines = [line.strip() for line in sticker_data_input.strip().split('\n') if line.strip()]

# --- Main Script Execution ---
try:
    base_img_original = Image.open(BASE_IMAGE_PATH)
except FileNotFoundError:
    print(f"Error: Base image '{BASE_IMAGE_PATH}' not found.")
    exit()

font_paths_to_try = [FONT_PATH, FONT_PATH_FALLBACK]
loaded_font_path = None
for fp_try in font_paths_to_try:
    try:
        ImageFont.truetype(fp_try, 10); loaded_font_path = fp_try
        print(f"Using font: {loaded_font_path}"); break
    except IOError: print(f"Warning: Font '{fp_try}' not found.")
if not loaded_font_path: print(f"Error: No usable font found."); exit()

img_width, img_height = base_img_original.size
center_x = img_width / 2
y_pos_date_center = img_height * 0.13
y_pos_location_center = img_height * 0.23
y_pos_ef_center = img_height * 0.90
location_max_width = img_width * 0.70

font_date_obj = ImageFont.truetype(loaded_font_path, DATE_FONT_SIZE)
font_ef_obj = ImageFont.truetype(loaded_font_path, EF_RATING_FONT_SIZE)

# Store paths of generated stickers for sheet creation
generated_sticker_paths = []

print("\n--- Generating Individual Stickers ---")
for i, line_data in enumerate(sticker_data_input_lines):
    date_str, location_str, ef_str = parse_sticker_line(line_data)
    if not date_str: continue

    funnel_color_hex = get_ef_category_color(ef_str)
    sticker_canvas = recolor_graphic(base_img_original.copy(), funnel_color_hex)
    draw = ImageDraw.Draw(sticker_canvas)

    date_w = draw.textlength(date_str, font=font_date_obj)
    ascent_date, descent_date = font_date_obj.getmetrics()
    draw.text((center_x - date_w / 2, y_pos_date_center - (ascent_date + descent_date) / 2),
              date_str, font=font_date_obj, fill=TEXT_COLOR)

    draw_text_with_wrapping(draw, location_str, (center_x, y_pos_location_center),
                            loaded_font_path, LOCATION_FONT_SIZE, location_max_width, TEXT_COLOR)

    ef_w = draw.textlength(ef_str, font=font_ef_obj)
    ascent_ef, descent_ef = font_ef_obj.getmetrics()
    draw.text((center_x - ef_w / 2, y_pos_ef_center - (ascent_ef + descent_ef) / 2),
              ef_str, font=font_ef_obj, fill=TEXT_COLOR)

    safe_loc = re.sub(r'[^\w\s-]', '', location_str.split(',')[0]).strip().replace(' ', '_')[:30]
    safe_ef = re.sub(r'[^\w?-]', '', ef_str)
    filename = f"{date_str.replace('.', '-')}_{safe_loc}_{safe_ef}.png"
    output_path = os.path.join(INDIVIDUAL_STICKER_OUTPUT_DIR, filename)
    
    sticker_canvas.save(output_path)
    generated_sticker_paths.append(output_path) # Save path for sheet creation
    print(f"Generated: {output_path}")

print(f"\nDone generating {len(generated_sticker_paths)} individual stickers.")

# --- Create Sticker Sheet ---
if not generated_sticker_paths:
    print("No stickers were generated, so sheet creation is skipped.")
else:
    print("\n--- Creating Sticker Sheet ---")
    # Assume all stickers are the same size, get dimensions from the first one
    first_sticker_img = Image.open(generated_sticker_paths[0])
    sticker_w, sticker_h = first_sticker_img.size
    first_sticker_img.close()

    num_stickers = len(generated_sticker_paths)
    num_cols = STICKERS_PER_ROW_FOR_SHEET
    num_rows = (num_stickers + num_cols - 1) // num_cols # Ceiling division

    sheet_width = (sticker_w * num_cols) + (PADDING_BETWEEN_STICKERS_X * (num_cols - 1)) + (2 * MARGIN_AROUND_SHEET_X)
    sheet_height = (sticker_h * num_rows) + (PADDING_BETWEEN_STICKERS_Y * (num_rows - 1)) + (2 * MARGIN_AROUND_SHEET_Y)

    sticker_sheet = Image.new("RGB", (sheet_width, sheet_height), SHEET_BACKGROUND_COLOR)
    
    current_x = MARGIN_AROUND_SHEET_X
    current_y = MARGIN_AROUND_SHEET_Y
    
    for i, sticker_path in enumerate(generated_sticker_paths):
        col_index = i % num_cols
        row_index = i // num_cols

        # Calculate position for the current sticker
        paste_x = MARGIN_AROUND_SHEET_X + col_index * (sticker_w + PADDING_BETWEEN_STICKERS_X)
        paste_y = MARGIN_AROUND_SHEET_Y + row_index * (sticker_h + PADDING_BETWEEN_STICKERS_Y)
        
        try:
            sticker_img_to_paste = Image.open(sticker_path)
            sticker_sheet.paste(sticker_img_to_paste, (paste_x, paste_y))
            sticker_img_to_paste.close()
        except FileNotFoundError:
            print(f"Error: Could not find sticker image {sticker_path} for sheet.")
        except Exception as e:
            print(f"Error pasting {sticker_path}: {e}")

    sheet_output_path = FINAL_SHEET_FILENAME # Save in the script's root directory
    sticker_sheet.save(sheet_output_path)
    print(f"\nSticker sheet saved as: {sheet_output_path}")

print("\nAll processing complete.")