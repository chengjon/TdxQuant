from tdxquant.cli import build_parser


def test_parser_accepts_pingan_hid_submit_probe() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "pingan-hid-submit-probe",
            "--port",
            "COM3",
            "--hid-pre-delay",
            "3",
            "--code",
            "000001",
            "--price",
            "10.00",
            "--quantity",
            "100",
        ]
    )
    assert args.command == "pingan-hid-submit-probe"
    assert args.submit_mode == "button_enter"
    assert args.hid_pre_delay == 3
