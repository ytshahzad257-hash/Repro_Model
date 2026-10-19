.PHONY: test reproduce fast clean

test:
	python -m pytest -q

fast:
	python experiments/run_all.py --fast

reproduce:
	python experiments/run_all.py

clean:
	python -c "from pathlib import Path; import shutil; [shutil.rmtree(p) for p in Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache',ignore_errors=True)"
