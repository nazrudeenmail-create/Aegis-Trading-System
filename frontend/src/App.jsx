import React, { useState } from 'react';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardOverview } from './views/DashboardOverview';
import { InstrumentsView } from './views/InstrumentsView';
import { MarketAnalysisView } from './views/MarketAnalysisView';
import { PipelineMonitor } from './views/PipelineMonitor';
import { StrategiesView } from './views/StrategiesView';
import { PortfolioView } from './views/PortfolioView';
import { RiskView } from './views/RiskView';
import { OrdersView } from './views/OrdersView';
import { JournalView } from './views/JournalView';
import { ConnectionsView } from './views/ConnectionsView';
import { SettingsView } from './views/SettingsView';
import { SystemView } from './views/SystemView';
import { SystemConsole } from './components/SystemConsole';

function App() {
  const [currentView, setCurrentView] = useState('overview');

  const renderView = () => {
    switch (currentView) {
      case 'overview': return <DashboardOverview />;
      case 'pipeline': return <PipelineMonitor />;
      case 'market': return <MarketAnalysisView />;
      case 'portfolio': return <PortfolioView />;
      case 'positions': return <PortfolioView />;
      case 'instruments': return <InstrumentsView />;
      case 'strategies': return <StrategiesView />;
      case 'risk': return <RiskView />;
      case 'orders': return <OrdersView />;
      case 'journal': return <JournalView />;
      case 'connections': return <ConnectionsView />;
      case 'settings': return <SettingsView />;
      case 'system': return <SystemView />;
      default: return <DashboardOverview />;
    }
  };

  return (
    <>
      <DashboardLayout currentView={currentView} setCurrentView={setCurrentView}>
        {renderView()}
      </DashboardLayout>
      <SystemConsole />
    </>
  );
}

export default App;