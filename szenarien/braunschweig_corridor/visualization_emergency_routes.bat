C:\Python27\python "%SUMO_HOME%\tools\route\route2poly.py" sirene.net.xml sirene_emergency.rou.xml -o sirene_emergency_rou.poly.xml 

sumo-gui -n sirene.net.xml -a sirene_emergency_rou.poly.xml