import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h2>IYPM CRA</h2>
        </div>
        <p className="App-intro">
          This is an IYPM CRA test page for checking CI/CD deployment.
        </p>
      </div>
    );
  }
}

export default App;
