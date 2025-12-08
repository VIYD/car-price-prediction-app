import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

function App() {
  const [metadata, setMetadata] = useState({
    brands: [],
    models: [],
    brand_models: {},
    model_engines: {},
    model_transmissions: {},
    model_fuel_types: {},
    fuel_types: [],
    engines: [],
    transmissions: [],
    accidents: []
  })
  
  const [formData, setFormData] = useState({
    brand: '',
    model: '',
    model_year: 2020,
    milage: 50000,
    fuel_type: '',
    engine: '-',
    transmission: '-',
    accident: ''
  })
  
  const [price, setPrice] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Fetch metadata for dropdowns
    axios.get('http://localhost:8000/metadata')
      .then(res => {
        setMetadata(res.data)
        // Set defaults
        const firstBrand = res.data.brands[0] || ''
        const firstBrandModels = res.data.brand_models?.[firstBrand] || []
        const firstModel = firstBrandModels[0] || ''
        const modelEngines = res.data.model_engines?.[firstModel] || []
        const modelTransmissions = res.data.model_transmissions?.[firstModel] || []
        const modelFuelTypes = res.data.model_fuel_types?.[firstModel] || []
        
        setFormData(prev => ({
          ...prev,
          brand: firstBrand,
          model: firstModel,
          fuel_type: modelFuelTypes[0] || '',
          engine: modelEngines[0] || '-',
          transmission: modelTransmissions[0] || '-',
          accident: res.data.accidents[0] || ''
        }))
      })
      .catch(err => console.error("Failed to fetch metadata", err))
  }, [])

  const handleChange = (e) => {
    const { name, value } = e.target
    
    // If brand changes, update model, engine, transmission, and fuel_type
    if (name === 'brand') {
      const brandModels = metadata.brand_models?.[value] || []
      const firstModel = brandModels[0] || ''
      const modelEngines = metadata.model_engines?.[firstModel] || []
      const modelTransmissions = metadata.model_transmissions?.[firstModel] || []
      const modelFuelTypes = metadata.model_fuel_types?.[firstModel] || []
      
      setFormData({
        ...formData,
        brand: value,
        model: firstModel,
        fuel_type: modelFuelTypes[0] || '',
        engine: modelEngines[0] || '-',
        transmission: modelTransmissions[0] || '-'
      })
    } 
    // If model changes, update engine, transmission, and fuel_type
    else if (name === 'model') {
      const modelEngines = metadata.model_engines?.[value] || []
      const modelTransmissions = metadata.model_transmissions?.[value] || []
      const modelFuelTypes = metadata.model_fuel_types?.[value] || []
      
      setFormData({
        ...formData,
        model: value,
        fuel_type: modelFuelTypes[0] || '',
        engine: modelEngines[0] || '-',
        transmission: modelTransmissions[0] || '-'
      })
    }
    else {
      setFormData({
        ...formData,
        [name]: value
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPrice(null)
    
    try {
      const response = await axios.post('http://localhost:8000/predict', formData)
      setPrice(response.data.price)
    } catch (err) {
      setError("Failed to get prediction")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="glass-card">
        <h1>Car Price Predictor</h1>
        
        <form onSubmit={handleSubmit} className="form-grid">
          
          <div className="form-group">
            <label>Brand</label>
            <select name="brand" value={formData.brand} onChange={handleChange}>
              {metadata.brands.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Model</label>
            <select name="model" value={formData.model} onChange={handleChange}>
              {(metadata.brand_models?.[formData.brand] || []).map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Year</label>
            <input 
              type="number" 
              name="model_year" 
              value={formData.model_year} 
              onChange={handleChange} 
              min="1990" max="2025" 
            />
          </div>

          <div className="form-group">
            <label>Mileage (miles)</label>
            <input 
              type="number" 
              name="milage" 
              value={formData.milage} 
              onChange={handleChange} 
            />
          </div>

          <div className="form-group">
            <label>Fuel Type</label>
            <select name="fuel_type" value={formData.fuel_type} onChange={handleChange}>
              {(metadata.model_fuel_types?.[formData.model] || []).map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Engine</label>
            <select name="engine" value={formData.engine} onChange={handleChange}>
              {(metadata.model_engines?.[formData.model] || []).map(e => <option key={e} value={e}>{e}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Transmission</label>
            <select name="transmission" value={formData.transmission} onChange={handleChange}>
              {(metadata.model_transmissions?.[formData.model] || []).map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Accident History</label>
            <select name="accident" value={formData.accident} onChange={handleChange}>
              {metadata.accidents.map(a => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>

          <div className="full-width">
            <button type="submit" disabled={loading}>
              {loading ? "Calculating..." : "Estimate Price"}
            </button>
          </div>
        </form>

        {price !== null && (
          <div className="result-card">
            <h2>Estimated Price</h2>
            <div className="price-tag">${price.toLocaleString(undefined, {maximumFractionDigits: 0})}</div>
          </div>
        )}
        
        {error && <div className="error">{error}</div>}
      </div>
    </div>
  )
}

export default App
