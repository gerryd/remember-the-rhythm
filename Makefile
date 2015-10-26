DESTDIR=
SUBDIR=/usr/lib/rhythmbox/plugins/remember-the-rhythm/
DATADIR=/usr/share/rhythmbox/plugins/remember-the-rhythm/
GLIB_DIR=/usr/share/glib-2.0/schemas/

build:

install:
	install -d $(DESTDIR)$(SUBDIR)
	install -m 644 remember* $(DESTDIR)$(SUBDIR)
	install -d $(DESTDIR)$(DATADIR)/ui
	install -m 644 ui/* $(DESTDIR)$(DATADIR)/ui
	install -d $(DESTDIR)$(GLIB_DIR)
	install -m 644 schemas/org.gnome.rhythmbox.plugins.remember-the-rhythm.gschema.xml $(DESTDIR)$(GLIB_DIR)
