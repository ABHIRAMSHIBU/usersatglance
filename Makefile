PREFIX = /usr/bin
SERVICE_PREFIX = /etc/systemd/system/
install:
	@install uagd.py $(PREFIX)/uagd
	@install uag.py $(PREFIX)/uag
	@install uagread.py $(PREFIX)/uagread
	@install uagd_httpd.py $(PREFIX)/uagd_httpd.py
	cp -v uagd.service $(SERVICE_PREFIX)
	cp -v uagd_httpd.service $(SERVICE_PREFIX)
	sudo useradd -r -M uag