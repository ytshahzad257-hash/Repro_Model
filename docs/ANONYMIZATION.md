# Anonymous artifact release

For double-blind review, make a clean copy from a committed checkout and remove author names, affiliations, personal email addresses, ORCID identifiers, repository ownership, git metadata, machine-specific absolute paths, and identifying comments. Replace the public repository URL in `CITATION.cff` with a venue-provided anonymous archive URL. Keep the scientific content and generated results unchanged.

The release procedure is:

1. Copy the repository to a new directory.
2. Remove `.git/`, author metadata, and any local logs.
3. Run `python scripts/anonymize_artifact.py <copy>`.
4. Run `python -m pytest -q` and `python experiments/run_all.py --fast` in the copy.
5. Inspect `docs/`, `README.md`, generated metadata, and container files for personal paths.

The procedure does not modify the main repository.
