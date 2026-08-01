import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.pdf_parser import PDFParser

def test_pdf_parser():
    parse=PDFParser()
    result=parse.parse("./data/李显鑫_Java_AI开发_17681815141.pdf")

    print(result)
    with open('./tests/a.md','w',encoding='utf-8') as f:
        f.write(result.tables[0]['markdown'])



if __name__=="__main__":
    test_pdf_parser()