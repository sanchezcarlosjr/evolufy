activate:
	micromamba activate evolufy

activate:
	micromamba activate evolufy

install:
	micromamba env export -n evolufy -f environment.lock.yml
	micromamba activate evolufy