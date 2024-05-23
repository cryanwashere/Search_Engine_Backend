apt install python3.11-venv
python3 -m venv /home/env
source /home/env/bin/activate

apt install sshfs
mkdir /home/sshfs_volume
sudo sshfs -o allow_other,default_permissions root@138.68.149.96:/home/volume /home/sshfs_volume