echo "Uninstalling Antenna Toolkit......."
sleep 3

rm -rf ${HOME}/.local/share/applications/ansys_antenna_toolkit.desktop
rm -rf ${HOME}/.local/usr/share/doc/ansys-antenna_toolkit

rm -rf ${HOME}/.local/opt/ansys_antenna_toolkit

sed -i '/# Add alias for Ansys Antenna Toolkit/d' ~/.bashrc
sed -i  '/alias  ansys_antenna_toolkit/d' ~/.bashrc