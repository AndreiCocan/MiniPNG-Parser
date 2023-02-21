import struct
from PIL import Image
import sys
import math


# Fill the list with 255 or truncate it to be the desired length
def set_list_size(list, target_len):
    return list[:target_len] + [255]*(target_len - len(list))

# Check if 'magic' is the MiniPNG magic number, raise an error if its not the case
def check_magic_word(magic):
    if magic != b'Mini-PNG':
        raise ValueError("Not a MiniPNG file")

# Check to ensure the data obtained from D blocks are consistent with
# the expected number of bytes
def check_num_byte(pixel_type,width,height,bitmap):

    if width<0 or height<0:
        raise ValueError("width and height must be positive") 

    # Calculate the expected number of bytes per scanline based on the bit depth
    match pixel_type:
        case 0:
            bytes_per_scanline = width / 8
        case 1 | 2:
            bytes_per_scanline = width
        case 3:
            bytes_per_scanline = 3*width
        case _:
            raise ValueError("Invalid pixel type")


    # Calculate the expected total number of bytes for the image
    expected_num_bytes = height * bytes_per_scanline

    # Check if the actual number of bytes in the D block matches the expected number of bytes ()
    if len(bitmap) != math.ceil(expected_num_bytes):
        raise ValueError(f"Unexpected number of bytes in D block. Expected {expected_num_bytes}, but got {len(bitmap)}")


# Create the image
def display_image(pixel_type,width,height,bitmap,palette=None):

    if width<0 or height<0:
        raise ValueError("width and height must be positive") 

    # Making sure the palette is not missing in P mode
    if pixel_type == 2 and palette is None:
        raise ValueError("Palette block not found")

    # Because Pillow calculates differently the expected total number of bytes for mode 1 (because of the division by 8),
    # we don't use the library to show it, we instead print it.
    match pixel_type:
        case 0:
            print_b_and_w_image(pixel_type,width,height,bitmap)
            return
        case 1:
            mode = "L"
        case 2:
            mode = "P"
        case 3:
            mode = "RGB"
        case _:
            raise ValueError("Invalid pixel type")

    image = Image.frombytes(mode, (width, height), bitmap)

    # It is necessary to add padding to the palette because Pillow need a list with a size of 768 (256 colors). Thanks to that, if the data 
    # points to an index normaly not found in the palette, it will choose the default color white (thanks to set_list_size that fills it with 255 )
    if mode == "P":
        image.putpalette(set_list_size(palette,768))

    image.show()

# For black-and-white images, iterate over the pixels and print an 'X' for black pixels and a space for white pixels
def print_b_and_w_image(pixel_type,width,height,bitmap):

    if pixel_type != 0 :
        raise ValueError("Not a black and white image")

    if width<0 or height<0:
        raise ValueError("width and height must be positive") 

    for i in range(height):
        for j in range(width):
            pixel = bitmap[i * (width // 8) + j // 8] >> (7 - (j % 8)) & 0x01
            if pixel == 1:
                print(" ", end="")
            else:
                print("X", end="")
        print()

# Pretty print function to display image's metadata
def print_image_infos(pixel_type,width,height,comments,bitmap):
    print("Width = "+ str(width))
    print("Height = "+ str(height))
    print("Pixel Type = "+str(pixel_type))
    print()
    print("Comments = "+  comments.decode())
    print()


# Parse minipng from filename
def parse_minipng(filename):

    header_block = None
    palette = None
    comments = b""
    data_blocks = []

    # Read the file
    with open(filename, "rb") as f:

        # Check if the file is a MiniPNG
        magic = f.read(8)
        check_magic_word(magic)

        # Read the blocks
        while True:
            block_type = f.read(1)
            if block_type == b'':
                break
            block_length_bytes = f.read(4)
            block_length = struct.unpack(">I", block_length_bytes)[0]
            block_content = f.read(block_length)

            match block_type:
                case b'H':
                    header_block = block_content
                case b'P':
                    palette = list(block_content)
                case b'D':
                    data_blocks.append(block_content)
                case b'C':
                    comments+= block_content
                case _ :
                    raise ValueError("Wrong block type")

    # Make sure there is a header block
    if header_block is None:
        raise ValueError("Header block not found")

    # Unpack the header block
    width, height, pixel_type = struct.unpack(">IIB", header_block)
    
    # Concatenate the data blocks to obtain the image bitmap
    bitmap = b''.join(data_blocks)

    # Check the number of bytes in bitmap
    check_num_byte(pixel_type,width,height,bitmap)

    # Print image infos
    print_image_infos(pixel_type,width,height,comments,bitmap)

    # Create and show the image
    display_image(pixel_type,width,height,bitmap,palette)

if __name__=="__main__":
    parse_minipng(sys.argv[1])
