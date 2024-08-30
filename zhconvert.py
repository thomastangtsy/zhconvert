#!/usr/bin/env python3

from argparse import ArgumentParser
from enum import Enum
import json
from pathlib import Path
import requests


ZHCONVERT_PY_VERSION = "0.1"
ZHCONVERT_ZPI_ENDPOINT = "https://api.zhconvert.org"

ConverterType = ("Simplified", "Traditional", "China", "Hongkong", "Taiwan", "Pinyin", "Bopomofo", "Mars", "WikiSimplified", "WikiTraditional")

def read_file(file: Path, encoding="utf-8"):
  f = open(file, "r", encoding=encoding)
  content = f.read()
  f.close()
  return content


def save_file(file: Path, content):
  f = open(file, "w", encoding="utf-8")
  f.write(content)
  f.close()


def convert(converter: str, content: str):
  headers = {
    "content-type": "application/json"
  }
  body = {
    "converter": converter,
    "text": content
  }

  r = requests.post(f"{ZHCONVERT_ZPI_ENDPOINT}/convert", headers=headers,data=json.dumps(body))
  response = r.json()

  return response["data"]["text"]


def main():
  parser = ArgumentParser(prog="zhconvert", description="Translate between traditional and simplified Chinese, and localization.")
  parser.add_argument("-v", "--version", action="version", version=ZHCONVERT_PY_VERSION)
  parser.add_argument("-c", "--converter", metavar="CONVERTER",choices=ConverterType, default="Traditional", dest="converter", help="The converter to use. (default: Traditional)\n(Available converter: {})".format(', '.join(ConverterType)))
  parser.add_argument("-e", "--encoding", metavar="ENCODING", default="utf-8", dest="encoding", help="Input file encoding. (default: utf-8)")
  parser.add_argument("-f", "--force", action="store_true", default=False, dest="overwrite", help="Force overwrite output file")
  parser.add_argument("-o", "--output-dir", metavar="DIR", dest="output_dir", required=True, help="Output directory.")
  parser.add_argument("file", nargs="+", help="at least one input file.")
  
  args = vars(parser.parse_args())

  outputPath = Path(args["output_dir"])
  if not args["output_dir"] and not outputPath.is_dir:
    print("Error: output directory does not exist or not a directory")
    exit(2)
  
  for file in args["file"]:
    filePath = Path(file)
    outputFilePath = outputPath.joinpath(filePath.name)

    
    if not filePath.exists():
      print(f"Error: {file}: No such file")
      exit(2)
    elif not filePath.is_file():
      print(f"Error: {file}: Not a file")
      exit(2)
    elif not args["overwrite"] and outputFilePath.exists():
      print(f"Error: cannot output to {outputFilePath}: already exists")
      exit(2)
    elif args["overwrite"] and not outputFilePath.is_file():
      print(f"Error: cannot overwrite {outputFilePath}: not a file")
      exit(2)

    print(f"Processing {filePath}... ", end="")
    
    try:
      content = read_file(filePath, encoding=args["encoding"])
      converted_content = convert(args["converter"], content)
      save_file(outputFilePath, converted_content)
    except Exception as e:
      print(f"Error when processsing '{filePath}': ", e)
      exit(4)
    
    print("Done")
    print(f"Written to {outputFilePath}")
  

if __name__ == "__main__":
  main()
