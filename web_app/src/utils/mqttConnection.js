// mqttConnection.js

import mqtt from 'mqtt';

const client = mqtt.connect('ws://io.adafruit.com', {
  username: import.meta.env.VITE_AIO_USERNAME, 
  password: import.meta.env.VITE_AIO_KEY,
});

client.on('connect', () => {
  console.log('Connected');
});

// Add other event listeners or functions as needed

export default client;