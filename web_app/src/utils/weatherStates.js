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
        //'Lights in Smoke Boxes': 'Changes to red if in use, green if avaliable.',
        'Pavillion Indoor Lights': 'Switch off entirely',
        'Motorized shading of tree': 'Remains retracted'
        //'LED lighting of large tree': 'Remains off'
      },
      'id': 0,
      'scenario': 's1',
      'weather': 'Sunny',
      'background_image': s1_background,
      'icon_class': 'bi bi-sun', // icon class for Sunny weather
      'description': 'Clear skies and pleasant morning',
      'effect': 'The Cocoon does not interfere much'
    },
    {
      'data_to_render': {
        'Heat Index': 'Uncomfortable (too hot, too humid)',
        'Luminosity': 'High',
        'LED Filaments for Trees': 'Switches off entirely',
        'Exterior Pavillion Lights': 'Switches off entirely',
        //'Lights in Smoke Boxes': 'Changes to red if in use, green if avaliable.',
        'Pavillion Indoor Lights': 'Switch off entirely',
        'Motorized shading of tree': 'Remains retracted'
        //'LED lighting of large tree': 'Remains off'
      },
      'id': 1,
      'scenario': 's3',
      'weather': 'Extremely Sunny',
      'background_image': s2_background,
      'icon_class': 'bi bi-sun', // icon class for Sunny weather
      'description': 'Scorching hot afternoon',
      'effect': 'The Cocoon creates a cooling atmosphere.'
    },
    {
      'data_to_render': {
        'Heat Index': 'Uncomfortable (too humid)',
        'Luminosity': 'Low (due to clouds)',
        'LED Filaments for Trees': 'Switches on',
        'Exterior Pavillion Lights': 'Switches on',
        //'Lights in Smoke Boxes': 'Changes to red if in use, green if avaliable.',
        'Pavillion Indoor Lights': 'Switches on and shows a yellow aura',
        'Motorized shading of tree': 'Extends to full extent'
        //'LED lighting of large tree': 'Turns on'
      },
      'id': 2,
      'scenario': 's2',
      'weather': 'Rainy',
      'background_image': s3_background,
      'icon_class': 'bi bi-cloud-rain', // icon class for Rainy weather
      'description': 'Stormy Afternoon',
      'effect': 'The Cocoon creates a homey and warm atmosphere.'
    },
    {
      'data_to_render': {
        'Heat Index': 'Comfortable',
        'Luminosity': 'Low (at night)',
        'LED Filaments for Trees': 'Switches on',
        'Exterior Pavillion Lights': 'Switches on',
        //'Lights in Smoke Boxes': 'Changes to red if in use, green if avaliable.',
        'Pavillion Indoor Lights': 'Switches on and shows a light blue (inspired by bioluminescent caves)',
        'Motorized shading of tree': 'Remains retracted'
        //'LED lighting of large tree': 'Remains retracted'
      },
      'id': 3,
      'scenario': 's4',
      'weather': 'Clear Night',
      'background_image': s4_background,
      'icon_class': 'bi bi-moon', // icon class for Clear weather
      'description': 'Starry clear night',
      'effect': 'Like bioluminescent caves the pavillion sparkels when people walk past.'
    }
  ];