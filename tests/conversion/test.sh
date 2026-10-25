#!/usr/bin/env bash
./compiler.py singlechapter in="./tests/conversion/files" out="./tests/results/conversion.pdf" overwrite_duplicate
pdfimages -list ./tests/results/conversion.pdf
