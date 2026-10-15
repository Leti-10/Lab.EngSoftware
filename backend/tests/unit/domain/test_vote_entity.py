import pytest

from src.domain.entities import Vote
from src.domain.enums.enums import VoteTarget
from src.domain.exceptions import (
    InvalidVoteStatusError,
    InvalidVoteTargetError,
    InvalidVoteUserError,
)


def test_vote_accepts_valid_data_and_converts_target_entity():
    vote = Vote(
        status="like",
        target_entity="books",
        target_id=3,
        user_id=1,
    )

    assert vote.target_entity is VoteTarget.BOOK


@pytest.mark.parametrize("status", ["", "   "])
def test_vote_rejects_blank_status(status):
    with pytest.raises(InvalidVoteStatusError):
        Vote(status=status, target_entity="books", target_id=3, user_id=1)


def test_vote_rejects_unknown_target_entity():
    with pytest.raises(InvalidVoteTargetError):
        Vote(status="like", target_entity="authors", target_id=3, user_id=1)


def test_vote_rejects_non_positive_target_id():
    with pytest.raises(InvalidVoteTargetError):
        Vote(status="like", target_entity="books", target_id=0, user_id=1)


def test_vote_rejects_non_positive_user_id():
    with pytest.raises(InvalidVoteUserError):
        Vote(status="like", target_entity="books", target_id=3, user_id=0)
