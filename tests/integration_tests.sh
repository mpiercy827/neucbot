#!/bin/bash
set -e

python3 ./neucbot.py -m Materials/Acrylic.dat -c Chains/Th232Chain.dat -d v2 -o tmp-acrylic-th232-chain.txt
diff tmp-acrylic-th232-chain.txt tests/integration_tests/acrylic-th232-chain.txt
rm tmp-acrylic-th232-chain.txt

python3 ./neucbot.py -m Materials/Acrylic.dat -l AlphaLists/Rn220Alphas.dat -d v2 -o tmp-acrylic-rn220-alphalist.txt
diff tmp-acrylic-rn220-alphalist.txt tests/integration_tests/acrylic-rn220-alphalist.txt
rm tmp-acrylic-rn220-alphalist.txt

python3 ./neucbot.py -m Materials/Acrylic.dat -l AlphaLists/Bi212Alphas.dat -d v2 -o tmp-acrylic-bi212-alphalist.txt
diff tmp-acrylic-bi212-alphalist.txt tests/integration_tests/acrylic-bi212-alphalist.txt
rm tmp-acrylic-bi212-alphalist.txt
