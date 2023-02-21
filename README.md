# MiniPNG Parser

**A miniPNG parser written in `python 3.10`**

**Make sure to install the requirements. The programe uses `Pillow`, a fork of PIL (Python Imaging Library) to display the images (except for black and white ones wich are printed directly in the terminal).**

## Getting Started
```bash
git clone https://github.com/AndreiCocan/MiniPNG-Parser
cd MiniPNG-Parser
python3 -m pip install -r requirements.txt
```
```bash
python3 -m miniPNG_parser.py <YOUR .mp FILE HERE>
```

## MiniPNG

A MiniPNG image starts with a magic number (the 8 bytes representing the `Mini-PNG` string), followed by `blocks`. Each of this block follows the following format:

| Offset         | Field Name     | Field Size     |Field Description |
|:--------------:|:--------------:|:--------------:|:--------------:|
|0| Block Type| 1 byte| A character identifying the block type|
|1 |Block Length| 4 bytes| An integer indicating the size l of the block content|
|5 |Block Content| l bytes| The content of the block, which is type-dependent|

First, let us describe the blocks required for a MiniPNG image:
* A Header block (type H)
* Zero, one or more Comment blocks (type C)
* A Palette block (type P)
* One or more Data blocks (type D)

### Block H Description
The content of the H block is the following:

| Offset         | Field Name     | Field Size     |Field Description |
|:--------------:|:--------------:|:--------------:|:--------------:|
|0| Image Width| 4 bytes| An integer describing the width in pixels|
|4 |Image Height |4 bytes| An integer describing the height in pixels|
|8 |Pixel Type| 1 byte| 0 = black-and-white, 1 = gray levels, 2 = palette, 3 = 24 bits colors|

### Block C Description
The content of Comment blocks is simply a character string composed of displayable ASCII chars.\

### Block D Description
The content of data blocks must be concatenated to obtain the image bitmap.
With black-and-white pixels, each pixel is encoded as a bit (0 means black, 1 means white). Other pixel
types can be ignored for the moment. Pixels are stored from top to bottom, then left to right.

### Block P Description
To save space, if your image uses only a limited set of colors, you can use a palette to describe up to 256 colors.
To this aim, we use a new block type, P, which contains n RGB entries, each one encoded on 3 bytes.
The frst entry will be the 0 entry, and each pixel in the bitmap will be represented by a byte, which is the index of the color entry.
