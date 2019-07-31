To build kumodd.exe for windows, one options to install the [Chocolatey package
manager](https://chocolatey.org/docs/installation), and then:

``` shell
choco update -y python git
git clone https://github.com/rich-murphey/kumodd.git
cd kumodd
pip install -r requirements.txt
pip install pyinstaller 
pyinstaller -F kumodd
```

To get debug logs to stdout, set 'log_to_stdout: True' in config.yml.

