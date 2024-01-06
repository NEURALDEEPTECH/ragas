from __future__ import annotations


def test_add_userid():
    from ragas._analytics import EvaluationEvent

    evaluation_event = EvaluationEvent(
        event_type="evaluation", metrics=["harmfulness"], num_rows=1, evaluation_mode=""
    )
    payload = evaluation_event.__dict__
    assert payload.get("user_id") is not None


def setup_user_id_filepath(tmp_path, monkeypatch):
    # setup
    def user_data_dir_patch(appname, roaming=True) -> str:
        return str(tmp_path / appname)

    import ragas._analytics
    from ragas._analytics import USER_DATA_DIR_NAME

    monkeypatch.setattr(ragas._analytics, "user_data_dir", user_data_dir_patch)
    userid_filepath = tmp_path / USER_DATA_DIR_NAME / "uuid.json"

    return userid_filepath


def test_write_to_file(tmp_path, monkeypatch):
    userid_filepath = setup_user_id_filepath(tmp_path, monkeypatch)

    # check if file created if not existing
    assert not userid_filepath.exists()
    from ragas._analytics import get_userid
    import json

    userid = get_userid()
    assert userid_filepath.exists()
    with open(userid_filepath, "r") as f:
        assert userid == json.load(f)["userid"]

    assert not (tmp_path / "uuid.json").exists()

    # del file and check if LRU cache is working
    userid_filepath.unlink()
    assert not userid_filepath.exists()
    userid_cached = get_userid()
    assert userid == userid_cached


def test_load_userid_from_json_file(tmp_path, monkeypatch):
    userid_filepath = setup_user_id_filepath(tmp_path, monkeypatch)
    assert not userid_filepath.exists()

    # create uuid.json file
    userid_filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(userid_filepath, "w") as f:
        import json

        json.dump({"userid": "test-userid"}, f)

    from ragas._analytics import get_userid

    # clear LRU cache since its created in setup for the above test
    get_userid.cache_clear()

    assert get_userid() == "test-userid"