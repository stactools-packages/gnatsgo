from stactools.testing import CliTestCase

from stactools.gnatsgo.commands import create_gnatsgo_command


class CommandsTest(CliTestCase):

    def create_subcommand_functions(self):
        return [create_gnatsgo_command]
