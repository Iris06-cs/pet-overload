import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const questionsSlice = createSlice({
    name: 'questions',
    initialState: {
        allQuestions: [],
        error: null,
        displayedQuestions: [],
    },
    reducers: {
        sortQuestionsByNewest(state) {
            state.displayedQuestions = [...state.allQuestions].sort((a, b) => {
                return new Date(b.created_at) - new Date(a.created_at);
            });
        },
        sortQuestionsByScore(state) {
            state.displayedQuestions = [...state.allQuestions].sort((a, b) => {
                return b.votes_score - a.votes_score;
            });
        },
        filterQuestionsByUnanswered(state) {
            state.displayedQuestions = state.allQuestions.filter(
                (question) => question.answers_count === 0
            );
        },
        updateQuestionAfterVote(state, action) {
            const updatedQuestion = action.payload;
            const idx = state.allQuestions.findIndex(
                (question) => question.id === updatedQuestion.id
            );
            state.allQuestions[idx] = updatedQuestion;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(getAllQuestions.fulfilled, (state, action) => {
                state.allQuestions = action.payload;
                state.error = null;
                state.displayedQuestions = action.payload;
            })
            .addCase(getAllQuestions.rejected, (state, action) => {})
            .addCase(deleteQuestion.fulfilled, (state, action) => {
                state.loading = false;
                state.allQuestions = state.allQuestions.filter(
                    (vote) => vote.id === action.payload
                );
                state.error = null;
            })

            .addCase(deleteQuestion.rejected, (state, action) => {
                console.log('Rejected with value:', action.payload);
                state.loading = false;
                state.error = action.payload.error;
            })
            .addCase(filterQuestions.fulfilled, (state, action) => {
                state.loading = false;
                state.allQuestions = [...action.payload];
                state.error = null;
            })
            .addCase(filterQuestions.rejected, (state, action) => {
                console.log('Rejected with value:', action.payload);
                state.loading = false;
                state.error = action.payload.error;
            });

//duplicate?
            //.addCase(deleteQuestion.rejected, (state, action) => {});

    },
});

export const getAllQuestions = createAsyncThunk(
    'questions/getAllQuestions',
    async (_, { rejectWithValue }) => {
        const response = await fetch('/api/questions/', {
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (!response.ok) {
            return rejectWithValue(await response.json());

        }

        return data.questions;
    }
);

export const filterQuestions = createAsyncThunk(
    'questions/filterQuestions',
    async (parameter, { rejectWithValue }) => {
        const response = await fetch(`/api/questions${parameter}`);
        if (!response.ok) {
            return rejectWithValue(await response.json());
        }
        const data = await response.json();
        console.log('data:', data);

        return data.questions;
    }
);
//duplicate?
//export const deleteQustion = createAsyncThunk(


export const deleteQuestion = createAsyncThunk(
    'questions/deleteQuestion',
    async (questionId, { rejectWithValue }) => {
        const response = await fetch(`/api/questions/${questionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errData = await response.json();

            return rejectWithValue(errData);
        }

        return questionId;
    }
);

export const {
    sortQuestionsByNewest,
    sortQuestionsByScore,
    filterQuestionsByUnanswered,
    updateQuestionAfterVote,
} = questionsSlice.actions;

export default questionsSlice.reducer;
