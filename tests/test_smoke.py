from beads_lab import main


def test_main_runs(capsys) -> None:
    main()
    assert "Hello from beads-lab!" in capsys.readouterr().out
