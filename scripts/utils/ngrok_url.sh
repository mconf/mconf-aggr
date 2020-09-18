curl --silent http://127.0.0.1:4040/api/tunnels | jq '.tunnels[0].public_url' | sed -e 's/^"//' -e 's/"$//'
