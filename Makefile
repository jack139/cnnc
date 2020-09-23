PY = python2.7 -m compileall -q -f
JAVA = java -jar yuicompressor-2.4.8.jar

CONFIG = config

SRC = src
SRC_CONF = $(SRC)/$(CONFIG)

JS_PATH=static/js/wx/
JS_FILES=cate doct2 ui_helper tnm_cate tnm_page tnm_helper

TARGETS = cnnc
TARGET_CONF = $(TARGETS)/$(CONFIG)

all: clean $(TARGETS)

$(TARGETS):
	cp -r $(SRC) $(TARGETS)
	-$(PY) $(TARGETS)
	find $(TARGETS) -name '*.py' -delete
	rm $(TARGET_CONF)/setting.pyc
	cp $(SRC_CONF)/setting.py $(TARGET_CONF)

js:
	@for c in $(JS_FILES); do \
		echo "compressing $$c ..."; \
		$(JAVA) $(JS_PATH)$$c.js > $(JS_PATH)$$c.min.js; \
	done

clean: 
	rm -rf $(TARGETS)
