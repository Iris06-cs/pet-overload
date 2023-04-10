import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const answerSlice = createSlice({
    name: 'answers',
    initialState: {
        allAnswers: [],
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(getAllAnswers.fulfilled, (state, action) => {
                state.allAnswers = action.payload;
            })
            .addCase(getAllAnswers.rejected, (state, action) => {
                console.log('Rejected with value:', action.payload);
            })
            .addCase(deleteAnswer.fulfilled, (state, action) => {
                state.loading = false;
                state.allAnswers = state.allAnswers.filter(
                    (vote) => vote.id === action.payload
                );
            })
            .addCase(deleteAnswer.rejected, (state, action) => {
                console.log('Rejected with value:', action.payload);
                state.loading = false;
            });
    },
});

export const getAllAnswers = createAsyncThunk(
    'answers/getAllAnswers',
    async (_, { rejectWithValue }) => {
        const response = await fetch('/api/answers/', {
            headers: {
                'Content-Type': 'application/json',
            },
            //source of bug
            // credentials: 'include',
        });

        if (!response.ok) {
            rejectWithValue(await response.json());
        }
        const data = await response.json();
        console.log('data', data);
        return data.Answers;
    }
);

export const getAnswersByQuestion = createAsyncThunk(
    'answers/getAnswersByQuestion',
    async (questionId, { rejectWithValue }) => {
        const response = await fetch(`/api/questions/${questionId}/answers`, {
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            rejectWithValue(await response.json());
        }

        const data = await response.json();
        console.log(`Answers to question ${questionId}`, data.answers);

        return data.answers;
    }
);
export const deleteAnswer = createAsyncThunk(
    'answers/deleteAnswer',
    async (answerId, { rejectWithValue }) => {
        const response = await fetch(`/api/answers/${answerId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            const errData = await response.json();
            return rejectWithValue(errData);
        }

        return answerId;
    }
);
export default answerSlice.reducer;
