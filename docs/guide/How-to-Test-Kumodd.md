# Testing Kumodd

To test the validity of kumodd itself, use the Following regression test. The test data
are freely redistributable files are taken from the Govdocs1 forensic corpus [Garfinkel,
2009] [Digital Corpora](https://digitalcorpora.org/corpora/files) publishes both the
file and a catalog of MD5 values.  The selected files are shown below.

    md5sum -b *
    a152337c66a35ac51dda8603011ffc7d *389815.html
    0fe512e8859726eebb2111b127a59719 *435465.pdf
    7221db70bf7868cd5c3ed5c33acda132 *520616.ppt
    f679e5e66d3451fbb2d7a0ff56b28938 *594891.xml
    e3f7976dff0637c80abaf5dc3a41c3d8 *607528.csv
    c92ff79d722bc9a486c020467d7cb0f9 *766091.jpg
    0711edc544c47da874b6e4a6758dc5e6 *838629.txt
    3fc66ab468cb567755edbe392e676844 *939202.doc
    6f1d791aeca25495a939b87fcb17f1bd *985500.gif
    207dcccbd17410f86d56ab3bc9c28281 *991080.xls

Make sure the option "Convert uploaded files to Google Docs editor format" should not be
checked in Google Drive's Settings; otherwise, the files will be converted during
upload, the MD5 values will change, and the test will fail.  Drag the test folder into
google drive. Then, download the folder with Kumodd, for example using the options: -f
test to select the test folder, -d all to download all file types, and -col test to
select the MD5, status and file name columns.


    kumodd -f test -d all -col test
    MD5 of File                      Status  Name
    a152337c66a35ac51dda8603011ffc7d valid   389815.html
    0fe512e8859726eebb2111b127a59719 valid   435465.pdf
    7221db70bf7868cd5c3ed5c33acda132 valid   520616.ppt
    f679e5e66d3451fbb2d7a0ff56b28938 valid   594891.xml
    e3f7976dff0637c80abaf5dc3a41c3d8 valid   607528.csv
    c92ff79d722bc9a486c020467d7cb0f9 valid   766091.jpg
    0711edc544c47da874b6e4a6758dc5e6 valid   838629.txt
    3fc66ab468cb567755edbe392e676844 valid   939202.doc
    6f1d791aeca25495a939b87fcb17f1bd valid   985500.gif
    207dcccbd17410f86d56ab3bc9c28281 valid   991080.xls

If kumodd generates the above output exactly, it is functioning correctly.

If you want more extensive testing, [the t5 corpus](http://roussev.net/t5/t5.html) a
larger cross section of small files from the Govdocs1 data sets. It contains 4,457 html,
pdf, text, doc, ppt, jpg, xls, and gif files, in 1.9GB of data, 1.2GB compressed.
vassil@s.uno.edu
