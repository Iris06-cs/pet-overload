import { useDispatch, useSelector } from 'react-redux';
import { useEffect, useRef, useState } from 'react';
import {
    selectVoteStatus,
    deleteQuestionVoteById,
    updateQuestionVoteById,
    createQuestionVote,
} from '../../../store/questionVotes';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { updateQuestionAfterVote } from '../../../store/questions';

const Voting = ({ questionId, voteScore }) => {
    const [currentVoteScore, setCurrentVoteScore] = useState(voteScore);

    const upvoteArrowRef = useRef(null);
    const downvoteArrowRef = useRef(null);
    const currentVote = useSelector((state) =>
        selectVoteStatus(state.questionVotes, questionId)
    );
    const voteType = {
        UPVOTE: 1,
        DOWNVOTE: -1,
        NO_VOTE: 0,
    };
    const dispatch = useDispatch();
    const [currentVoteType, setCurrentVoteType] = useState(
        currentVote ? currentVote.vote_status : voteType.NO_VOTE
    );

    useEffect(() => {
        setCurrentVoteType(
            currentVote
                ? currentVote.isLiked
                    ? voteType.UPVOTE
                    : voteType.DOWNVOTE
                : voteType.NO_VOTE
        );
    }, [currentVote]);
    useEffect(() => {
        if (currentVoteType === voteType.UPVOTE) {
            upvoteArrowRef.current.classList.add('selected');
            downvoteArrowRef.current.classList.remove('selected');
        } else if (currentVoteType === voteType.DOWNVOTE) {
            downvoteArrowRef.current.classList.add('selected');
            upvoteArrowRef.current.classList.remove('selected');
        } else {
            upvoteArrowRef.current.classList.remove('selected');
            downvoteArrowRef.current.classList.remove('selected');
        }
    }, [currentVoteType]);
    const handleVoteArrowClick = async (arrowRef) => {
        const { current } = arrowRef;
        const { UPVOTE, DOWNVOTE, NO_VOTE } = voteType;

        current.classList.add('fa-beat');
        setTimeout(() => current.classList.remove('fa-beat'), 800);

        const voteTypeClicked = current.classList.contains('upvote-arrow')
            ? UPVOTE
            : DOWNVOTE;

        const updateVoteScore = (updatedQuestion) => {
            dispatch(updateQuestionAfterVote(updatedQuestion));
            setCurrentVoteScore(updatedQuestion.votes_score);
        };

        if (!currentVote || currentVote.voteStatus === NO_VOTE) {
            const questionVote = await dispatch(
                createQuestionVote(
                    { questionId: questionId, isLiked: voteTypeClicked },
                    voteTypeClicked
                )
            );
            updateVoteScore(questionVote.payload.question);
        } else if (currentVoteType === voteTypeClicked) {
            dispatch(
                deleteQuestionVoteById({ questionVoteId: currentVote.id })
            );
            setCurrentVoteScore(
                currentVoteScore + (voteTypeClicked === UPVOTE ? -1 : 1)
            );
        } else {
            const updatedQuestionVote = await dispatch(
                updateQuestionVoteById(
                    {
                        questionVoteId: currentVote.id,
                        isLiked: voteTypeClicked,
                    },
                    voteTypeClicked
                )
            );
            updateVoteScore(updatedQuestionVote.payload.question);
        }
    };
    return (
        <div className="voting-score">
            <FontAwesomeIcon
                className="upvote-arrow"
                icon="fa-up-long"
                ref={upvoteArrowRef}
                onClick={() => handleVoteArrowClick(upvoteArrowRef)}
            />
            <p className="voting-score-value">{currentVoteScore}</p>
            <FontAwesomeIcon
                className="downvote-arrow"
                icon="fa-down-long"
                ref={downvoteArrowRef}
                onClick={() => handleVoteArrowClick(downvoteArrowRef)}
            />
        </div>
    );
};

export default Voting;
