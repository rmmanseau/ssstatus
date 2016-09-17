ROOTDIR=${1:-"/"}

mkdir -p "${ROOTDIR}usr/bin/"
mkdir -p "${ROOTDIR}usr/share/bash-completion/completions/"

cp ssstatus.py "${ROOTDIR}usr/bin/ssstatus"
chmod +x "${ROOTDIR}usr/bin/ssstatus"
cp ssstatus-complete.sh "${ROOTDIR}usr/share/bash-completion/completions/ssstatus"
