cd /home/stackone/stackone/
if [ -e /home/stackone/stackone/installed ]; then
        echo "Already installed"
        rm -r /home/stackone/stackone/setup-stackone
else
        ./setup-esage
        touch /home/stackone/stackone/installed
fi
cd /home/stackone/stackone/
./start-stackone
