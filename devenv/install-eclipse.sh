#!/bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEMPDIR="$(mktemp -d)"

echo -n 'Downloading Eclipse installer ...'
wget -q -O$TEMPDIR/eclipse-installer.tar.gz 'http://eclipse.mirror.wearetriple.com//oomph/products/eclipse-inst-linux64.tar.gz'
echo ' done'

echo -n 'Extracting installer ...'
tar -x -C $TEMPDIR -f $TEMPDIR/eclipse-installer.tar.gz
echo ' done'

echo 'Starting installation process ...'
$TEMPDIR/eclipse-installer/eclipse-inst -vmargs "-Doomph.redirection.setups=http://git.eclipse.org/c/oomph/org.eclipse.oomph.git/plain/setups/->$THIS_DIR/eclipse-setups/"


rm -r $TEMPDIR
