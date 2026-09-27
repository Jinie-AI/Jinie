import React from 'react';
import config from './src/config.json';
import AppView from './src/components/AppView';
import {loadState,saveState} from './src/storage';
export default function App(){return <AppView config={config} loadState={loadState} saveState={saveState}/>;}
