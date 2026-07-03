import StatusBadge from './components/StatusBadge';
import LiveGauges from './components/LiveGauges';
import DtcList from './components/DtcList';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">OBD-II Teşhis Paneli</h1>
        <StatusBadge />
      </header>

      <main className="app-main">
        <LiveGauges />
        <DtcList />
      </main>
    </div>
  );
}
