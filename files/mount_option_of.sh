#!/bin/sh
#
# mount_option_of mount_point
#
# prints comma-separated mount(8) options of mount_point

mount | grep -e " \\$1 " | sed -e "s/.*(//" -e "s/)//" -e "s/local, //"
