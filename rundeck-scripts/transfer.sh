#!/bin/bash
set -e
source "$(dirname $0)/functions"

exec python3 $INSTALL_DIR/scripts/transfer.py -p "$RD_OPTION_PRIVATE_KEY" -a "$RD_OPTION_AMOUNT" -r "$RD_OPTION_RECEIVER"
