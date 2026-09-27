.PHONY: test reproduce fast clean

test:
	python -m pytest -q

fast:
	python experiments/run_all.py --fast

reproduce:
	python experiments/run_all.py

clean:
	python -c "from pathlib import Path; [p.unlink() for p in Path('results/generated').rglob('*') if p.is_file()]; [p.unlink() for p in Path('figures/generated').rglob('*') if p.is_file()]"
