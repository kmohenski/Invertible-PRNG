from PIL import Image

PIC_SIZE = 64
COLOR_BITS = 8
PIXEL = 3 * COLOR_BITS
e = (PIC_SIZE**2)*PIXEL  # 98304

permutations = 2**e
increment = permutations - 2**4895

modulus = 3**62023

a = (modulus >> 1) + 3**5460


def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    else:
        gcd, x, y = extended_gcd(b, a % b)
        return gcd, y, x - (a // b) * y


def modular_inverse(a, m):
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    else:
        return x % m


# Example usage
ainverse = modular_inverse(a, modulus)

shift_1 = int((18/32)*e)  # 55296
shift_2 = int((15/32)*e)  # 46080
shift_3 = int((11/32)*e)  # 33792
shift_4 = int((7/32)*e)  # 21504

mask_one = 2**(int(e/2)-2*1987)
mask_two = 2**(int(e/2)-2*8000)


def encode_lcg(x):
    return (a * x + increment) % modulus


def decode_lcg(x):
    return ainverse * (x - increment) % modulus


# TODO: add masks. small numbers look wack
def encode(x: int):
    # print(f"encode in {x}")
    x = encode_lcg(x)
    # print(f"encode_lcg {x}")
    x ^= (x >> shift_3)
    x ^= ((x % mask_one) << shift_4)
    x ^= ((x % mask_two) << shift_2)
    x ^= (x >> shift_1)
    # print(f"return {x}")

    if x >= permutations:
        x = encode(x)

    return x


def decode(x: int):
    # print(f"decode in {x}")
    x ^= (x >> shift_1)

    rev_x = x ^ ((x % mask_two) << shift_2)
    x = x ^ ((rev_x % mask_two) << shift_2)
    rev_x = x ^ ((x % mask_one) << shift_4)

    rev_x = x ^ ((rev_x % mask_one) << shift_4)
    rev_x = x ^ ((rev_x % mask_one) << shift_4)
    rev_x = x ^ ((rev_x % mask_one) << shift_4)

    x = x ^ ((rev_x % mask_one) << shift_4)
    rev_x = x ^ (x >> shift_3)
    rev_x = x ^ (rev_x >> shift_3)
    x = x ^ (rev_x >> shift_3)
    # print(f"before lcg {x}")
    x = decode_lcg(x)
    # print(f"decode_lcg {x}")

    if x < 0:
        x += modulus
        # print(f"negative {x}")

    if x >= permutations:
        x = decode(x)

    return x


test_value = 100000

next_value = encode(test_value)
last_value = decode(test_value)
lastest_value = decode(last_value)
nextest_value = encode(next_value)

next_of_last = encode(last_value)
last_of_next = decode(next_value)

print("Testing invertibility")
print("=====================")
print(f"Test: {test_value}")
print(f"Next of test: {next_value}")  # random
print(f"Last of test: {last_value}")  # random
print(f"Last of next: {last_of_next}")  # should go back to test_value
print(f"next of last: {next_of_last}")  # should go back to test_value
print(f"next of next: {nextest_value}")  # random
print(f"last of last: {lastest_value}")  # random


# Code for generating Images
def fill_array(arr):
    # Calculate the number of elements needed to reach 4096
    remaining_length = 4096 - len(arr)
    if remaining_length > 0:
        arr[:0] = [[0, 0, 0]] * remaining_length
    else:
        arr = arr[-4096:]
    return arr


# Convert starting int to binary to RGB array
def decimal_to_binary(decimal):
    binary = bin(decimal)[2:]
    binary = ((PIXEL - len(str(binary)) % PIXEL) * "0") + str(binary)
    twenty_four_bit_chunks = [binary[i:i+PIXEL] for i in range(0, len(binary), PIXEL)]
    eight_bit_chunks = [[int(chunk[i:i+COLOR_BITS], 2) for i in range(0, len(chunk), COLOR_BITS)] for chunk in twenty_four_bit_chunks]
    return fill_array(eight_bit_chunks)


# Test generating 2 pictures
first_picture = decimal_to_binary(encode(1))

image = Image.new('RGB', (PIC_SIZE, PIC_SIZE))

# Load the pixel data from the RGB array to the image
for y in range(PIC_SIZE):
    for x in range(PIC_SIZE):
        image.putpixel((x, y), tuple(first_picture[y*PIC_SIZE+x]))

image.save('encoding_1.png')

first_picture = decimal_to_binary(encode(2))

# Create a new image with mode 'RGB' and size 64x64
image = Image.new('RGB', (PIC_SIZE, PIC_SIZE))

# Load the pixel data from the RGB matrix to the image
for y in range(PIC_SIZE):
    for x in range(PIC_SIZE):
        image.putpixel((x, y), tuple(first_picture[y*PIC_SIZE+x]))

image.save('encoding_2.png')


# Generate and save 1000 images into images folder
start = 0
# Uncomment code to enable scaling
SCALE_FACTOR = 3

for i in range(1000):
    encoded = encode(i)
    start = encoded
    picture = decimal_to_binary(encoded)
    # scaled_image = Image.new('RGB', (PIC_SIZE * SCALE_FACTOR, PIC_SIZE * SCALE_FACTOR))
    scaled_image = Image.new('RGB', (PIC_SIZE, PIC_SIZE))

    for y in range(PIC_SIZE):
        for x in range(PIC_SIZE):
            color = tuple(picture[y * PIC_SIZE + x])
            scaled_image.putpixel((x, y), color)
            # Set a 3x3 block of pixels in the new image
            # for dy in range(SCALE_FACTOR):
            #     for dx in range(SCALE_FACTOR):
            #         scaled_image.putpixel((x * SCALE_FACTOR + dx, y * SCALE_FACTOR + dy), color)

    # Save the scaled image
    scaled_image.save(f"images/{i % 1000}_pic.png")


# Converting image to RGB array as the original site has option to look up pictures in database
def image_to_64x64_rgb_array(image_path):
    with Image.open(image_path) as img:
        # Resize the image and convert it to RGB mode
        img = img.resize((64, 64))
        img = img.convert('RGB')

        rgb_array = []
        for y in range(64):
            for x in range(64):
                rgb = img.getpixel((x, y))
                rgb_array.append(rgb)
        return rgb_array


# Convert RGB array to Binary
def rgb_array_to_binary(rgb_array):
    # Ensure the array has 64x64 RGB values
    if len(rgb_array) != 64 * 64:
        raise ValueError("The input array must have exactly 4096 RGB values.")

    # Convert each RGB triplet into an 8-bit binary string and concatenate them
    binary_string = ''.join(f'{r:08b}{g:08b}{b:08b}' for r, g, b in rgb_array)

    return binary_string


# Testing Image to int conversion
image_path = "INSERT PATH HERE"

rgb_array = image_to_64x64_rgb_array(image_path)
binary_result = rgb_array_to_binary(rgb_array)
decimal_result = int(binary_result, 2)
decoded_result = decode(decimal_result)


print(f"Decimal: {decimal_result}")
print(f"Decoded: {decoded_result}")
print(f"Encoded: {encode(decoded_result)}")


# Generating (hopefully) same picture from the decoded number
encoded = encode(decoded_result)
picture = decimal_to_binary(encoded)

scaled_image = Image.new('RGB', (PIC_SIZE * SCALE_FACTOR, PIC_SIZE * SCALE_FACTOR))

for y in range(PIC_SIZE):
    for x in range(PIC_SIZE):
        color = tuple(picture[y * PIC_SIZE + x])
        # Set a 3x3 block of pixels in the new image
        for dy in range(SCALE_FACTOR):
            for dx in range(SCALE_FACTOR):
                scaled_image.putpixel((x * SCALE_FACTOR + dx, y * SCALE_FACTOR + dy), color)

# Save the scaled image
scaled_image.save(f"images/002_pic.png")
