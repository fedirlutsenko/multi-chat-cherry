### Usage(GNU/Linux macOS Windows):
 - [Install docker](https://docs.docker.com/engine/installation/)
 - `docker run -d --name x11-bridge -e MODE="html" -p 10000:10000 -e XPRA_DISPLAY=:14 -e XPRA_PASSWORD=<PASSWORD> jare/x11-bridge`
 - `docker run -d --name chat -p 8080:8080 -v <PATH_TO_CONFIG>:/usr/lib/python2.7/site-packages/LalkaChat/conf deforce/lalkachat`
 - Open chat config at `http://localhost:10000/index.html?encoding=png&password=<PASSWORD>`
 - And chat window at `http://localhost:8080/`
 - You can update the chat with `docker rmi -f czt/lalkachat`
 - Remove containers with `docker rmi -f x11-bridge chat`


#### Production docker build:

 - `docker build -t deforce/alpine-wxpython:latest docker/Dockerfiles/alpine-wxpython`
 - `docker build -t deforce/lalkachat:latest .`

