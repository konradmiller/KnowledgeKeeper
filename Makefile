all: prepare
	./kk

prepare:
	./build_ui.sh
	python syncdb.py

clean:
	find . -name "*.pyc" | xargs rm -f
	rm -rf KnowledgeKeeper/forms/ icons_rc.py

distclean: clean
	rm -rf whoosh_index knowledgekeeper.sqlite3
