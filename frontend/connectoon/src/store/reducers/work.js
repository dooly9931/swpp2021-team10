import * as actionTypes from '../actions/actionTypes';

const initialState = {
  works: [
  ],
  mainWorkLists: [
    { title: '', works: [] }, { title: '', works: [] },
  ],
  selectedWorks: [
  ],
  searchedWorks: [
    [], [],
  ],
  selectedWork: null,
  noSuchSelectedWork: false,
  recommWorks: [
    { title: '', works: [] }, { title: '', works: [] },
  ],
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.GET_MAIN_WORKS:
      const newMainWorkLists = state.mainWorkLists.map((listDict, idx) => {
        if (action.listStart[idx]) {
          return { title: action.mainWorkLists[idx].title, works: JSON.parse(action.mainWorkLists[idx].works) };
        } else {
          return { title: action.mainWorkLists[idx].title, works: listDict.works.concat(JSON.parse(action.mainWorkLists[idx].works)) };
        }
      });
      return { ...state, mainWorkLists: newMainWorkLists };
    case actionTypes.GET_WORK:
      return { ...state, selectedWork: action.selectedWork, noSuchSelectedWork: false };
    case actionTypes.WORK_NOT_EXISTING:
      return { ...state, selectedWork: null, noSuchSelectedWork: true };
    case actionTypes.GET_REC_WORKS:
      const newRecommWorks = state.recommWorks.map((listDict, idx) => {
        if (action.listStart[idx]) {
          return { title: action.selectedWorks[idx].title, works: action.selectedWorks[idx].works };
        } else {
          return { title: action.selectedWorks[idx].title, works: listDict.works.concat(action.selectedWorks[idx].works) };
        }
      });
      return { ...state, recommWorks: newRecommWorks };
    case actionTypes.GET_SEARCH_WORKS:
      const newSearchedWorks = state.searchedWorks.map((listDict, idx) => {
        if (action.listStart[idx]) {
          return action.selectedWorks[idx];
        } else {
          return listDict.concat(action.selectedWorks[idx]);
        }
      });
      return { ...state, searchedWorks: newSearchedWorks };
    default:
      break;
  }
  return state;
};

export default reducer;
