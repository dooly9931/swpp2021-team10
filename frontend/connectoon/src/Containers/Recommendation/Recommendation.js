import React, { Component } from 'react';
import PropTypes, { func } from 'prop-types';

import { connect } from 'react-redux';
import { withRouter } from 'react-router';

import * as actionCreators from '../../store/actions/index';
import WorkList from '../../Components/WorkList/WorkList';
import { stateConstructor, stateUpdator } from '../WorkPaginationTools/tools';

import './Recommendation.css';

class Recommendation extends Component {
  constructor(props) {
    super(props);
    const { location, onGetRecWorks } = this.props;
    this.state = stateConstructor(location);
    const { requestWorks } = this.state;
    onGetRecWorks(requestWorks);
  }

  onClickWork = (workId) => {
    this.props.history.push('/works/' + String(workId));
  }

  onClickMore = (listId) => {
    const { subjectRows, newRequestWorks, fetchMore } = stateUpdator(listId, this.state);
    this.setState({ subjectRows, requestWorks: newRequestWorks });
    if (fetchMore) {
      this.props.onGetRecWorks(newRequestWorks);
    }
    const { history } = this.props;
    history.replace('/recommendation', { subjectRows });
  }

  render() {
    if (!this.props.loggedInUser) {
      return <div className="recommendation-page">
        <h3>Please Login!</h3>
      </div>;
    }
    const { recWorkLists } = this.props;
    const { subjectRows, worksInRow } = this.state;
    const genreList = <WorkList
      className="genre-based-work-list"
      subject={recWorkLists[0].title}
      workList={recWorkLists[0].works}
      rows={subjectRows[0]}
      worksInRow={worksInRow}
      onClickWork={(workId) => this.onClickWork(workId)}
      onClickMore={() => this.onClickMore(0)}
    />;
    const reviewList = <WorkList
      className="review-based-work-list"
      subject={recWorkLists[1].title}
      workList={recWorkLists[1].works}
      rows={subjectRows[1]}
      worksInRow={worksInRow}
      onClickWork={(workId) => this.onClickWork(workId)}
      onClickMore={() => this.onClickMore(1)}
    />;

    return (
      <div className="recommendation-page">
        {genreList}
        {reviewList}
      </div>
    );
  }
}

Recommendation.defaultProps = {
  onGetRecWorks: func,
  recWorkLists: PropTypes.arrayOf(PropTypes.any),
};

Recommendation.propTypes = {
  onGetRecWorks: func,
  recWorkLists: PropTypes.arrayOf(PropTypes.any),
};

const mapStateToProps = (state) => {
  return {
    loggedInUser: state.user.loggedInUser,
    recWorkLists: state.work.recommWorks,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onGetRecWorks: (requestWorks) => dispatch(actionCreators.getRecWorks(requestWorks)),
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(withRouter(Recommendation));
