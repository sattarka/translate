# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pytest import importorskip

from translate.convert import po2ini, test_convert
from translate.misc import wStringIO
from translate.storage import po


importorskip("iniparse")


class TestPO2Ini(object):

    def _convert(self, posource, inisource, dialect="default"):
        """Helper that converts PO to format without files."""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        templatefile = wStringIO.StringIO(inisource)
        convertor = po2ini.po2ini(templatefile, inputpo, dialect=dialect)
        outputini = convertor.convertstore()
        return outputini

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        posource = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        initemplate = """[section]
prop=value
"""
        iniexpected = """[section]
prop=waarde
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_space_preservation(self):
        """check that we preserve any spacing in ini files when merging"""
        posource = """#: [section]prop
msgid "value"
msgstr "waarde"
"""
        initemplate = """[section]
prop  =  value
"""
        iniexpected = """[section]
prop  =  waarde
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        posource = r"""#: [section]accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""
"""
        initemplate = """[section]
accesskey-accept=
"""
        iniexpected = """[section]
accesskey-accept=
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_merging_fuzzy(self):
        """check merging a fuzzy translation"""
        posource = """#: [section]prop
#, fuzzy
msgid "value"
msgstr "waarde"
"""
        initemplate = """[section]
prop=value
"""
        iniexpected = """[section]
prop=value
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_merging_propertyless_template(self):
        """check that when merging with a template with no ini values that we copy the template"""
        posource = ""
        initemplate = """# A comment
"""
        iniexpected = initemplate
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_empty_value(self):
        """test that we handle an value in translation that is missing in the template"""
        posource = """#: [section]key
msgctxt "key"
msgid ""
msgstr "translated"
"""
        initemplate = """[section]
key =
"""
        iniexpected = """[section]
key =translated
"""
        inifile = self._convert(posource, initemplate)
        assert inifile == iniexpected

    def test_dialects_inno(self):
        """test that we output correctly for Inno files."""
        posource = r"""#: [section]prop
msgid "value\tvalue2\n"
msgstr "ṽḁḽṻḝ\tṽḁḽṻḝ2\n"
"""
        initemplate = """[section]
prop  =  value%tvalue%n
"""
        iniexpected = """[section]
prop  =  ṽḁḽṻḝ%tṽḁḽṻḝ2%n
"""
        inifile = self._convert(posource, initemplate, "inno").decode('utf-8')
        assert inifile == iniexpected


class TestPO2IniCommand(test_convert.TestConvertCommand, TestPO2Ini):
    """Tests running actual po2ini commands on files"""
    convertmodule = po2ini
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)
