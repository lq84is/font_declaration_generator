import sys
from fontTools.ttLib import TTFont

def unicode_to_c_literal(unicode_code):
    if unicode_code <= 0xFFFF:
        return "\\u{:04x}".format(unicode_code)
    else:
        return "\\U{:08x}".format(unicode_code)

def generate_header_file(font_path):
    font = TTFont(font_path)
    font_name = font_path.split("/")[-1].split(".")[0].replace(" ", "_").replace("-", "_")
    output_file = f"{font_name}_definitions.h"

    with open(output_file, "w") as file:
        file.write("#ifndef {0}_H\n".format(font_name.upper()))
        file.write("#define {0}_H\n\n".format(font_name.upper()))

        for table in font['cmap'].tables:
            for key, value in table.cmap.items():
                symbol_name = value.replace(" ", "_").replace("-", "_").replace(".", "_").upper()
                
                if not value or "ZERO_WIDTH_SPACE" in symbol_name:  
                    continue

                unicode_val = format(key, 'X')
                c_literal = unicode_to_c_literal(key)

                try:
                    file.write("#if !defined(LV_SYMBOL_{0})\n".format(symbol_name))
                    file.write("  #define LV_SYMBOL_{0}         \"{1}\" /*{2}, 0x{3}*/\n".format(symbol_name, c_literal, key, unicode_val))
                    file.write("#endif\n\n")
                except Exception as e:
                    print(f"Error writing symbol: {symbol_name} (Unicode: {key}, C Literal: {c_literal})")
                    print("Error:", e)
                    break

        file.write("#endif // {0}_H\n".format(font_name.upper()))
    
    print(f"Header file generated: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Takes all symbols with names from font file and places them to .h file. ")
        print("Usage: python3 script.py fontfile.ttf")
        sys.exit(1)

    font_path = sys.argv[1]
    generate_header_file(font_path)
