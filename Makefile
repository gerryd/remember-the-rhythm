PLUGIN_PATH=/usr/lib/rhythmbox/plugins/remember-the-rhythm
DATA_PATH=/usr/share/rhythmbox/plugins/remember-the-rhythm
SCHEMA_PATH=/usr/share/glib-2.0/schemas/

build:

install:
	mkdir -p $(PLUGIN_PATH)
	cp remember* $(PLUGIN_PATH)
	mkdir -p $(DATA_PATH)/ui
	cp ui/* $(DATA_PATH)/ui
	cp schemas/org.gnome.rhythmbox.plugins.remember-the-rhythm.gschema.xml $(SCHEMA_PATH)
	glib-compile-schemas $(SCHEMA_PATH)
	
uninstall:
	rm -Rf $(PLUGIN_PATH)
	rm -Rf $(DATA_PATH)
	rm $(SCHEMA_PATH)org.gnome.rhythmbox.plugins.remember-the-rhythm.gschema.xml 
	glib-compile-schemas $(SCHEMA_PATH)
