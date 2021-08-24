import './App.css';
import SearchInput from './components/searchInput.js';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div>
        <Switch>
          <Route path='/' exact component={SearchInput}/>
          <Route path='/search=:CUI' component={SearchInput}/>
        </Switch>
      </div>
    </Router>
  );
}

export default App;

