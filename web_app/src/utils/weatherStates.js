import s1_background from '../assets/images/s1.jpg'
import s2_background from '../assets/images/s2.jpg'
import s3_background from '../assets/images/s3.jpg'
import s4_background from '../assets/images/s4.jpg'

export const weatherStates = [
    {
      'data_to_render': {
        'Heat Index': 'Comfortable',
        'Luminosity': 'Moderate',
        'LED Filaments for Trees': 'Switches off entirely',
        'Exterior Pavillion Lights': 'Switches off entirely',
        'Lights in Smoke Boxes': 'Will cycle randomly',
        'Pavillion Indoor Lights': 'Switch off entirely',
        'Motorized shading of tree': 'Remains retracted',
        'LED lighting of large tree': 'Remains off'
      },
      'weather': 'Sunny',
      'background_image': s1_background,
      'icon_class': 'bi bi-sun' // icon class for Sunny weather
    },
    {
      'data_to_render': {
        'Heat Index': 'Uncomfortable (too hot, too humid)',
        'Luminosity': 'High',
        'LED Filaments for Trees': 'Switches off entirely',
        'Exterior Pavillion Lights': 'Switches off entirely',
        'Lights in Smoke Boxes': 'Will cycle randomly',
        'Pavillion Indoor Lights': 'Switch off entirely',
        'Motorized shading of tree': 'Remains retracted',
        'LED lighting of large tree': 'Remains off'
      },
      'weather': 'Extremely Sunny',
      'background_image': s2_background,
      'icon_class': 'bi bi-sun' // icon class for Sunny weather
    },
    {
      'data_to_render': {
        'Heat Index': 'Uncomfortable (too humid)',
        'Luminosity': 'Low (due to clouds)',
        'LED Filaments for Trees': 'Switches on',
        'Exterior Pavillion Lights': 'Switches on',
        'Lights in Smoke Boxes': 'Will cycle randomly',
        'Pavillion Indoor Lights': 'Switches on and shows a yellow aura',
        'Motorized shading of tree': 'Extends to full extent',
        'LED lighting of large tree': 'Turns on'
      },
      'weather': 'Rainy',
      'background_image': s3_background,
      'icon_class': 'bi bi-cloud-rain' // icon class for Rainy weather
    },
    {
      'data_to_render': {
        'Heat Index': 'Comfortable',
        'Luminosity': 'Low (at night)',
        'LED Filaments for Trees': 'Switches on',
        'Exterior Pavillion Lights': 'Switches on',
        'Lights in Smoke Boxes': 'Will cycle randomly',
        'Pavillion Indoor Lights': 'Switches on and shows a light blue (inspired by bioluminescent caves)',
        'Motorized shading of tree': 'Remains retracted',
        'LED lighting of large tree': 'Remains retracted'
      },
      'weather': 'Clear',
      'background_image': s4_background,
      'icon_class': 'bi bi-moon' // icon class for Clear weather
    }
  ];