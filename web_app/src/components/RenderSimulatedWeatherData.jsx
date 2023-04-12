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

export default RenderSimulatedWeatherData;