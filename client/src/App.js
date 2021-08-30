import './App.css';
import SearchInput from './components/searchInput.js';
import PageNotFound from './components/pageNotFound';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div>
        <Switch>
          <Route path='/' exact component={SearchInput}/>
          <Route path='/search=:term' component={SearchInput}/>
          <Route component={PageNotFound}/>
        </Switch>
      </div>
    </Router>
  );
}

export default App;

