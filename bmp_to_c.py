from PIL import Image
import numpy as np

def bmp_to_c_array(image_path, output_array_name="bitmap"):
    # Load image
    img = Image.open(image_path).convert('1')  # Convert to 1-bit
    width, height = img.size

    # Convert to NumPy array (1-bit: 0=black, 1=white)
    img_data = np.array(img, dtype=np.uint8)
    img_data = 1 - img_data  # Invert (optional)

    # Pack bits into bytes
    row_padded = (width + 7) // 8  # Ensure width fits into bytes
    packed_data = np.zeros(row_padded * height, dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            if img_data[y, x]:  # If pixel is white (1)
                packed_data[y * row_padded + x // 8] |= (1 << (7 - (x % 8)))

    # Generate C-style array
    hex_array = ', '.join(f'0x{byte:02X}' for byte in packed_data)
    c_code = f"const uint8_t {output_array_name}[] = {{\n    {hex_array}\n}};"

    # Save to file
    with open("bitmap.h", "w") as f:
        f.write(c_code)

    print("C array saved to bitmap.h")
    return c_code

# Example usage
bmp_to_c_array("input.bmp")
