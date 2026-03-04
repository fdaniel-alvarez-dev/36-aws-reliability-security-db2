.PHONY: setup demo test clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

demo:
	. .venv/bin/activate && python pipelines/pipeline.py

test:
	. .venv/bin/activate && pytest -q

clean:
	rm -rf .venv data/processed
