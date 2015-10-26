PLUGIN_PATH=/usr/lib/rhythmbox/plugins/remember-the-rhythm/
DATA_PATH=/usr/share/rhythmbox/plugins/remember-the-rhythm/
SCHEMA_PATH=/usr/share/glib-2.0/schemas/

build:

install:
	install -d $(PLUGIN_PATH)
	install -m 644 remember* $(PLUGIN_PATH)
	install -d $(DATA_PATH)/ui
	install -m 644 ui/* $(DATA_PATH)/ui
	install -d $(SCHEMA_PATH)
	install -m 644 schemas/org.gnome.rhythmbox.plugins.remember-the-rhythm.gschema.xml $(SCHEMA_PATH)
