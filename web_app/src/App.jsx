import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css';

import axios from 'axios';
import { useState, useEffect } from 'react'
import './App.css';

import mqttClient from './utils/mqttConnection.js';
import { weatherStates } from './utils/weatherStates';
import RenderSimulatedWeatherData from './components/RenderSimulatedWeatherData'

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
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);
  const [selectedOption, setSelectedOption] = useState('');

  const initializeBackground = () => {
      document.body.style.backgroundImage = `url(${weatherStates[weatherIndex].background_image})`;
  }
  
  initializeBackground()

  const handleOptionChange = (event) => {
    setSelectedOption(event.target.value); // Update selected option in state
  }

  const handleClick = () => {
    if (!isButtonDisabled) {
      setIsButtonDisabled(true); // Disable the button

      const nextWeatherIndex = selectedOption;

      setWeatherIndex(nextWeatherIndex);

      document.body.style.backgroundImage = `url(${weatherStates[nextWeatherIndex].background_image})`;

      mqttClient.publish('neelonoon/feeds/project.scenario', `${weatherStates[weatherIndex].scenario}`, () => {
        console.log('Published scenario information to mqtt server.')
      })

      setTimeout(() => {
        setIsButtonDisabled(false); // Enable the button after 5 seconds
      }, 5000);
    }
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
              <select className="form-select" onChange={handleOptionChange}>
                  <option value={selectedOption}>Select a weather condition</option>
                  { weatherStates.map((weatherState) => {
                    return(
                      <option value={weatherState.id} disabled={Number(selectedOption) === Number(weatherState.id) ? true : false}>{weatherState.weather}</option>
                    )
                  }) }
                </select>
            </div>
            <div class="col-md-12 text-center mt-2">
              <button class="btn btn-primary" onClick={handleClick} disabled={isButtonDisabled}>Simulate Weather</button>
            </div>
          <div class="col-md-12 text-center mt-2">
            <button class="btn btn-secondary" onClick={changeActiveScreen} disabled={isButtonDisabled}>Access Sensor Panel</button>
          </div>
            </div>
            </div>
          </div>
        </div>
      </div>
  )
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
