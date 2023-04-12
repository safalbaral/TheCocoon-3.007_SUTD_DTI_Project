import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css';

import sunny_background from "./assets/images/sunny_weather.jpg";
import rainy_background from "./assets/images/rainy_weather.jpg";

import axios from 'axios';
import { useState, useEffect } from 'react'
import './App.css';

import mqttClient from './utils/mqttConnection.js';

const weatherStates = [
  {
    name: 'Sunny Weather',
    icon_class: 'bi bi-sun',
    pavillion_lights: 'Minimally Lit',
    shades: 'Partially Deployed',
    lighting_mood: 'Natural lighting, minimal artifical mood lighting',
    background_gradient: "linear-gradient(315deg, #bdd4e7 0%, #8693ab 74%);",
    background_color: 'orange',
    background_image: sunny_background
  },
  {
    name: 'Rainy Weather',
    icon_class: 'bi bi-cloud-drizzle',
    pavillion_lights: 'All lights Lit',
    shades: 'Fully Deployed',
    lighting_mood: 'Warm lighting through LED lights',
    background_gradient: "linear-gradient(315deg, #bdd4e7 0%, #8693ab 74%);",
    background_color: 'blue',
    background_image: rainy_background
  }
]


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
      }); // Replace with your topic
      //mqttClient.off("message", handleMqttMessage);
      //mqttClient.end();
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
            <RenderSensors sensorsData={sensorsData}/>
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
      console.log('Clicked')
  }

  return (
    <div class='main-card container d-flex'>
      <div class="container">
        <div class="card shadow-lg">
          <div class="card-body">
            <div className="d-flex flex-row align-items-center">
              <i class={weatherStates[weatherIndex].icon_class}></i>
              <h2 class="card-title"> {weatherStates[weatherIndex].name} </h2>
            </div>
            <div class="row">
              <div class="col-md-6">
                <div>
                  <h3>Pavillion Lights</h3>
                  <p><strong>{weatherStates[weatherIndex].pavillion_lights}</strong></p>
                </div>
                <div>
                  <h3>Shades</h3>
                  <p><strong>{weatherStates[weatherIndex].shades}</strong></p>
                </div>
              </div>
              <div class="col-md-6">
                <h3>Lighting Mood</h3>
                <p><strong>{weatherStates[weatherIndex].lighting_mood}</strong></p>
              </div>
            </div>
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
