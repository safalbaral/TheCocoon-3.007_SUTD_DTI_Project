import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css';

import axios from 'axios';
import { useState, useEffect } from 'react'
import './App.css';

import mqttClient from './utils/mqttConnection.js';
import { weatherStates } from './utils/weatherStates';

const SensorsScreen = ({changeActiveScreen}) => {
  const [sensorsData, setSensorsData] = useState({
    'data': '123',
    'other data': '456'
  });

  useEffect(() => {
    // Subscribe to the desired MQTT topic
    mqttClient.subscribe("neelonoon/feeds/project.scenario", () => {
      'SUBSCRIBED'
    }); // Replace with your topic

    // Define a callback to handle incoming MQTT messages
    const handleMqttMessage = (topic, payload) => {
      // Update the state with the received message
      console.log('HHHHHHHHH')
      console.log(JSON.parse(payload.toString())) 
      setSensorsData(JSON.parse(payload.toString()));
    };

    // Attach the callback to the MQTT client
    mqttClient.on("message", handleMqttMessage);

    // Clean up the MQTT client and event listener when the component unmounts
    return () => {
      mqttClient.unsubscribe("neelonoon/feeds/project.scenario", () => {
        'UNSUBSCRIBED'
      }); 
    };
  }, []); // Empty array as the dependency list to run the effect only once

  return(
    <div class='main-card container d-flex justify-content-center'>
      <div class="container mt-5">
        <div class="card shadow-lg">
          <div class="card-body">
            <div className="d-flex flex-row align-items-center">
              <i class="bi bi-cpu"></i>
              <h2 class="card-title"> Realtime Sensor Data </h2>
            </div>
            <div className="row mt-4">
              <RenderSensors sensorsData={sensorsData}/>
            </div>
            <div class="row mt-4">
              <div class="col-md-12 text-center">
                <button class="btn btn-secondary" onClick={changeActiveScreen}>Access Weather Panel</button>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>
  )
}

const RenderSensors = ({sensorsData}) => {
  console.log(sensorsData)
  return (
    <div>
      {Object.entries(sensorsData).map(([data, value]) => ( 
        <div className="col-md-6" key={data}>
          <div>
            <h3>{data}</h3>
            <p><strong>{value}</strong></p>
          </div>
        </div>
      ))}
    </div>
  );
}

const MainScreen = ({changeActiveScreen}) => {
  const [weatherIndex, setWeatherIndex] = useState(0)

  const initializeBackground = () => {
      document.body.style.backgroundImage = `url(${weatherStates[weatherIndex].background_image})`;
  }
  
  initializeBackground()

  const handleClick = () => {
      const nextWeatherIndex = (weatherIndex + 1) % weatherStates.length;
      setWeatherIndex(nextWeatherIndex);
      document.body.style.backgroundImage = `url(${weatherStates[nextWeatherIndex].background_image})`;
      //document.body.style.backgroundColor = weatherStates[nextWeatherIndex].background_color;
      document.querySelector('.main-card').style.backgroundImage = weatherStates[nextWeatherIndex].background_gradient;
  }

  return (
    <div class='main-card container d-flex'>
      <div class="container">
        <div class="card shadow-lg">
          <div class="card-body">
            <div className="d-flex flex-row align-items-center">
              <i class={weatherStates[weatherIndex].icon_class}></i>
              <h2 class="card-title"> {weatherStates[weatherIndex].weather} </h2>
            </div>
            <RenderSimulatedWeatherData weatherState={weatherStates[weatherIndex]} />
            <div class="row mt-4">
              <div class="col-md-12 text-center">
                <button class="btn btn-primary" onClick={handleClick}>Change Weather</button>
              </div>
              <div class="col-md-12 text-center mt-2">
                <button class="btn btn-secondary" onClick={changeActiveScreen}>Access Sensor Panel</button>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>
  )
}

const RenderSimulatedWeatherData = ({weatherState}) => {
  return (
    <div className='row'>
      {Object.entries(weatherState.data_to_render).map(([data, value], index) =>  {
        const backgroundColor = '#f8f8f8' 
        return (
          <div className='col-md-6' key={data} style={{border: '1px solid #ddd', borderRadius: '4px', padding: '10px', marginBottom: '1px', backgroundColor}}>
            <h3 style={{fontSize: '18px', fontWeight: 'bold', marginBottom: '5px'}}>{data}</h3>
            <p style={{fontSize: '14px', color: '#444'}}><strong>{value}</strong></p>
          </div>
        )
      })}
    </div>
  );
}

function App() {
  const [activeScreen, setActiveScreen] = useState('weather');

  console.log(`ACTIVE SCREEN! ${activeScreen}`)  

  const changeActiveScreen = () => {
    setActiveScreen('weather')
  }

  const changeActiveScreen1 = () => {
    setActiveScreen('sensor')
  }

  if(activeScreen === 'weather') {
    console.log('Rendering main screen')
    return(<MainScreen changeActiveScreen={changeActiveScreen1}/>)
  } else if (activeScreen === 'sensor') {
    console.log('Rendering other screen')
    return(<SensorsScreen changeActiveScreen={changeActiveScreen}/>)
  }
}

export default App;
