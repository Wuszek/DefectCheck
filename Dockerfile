FROM ubuntu:latest

# install python, wget, pip
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	--no-install-recommends python3 python3-pip git wget unzip && \
	rm -rf /var/lib/apt/lists/*

# install libs for chrome and chrome
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	--no-install-recommends \
	fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 \
    	libcairo2 libcups2 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0 libgtk-3-0 \
    	libgtk-4-1 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 \
    	libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils && \
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
	dpkg -i google-chrome-stable_current_amd64.deb && \
	rm google-chrome-stable_current_amd64.deb && \
	rm -rf /var/lib/apt/lists/*

# clone repo and setup chromedriver
RUN git clone https://git.kobiela.click/wiktor.kobiela/DefectCheck && \
    cd DefectCheck && \
	rm chromedriver.exe && \
	mv chromedriver /usr/local/bin && \
	chmod +x /usr/local/bin/chromedriver && \
	pip3 install -r requirements.txt