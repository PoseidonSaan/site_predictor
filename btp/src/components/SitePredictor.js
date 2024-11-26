import React, { useState } from "react";
import axios from "axios";  // Import axios for API requests
import "./SitePredictor.css";

const SitePredictor = () => {
  const [xCoordinate, setXCoordinate] = useState("");
  const [yCoordinate, setYCoordinate] = useState("");
  const [requiredCapacity, setRequiredCapacity] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");  // State to hold error messages
  const [loading, setLoading] = useState(false);  // State for loading indicator

  // Handle the prediction when button is clicked
  const handlePredict = async () => {
    if (xCoordinate && yCoordinate && requiredCapacity) {
      setLoading(true);  // Set loading to true when request starts
      setError("");  // Clear previous errors

      try {
        // Send POST request to the Flask backend with the input data
        const response = await axios.post("http://13.232.89.166:5000/predict", {
          factory_x: xCoordinate,
          factory_y: yCoordinate,
          required_capacity: requiredCapacity,
        });

        if (response.data.sites) {
          setResults(response.data.sites);  // Set the results if the response is valid
        } else {
          setError(response.data.error || "Unknown error occurred.");
        }
      } catch (err) {
        setError("Failed to connect to server. Please check the backend.");
      } finally {
        setLoading(false);  // Set loading to false after the request is complete
      }
    } else {
      setError("Please enter all fields.");
    }
  };

  return (
    <div className="site-predictor">
      <h1>What Site?</h1>
      <p className="subtitle">Find the best sites based on your coordinates.</p>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="x-coordinate">X Coordinate:</label>
        <input
          type="number"
          id="x-coordinate"
          value={xCoordinate}
          onChange={(e) => setXCoordinate(e.target.value)}
          placeholder="Enter X coordinate"
          required
        />
        <label htmlFor="y-coordinate">Y Coordinate:</label>
        <input
          type="number"
          id="y-coordinate"
          value={yCoordinate}
          onChange={(e) => setYCoordinate(e.target.value)}
          placeholder="Enter Y coordinate"
          required
        />
        <label htmlFor="required-capacity">Required Storage Capacity:</label>
        <input
          type="number"
          id="required-capacity"
          value={requiredCapacity}
          onChange={(e) => setRequiredCapacity(e.target.value)}
          placeholder="Enter required capacity"
          required
        />
        <button type="button" onClick={handlePredict}>
          Which Site?
        </button>
      </form>

      {loading && <p>Loading...</p>}  {/* Display loading message */}
      
      {error && <p className="error">{error}</p>}  {/* Display error message if any */}

      {results.length > 0 && (
        <div className="results">
          <h2>Top 5 Sites</h2>
          <ul className="site-results">
            {results.map((result, index) => (
              <li key={index} className="result-item">
                <div className="result-rank">{index + 1}</div>
                <div className="result-details">
                  <span className="site-name">{result.STORAGE_UNIT_NAME}</span>
                  <span className="site-score">Score: {result.Cluster_Score}</span>
                  <span className="site-capacity">Capacity: {result.Capacity}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SitePredictor;
