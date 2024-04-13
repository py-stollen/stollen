
package_dir := stollen
examples_dir := examples
code_dir := $(package_dir) $(examples_dir)

.PHONY: lint
lint:
	@black --check --diff $(code_dir)
	@ruff check $(code_dir)
	@mypy --strict $(code_dir)

.PHONY: reformat
reformat:
	@black $(code_dir)
	@ruff check $(code_dir) --fix
