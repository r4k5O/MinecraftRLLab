$ErrorActionPreference = 'Stop'
python -m unittest discover -s client/tests -p 'test_*.py' -v
python -m unittest discover -s tools/tests -p 'test_*.py' -v
gradle :plugin:runTests :plugin:jar --console=plain
python tools/build_client.py --output dist
