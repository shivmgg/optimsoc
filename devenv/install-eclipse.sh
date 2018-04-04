#!/bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEMPDIR="$(mktemp -d)"

INSTALLER_URL='http://www.eclipse.org/downloads/download.php?file=/oomph/products/eclipse-inst-linux64.tar.gz&r=1'

echo -n 'Downloading Eclipse installer ...'
curl -Ls -o $TEMPDIR/eclipse-installer.tar.gz "$INSTALLER_URL"
echo ' done'

echo -n 'Extracting installer ...'
tar -x -C $TEMPDIR -f $TEMPDIR/eclipse-installer.tar.gz
echo ' done'

echo 'Starting installation process ...'
$TEMPDIR/eclipse-installer/eclipse-inst -vmargs "-Doomph.redirection.setups=http://git.eclipse.org/c/oomph/org.eclipse.oomph.git/plain/setups/->$THIS_DIR/eclipse-setups/"


rm -r $TEMPDIR
