#!/usr/bin/env bash
set -e

mkdir -p ~/.ssh
echo "$HPC_SSH_ID_RSA" > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa

# Avoid host authenticity prompt
echo -e "Host *\n  StrictHostKeyChecking no\n" > ~/.ssh/config

# Start ssh-agent
eval "$(ssh-agent -s)"

# Use SSH_ASKPASS trick to feed passphrase
# ssh-add reads passphrase by calling $SSH_ASKPASS in a no-tty context
export DISPLAY=:0
export SSH_ASKPASS=/tmp/askpass.sh

cat << 'EOF' > $SSH_ASKPASS
#!/usr/bin/env bash
echo "$HPC_SSH_ID_RSA_PASSPHRASE"
EOF
chmod +x $SSH_ASKPASS

# Run ssh-add in a way that forces it to use SSH_ASKPASS
setsid ssh-add ~/.ssh/id_rsa < /dev/null

unset HPC_SSH_ID_RSA_PASSPHRASE