#!/bin/sh

# Decrypt the file
mkdir -p $HOME/secrets
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$SECRET_PASSPHRASE" \
--output $HOME/secrets/facebook.com_cookies.txt facebook.com_cookies.txt.gpg