import React from 'react';

import reducer from './work';
import * as actionTypes from '../actions/actionTypes';

const stubWork = { id: 1 };
const stubMainWorks = [
  { title: 'Test Works', works: JSON.stringify([stubWork]) },
  { title: 'Test Works', works: JSON.stringify([stubWork]) },
];

describe('Work Reducer', () => {
  it('should return default state', () => {
    const newState = reducer(undefined, {}); // initialize
    expect(newState).toEqual({
      mainWorkLists: [{ title: '', works: [] }, { title: '', works: [] }],
      selectedWorks: [],
      searchedWorks: [[], []],
      selectedWork: null,
      noSuchSelectedWork: false,
      recommWorks: [{ title: '', works: [] }, { title: '', works: [] }],
      works: [],
    });
  });

  it('should return main works', () => {
    const stubInitialState = {
      mainWorkLists: [{ title: '', works: [] }, { title: '', works: [] }],
    };
    const stubNewMainWorks = [
      { title: 'Test Works', works: [stubWork] },
      { title: 'Test Works', works: [stubWork] },
    ];
    const newState = reducer(stubInitialState, { type: actionTypes.GET_MAIN_WORKS, mainWorkLists: stubMainWorks, listStart: [true, true] });
    expect(newState.mainWorkLists).toEqual(stubNewMainWorks);
  });

  it('should return concatenated main works', () => {
    const stubInitialState = {
      mainWorkLists: [{ title: 'Test Works', works: [stubWork] }, { title: 'Test Works', works: [stubWork] }],
    };
    const stubNewMainWorks = [
      { title: 'Test Works', works: [stubWork, stubWork] },
      { title: 'Test Works', works: [stubWork] },
    ];
    const newState = reducer(stubInitialState, { type: actionTypes.GET_MAIN_WORKS, mainWorkLists: stubMainWorks, listStart: [false, true] });
    expect(newState.mainWorkLists).toEqual(stubNewMainWorks);
  });

  it('should get work', () => {
    const stubInitialState = {
      selectedWork: null,
      noSuchSelectedWork: false,
    };
    const newState = reducer(stubInitialState, {
      type: actionTypes.GET_WORK,
      selectedWork: stubWork,
    });
    expect(newState).toEqual({
      selectedWork: stubWork,
      noSuchSelectedWork: false,
    });
  });

  it('should notify if there is no such work', () => {
    const stubInitialState = {
      noSuchSelectedWork: false,
    };
    const newState = reducer(stubInitialState, {
      type: actionTypes.WORK_NOT_EXISTING,
    });
    expect(newState).toEqual({
      selectedWork: null,
      noSuchSelectedWork: true,
    });
  });

  it('should get recommended works', () => {
    const stubInitialState = {
      recommWorks: [{ title: '', works: [] }, { title: '', works: [] }],
    };
    const stubRecWorks = [
      { title: 'Test Works', works: [stubWork] },
      { title: 'Test Works', works: [stubWork] },
    ];
    const newState = reducer(stubInitialState, { type: actionTypes.GET_REC_WORKS, selectedWorks: stubRecWorks, listStart: [true, true] });
    expect(newState.recommWorks).toEqual(stubRecWorks);
  });

  it('should return concatenated recommended works', () => {
    const stubInitialState = {
      recommWorks: [{ title: '', works: [stubWork] }, { title: '', works: [stubWork] }],
    };
    const stubRecWorks = [
      { title: 'Test Works', works: [stubWork, stubWork] },
      { title: 'Test Works', works: [stubWork] },
    ];
    const newState = reducer(stubInitialState, { type: actionTypes.GET_REC_WORKS, selectedWorks: stubRecWorks, listStart: [false, true] });
    const stubNewRecWorks = [
      { title: 'Test Works', works: [stubWork, stubWork, stubWork] },
      { title: 'Test Works', works: [stubWork] },
    ];
    expect(newState.recommWorks).toEqual(stubNewRecWorks);
  });

  it('should get searched works', () => {
    const stubInitialState = {
      searchedWorks: [[], []],
    };
    const newState = reducer(stubInitialState, {
      type: actionTypes.GET_SEARCH_WORKS,
      listStart: [true, true],
      selectedWorks: [[stubWork], [stubWork, stubWork]],
    });
    expect(newState).toEqual({
      searchedWorks: [[stubWork], [stubWork, stubWork]],
    });
  });

  it('should return concatenated searched works', () => {
    const stubInitialState = {
      searchedWorks: [[stubWork], [stubWork]],
    };
    const newState = reducer(stubInitialState, {
      type: actionTypes.GET_SEARCH_WORKS,
      listStart: [false, true],
      selectedWorks: [[stubWork], [stubWork, stubWork]],
    });
    expect(newState).toEqual({
      searchedWorks: [[stubWork, stubWork], [stubWork, stubWork]],
    });
  });
});
