#!/bin/bash

APPDIR=/home/vengle/FlaskProj/Notes
SRCDIR=/home/vengle/projects/Notes
cd $SRCDIR
cp ${SRCDIR}/*.py  $APPDIR
cp ${SRCDIR}/*.sh  $APPDIR
cp ${SRCDIR}/templates/*  $APPDIR/templates
cp -R  ${SRCDIR}/static/*  $APPDIR/static
sudo ${SRCDIR}/restart.sh
