from click.testing import CliRunner

from tile_stitcher.scripts.cli import cli


def test_cli_exit2():
    runner = CliRunner()
    result = runner.invoke(cli, ['hii'])
    assert result.exit_code == 2
