Feel free to contribute to this project by opening new PRs in this repository.

At the time of writing, March 2021, there is no GitHub hook to automatically test and check new code.

Please, make sure code keeps on passing `tox` and `mypy` checks, e.g.:

```
$ tox
  isort: commands succeeded
  black: commands succeeded
  flake8: commands succeeded
  congratulations :)

$ mypy gray_merchant_of_billund
Success: no issues found in 31 source files

```
